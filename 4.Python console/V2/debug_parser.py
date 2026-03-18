# -*- coding: utf-8 -*-
"""调试协议解析器"""

import sys
sys.path.insert(0, '.')

from utils.crc8 import crc8
from comms.protocol_parser import ProtocolParser

# 协议常量
STX0 = 0x55
STX1 = 0xAA
MSG_ADS129X_DATA = 0x20
OWN_FU_ID = 0x22
HOST_FU_ID = 0x20

def pack_test_frame(seq):
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
    
    # 48 字节测试数据 (10 个样本 × 4 通道 × 3 字节)
    payload = bytearray()
    for sample_idx in range(10):
        for ch in range(4):
            value = 1000  # 测试值
            payload.append((value >> 16) & 0xFF)
            payload.append((value >> 8) & 0xFF)
            payload.append(value & 0xFF)
    
    frame.extend(payload)
    
    # CRC
    calc_crc = crc8(bytes(frame))
    frame.append(calc_crc)
    
    return bytes(frame)


# 创建解析器
parser = ProtocolParser()

# 测试 10 帧
print("测试协议解析器...")
print()

for i in range(10):
    frame = pack_test_frame(i)
    
    # 验证 CRC
    received_crc = frame[-1]
    calculated_crc = crc8(bytes(frame[:-1]))
    crc_ok = received_crc == calculated_crc
    
    # 解析
    frames = parser.parse(frame)
    
    print(f"帧 {i}: CRC={crc_ok}, 解析成功={len(frames) > 0}, CRC 错误={parser.crc_errors}")

print()
print(f"统计：成功帧={parser.frame_count}, CRC 错误={parser.crc_errors}")
