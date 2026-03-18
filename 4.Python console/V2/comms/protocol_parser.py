# -*- coding: utf-8 -*-
"""
协议解析器
解析 MCU 发送的 ECG 数据帧
"""

import time
from dataclasses import dataclass
from collections import deque
from typing import List, Optional
import numpy as np

from utils.crc8 import crc8


@dataclass
class ECGFrame:
    """
    ECG 数据帧
    """
    timestamp: float          # 时间戳 (秒)
    seq: int                  # 序列号
    samples: np.ndarray       # 样本数据 shape: (4, 4), dtype=int32
    raw_payload: bytes        # 原始数据载荷 (用于调试)
    
    def __post_init__(self):
        # 确保 samples 是正确的形状和类型
        if isinstance(self.samples, list):
            self.samples = np.array(self.samples, dtype=np.int32)
        self.samples = self.samples.astype(np.int32)


class ProtocolParser:
    """
    协议解析器

    帧格式 (57 字节):
    STX0(1B) + STX1(1B) + LEN_L(1B) + LEN_H(1B) + SRC(1B) + DST(1B) + SEQ(1B) + MSGID(1B) + DATA(48B) + CRC(1B)

    DATA 载荷 (48 字节):
    4 个样本 × 4 通道 × 3 字节/通道 = 48 字节
    每样本：[CH1_24bit][CH2_24bit][CH3_24bit][CH4_24bit]
    """
    
    # 协议常量
    STX0 = 0x55
    STX1 = 0xAA
    MSG_ADS129X_DATA = 0x20
    HEADER_LEN = 8       # 帧头长度
    DATA_LEN = 48        # 数据载荷长度
    CRC_LEN = 1          # CRC 长度
    FRAME_LEN = HEADER_LEN + DATA_LEN + CRC_LEN  # 总帧长 57 字节
    
    def __init__(self):
        self.buffer = bytearray()
        self.frame_count = 0      # 成功解析的帧数
        self.error_count = 0      # 错误计数
        self.sync_errors = 0      # 同步错误计数
        self.crc_errors = 0       # CRC 错误计数
        self.last_seq = -1        # 上一个序列号
        
        # 统计信息
        self.stats = {
            'total_bytes': 0,
            'valid_frames': 0,
            'dropped_frames': 0
        }
    
    def parse(self, raw_data: bytes) -> List[ECGFrame]:
        """
        解析原始数据
        
        Args:
            raw_data: 从串口接收的原始字节数据
            
        Returns:
            ECGFrame 列表
        """
        self.buffer.extend(raw_data)
        self.stats['total_bytes'] += len(raw_data)
        
        frames = []
        
        while len(self.buffer) >= self.FRAME_LEN:
            # 查找帧头
            if self.buffer[0] != self.STX0 or self.buffer[1] != self.STX1:
                # 帧头不同步，丢弃第一个字节
                self.buffer.pop(0)
                self.sync_errors += 1
                self.error_count += 1
                continue
            
            # 检查帧长度是否足够
            if len(self.buffer) < self.FRAME_LEN:
                break
            
            # 提取完整帧
            frame_data = bytes(self.buffer[:self.FRAME_LEN])
            
            # CRC 校验
            if not self._verify_crc(frame_data):
                self.crc_errors += 1
                self.error_count += 1
                # CRC 错误，丢弃第一个字节并继续
                self.buffer.pop(0)
                continue
            
            # 验证消息类型
            msg_id = frame_data[7]
            if msg_id != self.MSG_ADS129X_DATA:
                # 消息类型不支持，丢弃
                self.buffer.pop(0)
                continue
            
            # 解析帧
            try:
                frame = self._parse_frame(frame_data)
                if frame:
                    frames.append(frame)
                    self.frame_count += 1
                    self.stats['valid_frames'] += 1
                    
                    # 检查序列号连续性
                    if self.last_seq >= 0:
                        expected_seq = (self.last_seq + 1) & 0xFF
                        if frame.seq != expected_seq:
                            # 序列号不连续，可能有丢包
                            pass
                    self.last_seq = frame.seq
                    
            except Exception as e:
                self.error_count += 1
            
            # 移除已处理的帧
            self.buffer = self.buffer[self.FRAME_LEN:]
        
        return frames
    
    def _parse_frame(self, frame_data: bytes) -> Optional[ECGFrame]:
        """
        解析单帧数据

        Args:
            frame_data: 完整的 57 字节帧

        Returns:
            ECGFrame 对象
        """
        # 提取帧字段
        seq = frame_data[6]
        payload = frame_data[8:56]  # 48 字节数据

        # 解析 48 字节为 10 样本×4 通道的 24 位数据
        # 注意：48 字节 = 16 个 24 位值 = 4 个样本 × 4 通道
        # 或者：每样本 12 字节（4 通道×3 字节），共 4 个样本
        samples = np.zeros((4, 4), dtype=np.int32)
        idx = 0

        for sample_idx in range(4):
            for ch in range(4):
                # 3 字节转 24 位有符号数 (MSB 优先)
                b0 = payload[idx]
                b1 = payload[idx + 1]
                b2 = payload[idx + 2]

                value = (b0 << 16) | (b1 << 8) | b2

                # 转换为有符号数
                if value >= 0x800000:
                    value -= 0x1000000

                samples[sample_idx, ch] = value
                idx += 3

        return ECGFrame(
            timestamp=time.time(),
            seq=seq,
            samples=samples,
            raw_payload=payload
        )
    
    def _verify_crc(self, frame_data: bytes) -> bool:
        """
        验证 CRC 校验
        
        Args:
            frame_data: 完整数据帧
            
        Returns:
            True 如果校验通过
        """
        received_crc = frame_data[-1]
        calculated_crc = crc8(frame_data[:-1])
        return received_crc == calculated_crc
    
    def reset(self):
        """重置解析器状态"""
        self.buffer.clear()
        self.frame_count = 0
        self.error_count = 0
        self.sync_errors = 0
        self.crc_errors = 0
        self.last_seq = -1
    
    def get_stats(self) -> dict:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        return {
            'frame_count': self.frame_count,
            'error_count': self.error_count,
            'sync_errors': self.sync_errors,
            'crc_errors': self.crc_errors,
            'buffer_size': len(self.buffer),
            **self.stats
        }
