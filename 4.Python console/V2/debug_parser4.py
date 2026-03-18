# -*- coding: utf-8 -*-
"""详细调试协议解析器 - 带异常捕获"""

import sys
sys.path.insert(0, '.')

from comms.protocol_parser import ProtocolParser
import traceback

# 构建测试帧
frame = bytearray()
frame.append(0x55)  # STX0
frame.append(0xAA)  # STX1
frame.append(48)    # LEN_L
frame.append(0)     # LEN_H
frame.append(0x22)  # SRC
frame.append(0x20)  # DST
frame.append(0)     # SEQ
frame.append(0x20)  # MSGID
frame.extend([0] * 48)  # DATA

from utils.crc8 import crc8
calc_crc = crc8(bytes(frame))
frame.append(calc_crc)

print(f"帧长度：{len(frame)} 字节")
print(f"CRC: {calc_crc:02x}")
print()

# 创建解析器
parser = ProtocolParser()

# 手动调用 parse 并捕获异常
try:
    print("调用 parser.parse()...")
    frames = parser.parse(bytes(frame))
    print(f"解析结果：{len(frames)} 帧")
except Exception as e:
    print(f"异常：{e}")
    traceback.print_exc()

print()
print(f"统计:")
print(f"  buffer_size: {len(parser.buffer)}")
print(f"  frame_count: {parser.frame_count}")
print(f"  error_count: {parser.error_count}")
print(f"  sync_errors: {parser.sync_errors}")
print(f"  crc_errors: {parser.crc_errors}")

# 手动验证 CRC
print()
print("手动验证 CRC...")
received_crc = frame[-1]
calculated_crc = crc8(bytes(frame[:-1]))
print(f"  received_crc: {received_crc} (0x{received_crc:02x})")
print(f"  calculated_crc: {calculated_crc} (0x{calculated_crc:02x})")
print(f"  CRC 匹配：{received_crc == calculated_crc}")

# 检查消息类型
print()
print("检查消息类型...")
msg_id = frame[7]
print(f"  msg_id: {msg_id} (0x{msg_id:02x})")
print(f"  MSG_ADS129X_DATA: {parser.MSG_ADS129X_DATA} (0x{parser.MSG_ADS129X_DATA:02x})")
print(f"  消息类型匹配：{msg_id == parser.MSG_ADS129X_DATA}")
