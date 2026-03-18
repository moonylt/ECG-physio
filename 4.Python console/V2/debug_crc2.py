# -*- coding: utf-8 -*-
"""调试 CRC - 检查 bytearray vs bytes"""

import sys
sys.path.insert(0, '.')

from utils.crc8 import crc8

# 测试数据
data_bytes = b'\x55\xaa\x30\x00\x22\x20\x00\x20' + b'\x00' * 48
data_bytearray = bytearray(data_bytes)

print(f"bytes CRC: {crc8(data_bytes):02x}")
print(f"bytearray CRC: {crc8(bytes(data_bytearray)):02x}")
print(f"bytearray direct CRC: {crc8(data_bytearray):02x}")

# 检查 protocol_parser 中的调用
print()
print("检查 protocol_parser 中的 CRC 调用...")

# 模拟 protocol_parser 的 _verify_crc 方法
def verify_crc(frame_data):
    received_crc = frame_data[-1]
    calculated_crc = crc8(frame_data[:-1])
    print(f"  frame_data type: {type(frame_data)}")
    print(f"  frame_data[:-1] type: {type(frame_data[:-1])}")
    print(f"  received_crc: {received_crc}")
    print(f"  calculated_crc: {calculated_crc:02x}")
    return received_crc == calculated_crc

# 构建测试帧
frame_bytes = data_bytes + bytes([crc8(data_bytes)])
frame_bytearray = bytearray(frame_bytes)

print("\n测试 bytes 帧:")
result = verify_crc(frame_bytes)
print(f"  CRC 匹配：{result}")

print("\n测试 bytearray 帧:")
result = verify_crc(frame_bytearray)
print(f"  CRC 匹配：{result}")
