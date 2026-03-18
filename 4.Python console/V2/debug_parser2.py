# -*- coding: utf-8 -*-
"""直接在协议解析器上下文中调试"""

import sys
sys.path.insert(0, '.')

# 直接导入协议解析器的 crc8
from comms.protocol_parser import ProtocolParser
from comms.protocol_parser import crc8 as parser_crc8
from utils.crc8 import crc8 as utils_crc8

print(f"protocol_parser.crc8: {parser_crc8}")
print(f"utils.crc8: {utils_crc8}")
print(f"是否相同：{parser_crc8 == utils_crc8}")

# 测试 CRC 计算
test_data = b'\x55\xaa\x30\x00\x22\x20\x00\x20' + b'\x00' * 48
print(f"\nparser_crc8 结果：{parser_crc8(test_data):02x}")
print(f"utils_crc8 结果：{utils_crc8(test_data):02x}")

# 构建完整帧并验证
frame = bytearray()
frame.append(0x55)
frame.append(0xAA)
frame.append(48)
frame.append(0)
frame.append(0x22)
frame.append(0x20)
frame.append(0)
frame.append(0x20)
frame.extend([0] * 48)

# 使用 parser_crc8 计算
calc_crc = parser_crc8(bytes(frame))
frame.append(calc_crc)

print(f"\n使用 parser_crc8 计算的 CRC: {calc_crc:02x}")

# 验证
received_crc = frame[-1]
calculated_crc = parser_crc8(bytes(frame[:-1]))
print(f"接收 CRC: {received_crc}")
print(f"计算 CRC: {calculated_crc:02x}")
print(f"CRC 匹配：{received_crc == calculated_crc}")

# 现在测试协议解析器
print("\n\n测试协议解析器...")
parser = ProtocolParser()
frames = parser.parse(bytes(frame))
print(f"解析结果：{len(frames)} 帧")
print(f"CRC 错误：{parser.crc_errors}")
print(f"成功帧：{parser.frame_count}")
