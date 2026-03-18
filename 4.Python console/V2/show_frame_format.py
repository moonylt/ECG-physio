# -*- coding: utf-8 -*-
"""
显示 ECG 模拟器发送的数据帧结构
"""

import sys
sys.path.insert(0, '.')

import numpy as np
from utils.crc8 import crc8

# 协议常量
STX0 = 0x55
STX1 = 0xAA
MSG_ADS129X_DATA = 0x20
OWN_FU_ID = 0x22
HOST_FU_ID = 0x20


def generate_simple_ecg():
    """生成简单的模拟 ECG 数据"""
    # CH1: ECG 波形 (约 1000 uV)
    ch1 = 1000
    # CH2: ECG 波形 (约 1200 uV)
    ch2 = 1200
    # CH3: ECG 波形 (约 1100 uV)
    ch3 = 1100
    # CH4: 呼吸波形 (约 50000)
    ch4 = 50000
    
    return np.array([
        [ch1, ch2, ch3, ch4],
        [ch1, ch2, ch3, ch4],
        [ch1, ch2, ch3, ch4],
        [ch1, ch2, ch3, ch4],
    ], dtype=np.int32)


def pack_ecg_frame(samples, seq):
    """打包 ECG 数据帧"""
    frame = bytearray()
    frame.append(STX0)
    frame.append(STX1)
    
    payload_len = 48
    frame.append(payload_len & 0xFF)
    frame.append((payload_len >> 8) & 0xFF)
    
    frame.append(OWN_FU_ID)
    frame.append(HOST_FU_ID)
    frame.append(seq & 0xFF)
    frame.append(MSG_ADS129X_DATA)
    
    payload = bytearray()
    for sample_idx in range(4):
        for ch in range(4):
            value = samples[sample_idx, ch]
            value = max(-0x800000, min(0x7FFFFF, value))
            if value < 0:
                value = 0x1000000 + value
            
            payload.append((value >> 16) & 0xFF)
            payload.append((value >> 8) & 0xFF)
            payload.append(value & 0xFF)
    
    frame.extend(payload)
    crc = crc8(frame)
    frame.append(crc)
    
    return bytes(frame)


def show_frame_structure():
    """显示帧结构说明"""
    print("=" * 70)
    print("ECG 数据帧结构")
    print("=" * 70)
    print()
    print("帧格式 (57 字节):")
    print()
    print("  偏移  长度  字段          说明                  示例值")
    print("  ----  ----  ------------  --------------------  --------")
    print("  0     1     STX0         帧起始标志 0           0x55")
    print("  1     1     STX1         帧起始标志 1           0xAA")
    print("  2     1     LEN_L        数据长度低字节         0x30 (48)")
    print("  3     1     LEN_H        数据长度高字节         0x00")
    print("  4     1     SRC          源设备 ID              0x22 (FALCON_FE)")
    print("  5     1     DST          目标设备 ID            0x20 (FALCON_HOST)")
    print("  6     1     SEQ          序列号 (0-255 循环)     0x00")
    print("  7     1     MSGID        消息类型              0x20 (ADS129X 数据)")
    print("  8     48    DATA         数据载荷 (4 样本×4 通道)  见下方详情")
    print("  56    1     CRC          CRC8 校验              计算值")
    print()
    print("=" * 70)
    print()


def show_data_payload():
    """显示数据载荷详情"""
    print("数据载荷详情 (48 字节):")
    print()
    print("  每帧包含 4 个样本，每个样本 4 个通道，每个通道 3 字节 (24 位)")
    print()
    print("  样本 1:")
    print("    CH1: 字节 0-2   (24 位有符号数，MSB 优先)")
    print("    CH2: 字节 3-5")
    print("    CH3: 字节 6-8")
    print("    CH4: 字节 9-11")
    print("  样本 2: 字节 12-23 (同上)")
    print("  样本 3: 字节 24-35 (同上)")
    print("  样本 4: 字节 36-47 (同上)")
    print()
    print("=" * 70)
    print()


def show_example_frame():
    """显示示例帧"""
    print("示例帧 (第 1 帧，序列号=0):")
    print()
    
    # 生成简单数据
    samples = generate_simple_ecg()
    frame = pack_ecg_frame(samples, 0)
    
    # 显示十六进制
    print("十六进制数据:")
    print("-" * 70)
    
    for i in range(0, len(frame), 16):
        offset = i
        hex_part = ' '.join(f'{b:02X}' for b in frame[i:i+16])
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in frame[i:i+16])
        print(f"  {offset:04X}: {hex_part:<48} {ascii_part}")
    
    print("-" * 70)
    print()
    
    # 详细解析
    print("详细解析:")
    print("-" * 70)
    print(f"  帧头：0x{frame[0]:02X} 0x{frame[1]:02X} (STX0=0x55, STX1=0xAA)")
    print(f"  长度：{frame[2] + (frame[3] << 8)} 字节 (0x{frame[3]:02X}{frame[2]:02X})")
    print(f"  源 ID: 0x{frame[4]:02X} (FALCON_FE)")
    print(f"  目标 ID: 0x{frame[5]:02X} (FALCON_HOST)")
    print(f"  序列号：{frame[6]} (0x{frame[6]:02X})")
    print(f"  消息 ID: 0x{frame[7]:02X} (MSG_ADS129X_DATA)")
    print()
    
    # 解析数据载荷
    print("  数据载荷 (4 个样本 × 4 通道):")
    print("  " + "-" * 66)
    
    payload = frame[8:56]
    idx = 0
    for sample_idx in range(4):
        print(f"    样本 {sample_idx + 1}:")
        for ch in range(4):
            b0 = payload[idx]
            b1 = payload[idx + 1]
            b2 = payload[idx + 2]
            
            value = (b0 << 16) | (b1 << 8) | b2
            if value >= 0x800000:
                value -= 0x1000000
            
            print(f"      CH{ch + 1}: 0x{b0:02X}{b1:02X}{b2:02X} = {value:8d} (原始字节：{b0:02X} {b1:02X} {b2:02X})")
            idx += 3
    
    print("  " + "-" * 66)
    print()
    print(f"  CRC8: 0x{frame[56]:02X}")
    print()
    
    # 验证 CRC
    calc_crc = crc8(frame[:-1])
    print(f"  CRC 验证：接收=0x{frame[56]:02X}, 计算=0x{calc_crc:02X}, 匹配={frame[56] == calc_crc}")
    print()


def show_multiple_frames():
    """显示多帧数据"""
    print("=" * 70)
    print("连续帧示例 (序列号 0-2)")
    print("=" * 70)
    print()
    
    samples = generate_simple_ecg()
    
    for seq in range(3):
        frame = pack_ecg_frame(samples, seq)
        print(f"帧 {seq} (前 16 字节):")
        hex_str = ' '.join(f'{b:02X}' for b in frame[:16])
        print(f"  {hex_str}")
        print()
    
    print("...")
    print()


def show_binary_representation():
    """显示二进制表示"""
    print("=" * 70)
    print("帧头二进制表示")
    print("=" * 70)
    print()
    print("  STX0: 0x55 = 0101 0101")
    print("  STX1: 0xAA = 1010 1010")
    print()
    print("  特点：0x55 和 0xAA 是交替的 01 模式，便于时钟恢复")
    print()


def main():
    print()
    show_frame_structure()
    show_data_payload()
    show_binary_representation()
    show_example_frame()
    show_multiple_frames()
    
    print("=" * 70)
    print("串口发送参数")
    print("=" * 70)
    print()
    print(f"  串口：COM4 (虚拟串口对：COM4 <-> COM5)")
    print(f"  波特率：115200 bps")
    print(f"  数据位：8")
    print(f"  停止位：1")
    print(f"  校验位：无")
    print(f"  流控制：无")
    print()
    print(f"  每帧大小：57 字节")
    print(f"  帧率：125 FPS (500SPS / 4 样本)")
    print(f"  数据速率：125 × 57 × 8 = 57,000 bps")
    print(f"  带宽利用率：57000 / 115200 = 49.5%")
    print()
    print("=" * 70)
    print()


if __name__ == '__main__':
    main()
