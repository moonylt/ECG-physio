# -*- coding: utf-8 -*-
"""
协议解析器 v2
解析 MCU/ESP32 发送的 PHYSIO v2 数据帧（含 ECG、血氧、血压、温度等 accessory）
协议规范见 3.FIRMWARE/PROTOCOL.md
"""

import time
from dataclasses import dataclass
from typing import List, Optional
import numpy as np

from utils.crc8 import crc8


# ---------------------------------------------------------------------------
# 帧常量
# ---------------------------------------------------------------------------
STX0 = 0x55
STX1 = 0xAA
HEADER_LEN = 8          # STX0..MSGID
CRC_LEN = 1

# 地址
ADDR_PC = 0x00
ADDR_ESP32 = 0x01
ADDR_STM32 = 0x02

# MSGID - 波形
MSG_ADS129X_DATA = 0x20     # ECG/呼吸, 4样本x4通道, 48B
MSG_SPO2_PPG = 0x21         # 血氧PPG, 4样本x2通道, 24B
MSG_SPO2_RESULT = 0x22      # 血氧结果, 8B
MSG_IBP_DATA = 0x23         # 有创血压波形, 4样本x2通道, 24B
MSG_NIBP_RESULT = 0x24      # 无创血压结果, 8B
MSG_TEMP_DATA = 0x25        # 温度遥测, 17B
MSG_LEADOFF_STATUS = 0x26   # 导联脱落, 2B

# MSGID - 状态与配置
MSG_DEVICE_STATUS = 0xF0    # accessory 在线通告, 4B
MSG_SET_GAIN = 0xA0
MSG_SET_TEMP_TARGET = 0xA1
MSG_ACQ_CTRL = 0xA2

# accessory 掩码位
ACC_ECG = 1 << 0
ACC_SPO2 = 1 << 1
ACC_TSKIN = 1 << 2          # 体表温度
ACC_TRECT = 1 << 3          # 肛温
ACC_IBP = 1 << 4
ACC_NIBP = 1 << 5
ACC_HEATER = 1 << 6

ACC_NAMES = {
    ACC_ECG: 'ECG/呼吸',
    ACC_SPO2: '血氧',
    ACC_TSKIN: '体表温度',
    ACC_TRECT: '肛温',
    ACC_IBP: '有创血压',
    ACC_NIBP: '无创血压',
    ACC_HEATER: '加热板',
}


# ---------------------------------------------------------------------------
# 帧对象
# ---------------------------------------------------------------------------
@dataclass
class BaseFrame:
    """所有帧的公共字段"""
    timestamp: float          # 时间戳 (秒)
    seq: int                  # 序列号
    src: int                  # 源地址
    dst: int                  # 目的地址


@dataclass
class ECGFrame(BaseFrame):
    """ECG/呼吸波形帧 (MSGID 0x20)"""
    samples: np.ndarray       # shape: (4, 4), dtype=int32, CH0=呼吸
    raw_payload: bytes = b''

    def __post_init__(self):
        if isinstance(self.samples, list):
            self.samples = np.array(self.samples, dtype=np.int32)
        self.samples = self.samples.astype(np.int32)


@dataclass
class SpO2Frame(BaseFrame):
    """血氧 PPG 波形帧 (MSGID 0x21)"""
    samples: np.ndarray       # shape: (4, 2), CH0=IR, CH1=RED
    raw_payload: bytes = b''


@dataclass
class SpO2ResultFrame(BaseFrame):
    """血氧计算结果帧 (MSGID 0x22)"""
    spo2: float               # % (值已除以10)
    pulse_rate: int           # bpm
    status: int               # bit0=探头在位
    raw_payload: bytes = b''


@dataclass
class IBPFrame(BaseFrame):
    """有创血压波形帧 (MSGID 0x23)"""
    samples: np.ndarray       # shape: (4, 2), CH0=P1, CH1=P2
    raw_payload: bytes = b''


@dataclass
class NIBPResultFrame(BaseFrame):
    """无创血压结果帧 (MSGID 0x24)"""
    systolic: float           # mmHg (值已除以10)
    diastolic: float
    mean: float
    status: int
    raw_payload: bytes = b''


@dataclass
class TempFrame(BaseFrame):
    """温度遥测帧 (MSGID 0x25)"""
    t_skin: float             # 体表温度 ℃
    t_rect: float             # 肛温 ℃
    t_heater: float           # 加热板温度 ℃
    t_spare: float            # 冷结/备用 ℃
    flags: int                # PHY_TEMP_FLAG_*
    raw_payload: bytes = b''


@dataclass
class LeadoffFrame(BaseFrame):
    """导联脱落状态帧 (MSGID 0x26)"""
    mask: int                 # bit=1 表示该通道脱落
    raw_payload: bytes = b''


@dataclass
class DeviceStatusFrame(BaseFrame):
    """accessory 在线通告帧 (MSGID 0xF0)"""
    accessories: int          # ACC_* 掩码
    fw_version: int           # BCD, 如 0x20 = v2.0
    error_code: int
    raw_payload: bytes = b''

    def accessory_list(self) -> List[str]:
        return [name for bit, name in ACC_NAMES.items()
                if self.accessories & bit]


@dataclass
class GenericFrame(BaseFrame):
    """未识别消息类型的通用帧"""
    msgid: int
    raw_payload: bytes = b''


# ---------------------------------------------------------------------------
# 解析器
# ---------------------------------------------------------------------------
class ProtocolParser:
    """
    协议解析器（长度自适应）

    帧格式: STX0(1B) + STX1(1B) + LEN_L(1B) + LEN_H(1B) + SRC(1B) + DST(1B)
            + SEQ(1B) + MSGID(1B) + DATA(N B) + CRC8(1B)
    """

    MAX_FRAME_LEN = 8 + 512 + 1   # 防御异常长度

    def __init__(self):
        self.buffer = bytearray()
        self.frame_count = 0      # 成功解析的帧数
        self.error_count = 0      # 错误计数
        self.sync_errors = 0      # 同步错误计数
        self.crc_errors = 0       # CRC 错误计数
        self.last_seq = -1        # 上一个序列号
        self.dropped_frames = 0   # 序列号跳变检测到的丢帧

        # 统计信息
        self.stats = {
            'total_bytes': 0,
            'valid_frames': 0,
        }

    def parse(self, raw_data: bytes) -> List[BaseFrame]:
        """
        解析原始数据，返回帧对象列表（类型见上方 dataclass）
        """
        self.buffer.extend(raw_data)
        self.stats['total_bytes'] += len(raw_data)

        frames = []

        while True:
            # 1. 同步
            if len(self.buffer) < 2:
                break
            if self.buffer[0] != STX0 or self.buffer[1] != STX1:
                self.buffer.pop(0)
                self.sync_errors += 1
                self.error_count += 1
                continue

            # 2. 取长度字段
            if len(self.buffer) < HEADER_LEN:
                break
            data_len = self.buffer[2] | (self.buffer[3] << 8)
            frame_len = HEADER_LEN + data_len + CRC_LEN
            if frame_len > self.MAX_FRAME_LEN:
                # 长度非法，当作同步错误丢弃帧头
                self.buffer.pop(0)
                self.sync_errors += 1
                self.error_count += 1
                continue

            # 3. 整帧是否到齐
            if len(self.buffer) < frame_len:
                break

            frame_data = bytes(self.buffer[:frame_len])

            # 4. CRC 校验
            if not self._verify_crc(frame_data):
                self.crc_errors += 1
                self.error_count += 1
                self.buffer.pop(0)
                continue

            # 5. 按消息类型解析
            try:
                frame = self._dispatch(frame_data)
                if frame is not None:
                    frames.append(frame)
                    self.frame_count += 1
                    self.stats['valid_frames'] += 1
                    self._check_seq(frame.seq)
            except Exception:
                self.error_count += 1

            self.buffer = self.buffer[frame_len:]

        return frames

    # ------------------------------------------------------------------
    def _dispatch(self, f: bytes) -> Optional[BaseFrame]:
        """根据 MSGID 构造对应帧对象"""
        ts = time.time()
        seq, src, dst, msgid = f[6], f[4], f[5], f[7]
        payload = f[HEADER_LEN:-CRC_LEN]

        if msgid == MSG_ADS129X_DATA:
            return ECGFrame(timestamp=ts, seq=seq, src=src, dst=dst,
                            samples=self._decode_samples(payload, 4, 4),
                            raw_payload=payload)
        if msgid == MSG_SPO2_PPG:
            return SpO2Frame(timestamp=ts, seq=seq, src=src, dst=dst,
                             samples=self._decode_samples(payload, 4, 2),
                             raw_payload=payload)
        if msgid == MSG_SPO2_RESULT:
            return SpO2ResultFrame(
                timestamp=ts, seq=seq, src=src, dst=dst,
                spo2=(payload[0] | (payload[1] << 8)) / 10.0,
                pulse_rate=payload[2] | (payload[3] << 8),
                status=payload[4],
                raw_payload=payload)
        if msgid == MSG_IBP_DATA:
            return IBPFrame(timestamp=ts, seq=seq, src=src, dst=dst,
                            samples=self._decode_samples(payload, 4, 2),
                            raw_payload=payload)
        if msgid == MSG_NIBP_RESULT:
            return NIBPResultFrame(
                timestamp=ts, seq=seq, src=src, dst=dst,
                systolic=(payload[0] | (payload[1] << 8)) / 10.0,
                diastolic=(payload[2] | (payload[3] << 8)) / 10.0,
                mean=(payload[4] | (payload[5] << 8)) / 10.0,
                status=payload[6],
                raw_payload=payload)
        if msgid == MSG_TEMP_DATA:
            return TempFrame(
                timestamp=ts, seq=seq, src=src, dst=dst,
                t_skin=self._decode_float(payload, 0),
                t_rect=self._decode_float(payload, 4),
                t_heater=self._decode_float(payload, 8),
                t_spare=self._decode_float(payload, 12),
                flags=payload[16],
                raw_payload=payload)
        if msgid == MSG_LEADOFF_STATUS:
            return LeadoffFrame(timestamp=ts, seq=seq, src=src, dst=dst,
                                mask=payload[0] | (payload[1] << 8),
                                raw_payload=payload)
        if msgid == MSG_DEVICE_STATUS:
            return DeviceStatusFrame(
                timestamp=ts, seq=seq, src=src, dst=dst,
                accessories=payload[0] | (payload[1] << 8),
                fw_version=payload[2],
                error_code=payload[3],
                raw_payload=payload)

        return GenericFrame(timestamp=ts, seq=seq, src=src, dst=dst,
                            msgid=msgid, raw_payload=payload)

    @staticmethod
    def _decode_samples(payload: bytes, n_samples: int, n_channels: int) -> np.ndarray:
        """解码 24bit 有符号大端样本矩阵 -> (n_samples, n_channels) int32"""
        samples = np.zeros((n_samples, n_channels), dtype=np.int32)
        idx = 0
        for s in range(n_samples):
            for ch in range(n_channels):
                v = (payload[idx] << 16) | (payload[idx + 1] << 8) | payload[idx + 2]
                if v >= 0x800000:
                    v -= 0x1000000
                samples[s, ch] = v
                idx += 3
        return samples

    @staticmethod
    def _decode_float(payload: bytes, offset: int) -> float:
        """小端 f32"""
        return float(np.frombuffer(payload[offset:offset + 4],
                                   dtype='<f4')[0])

    def _check_seq(self, seq: int):
        if self.last_seq >= 0:
            expected = (self.last_seq + 1) & 0xFF
            if seq != expected:
                self.dropped_frames += 1
        self.last_seq = seq

    @staticmethod
    def _verify_crc(frame_data: bytes) -> bool:
        return frame_data[-1] == crc8(frame_data[:-1])

    def reset(self):
        """重置解析器状态"""
        self.buffer.clear()
        self.frame_count = 0
        self.error_count = 0
        self.sync_errors = 0
        self.crc_errors = 0
        self.last_seq = -1
        self.dropped_frames = 0

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            'frame_count': self.frame_count,
            'error_count': self.error_count,
            'sync_errors': self.sync_errors,
            'crc_errors': self.crc_errors,
            'dropped_frames': self.dropped_frames,
            'buffer_size': len(self.buffer),
            **self.stats
        }
