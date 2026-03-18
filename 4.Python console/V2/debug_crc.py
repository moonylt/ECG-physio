# -*- coding: utf-8 -*-
"""调试 CRC 计算"""

import sys
sys.path.insert(0, '.')

from utils.crc8 import crc8

# 协议常量
STX0 = 0x55
STX1 = 0xAA
MSG_ADS129X_DATA = 0x20
OWN_FU_ID = 0x22
HOST_FU_ID = 0x20

# 构建测试帧
frame = bytearray()
frame.append(STX0)
frame.append(STX1)

payload_len = 48
frame.append(payload_len & 0xFF)
frame.append((payload_len >> 8) & 0xFF)

frame.append(OWN_FU_ID)
frame.append(HOST_FU_ID)
frame.append(0)  # seq
frame.append(MSG_ADS129X_DATA)

# 48 字节数据
payload = bytes([0] * 48)
frame.extend(payload)

# 计算 CRC
calc_crc = crc8(bytes(frame))
frame.append(calc_crc)

print(f"帧长度：{len(frame)} 字节")
print(f"帧头：{frame[0]:02x} {frame[1]:02x}")
print(f"长度：{frame[2]:02x} {frame[3]:02x}")
print(f"源 ID: {frame[4]:02x}")
print(f"目标 ID: {frame[5]:02x}")
print(f"序列号：{frame[6]:02x}")
print(f"消息 ID: {frame[7]:02x}")
print(f"CRC: {frame[-1]:02x}")
print()

# 验证 CRC
received_crc = frame[-1]
calculated_crc = crc8(bytes(frame[:-1]))
print(f"接收 CRC: {received_crc:02x}")
print(f"计算 CRC: {calculated_crc:02x}")
print(f"CRC 匹配：{received_crc == calculated_crc}")
