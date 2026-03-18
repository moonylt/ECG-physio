# -*- coding: utf-8 -*-
"""详细调试协议解析器 - 检查_parse_frame"""

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
print()

# 创建解析器
parser = ProtocolParser()

# 手动调用 _parse_frame
print("手动调用 _parse_frame...")
try:
    result = parser._parse_frame(bytes(frame))
    print(f"_parse_frame 返回：{result}")
    if result:
        print(f"  seq: {result.seq}")
        print(f"  samples shape: {result.samples.shape}")
        print(f"  samples: {result.samples}")
except Exception as e:
    print(f"_parse_frame 异常：{e}")
    traceback.print_exc()

print()

# 检查 parse 方法中的逻辑
print("检查 parse 方法中的逻辑...")
parser.buffer.extend(bytes(frame))
print(f"buffer 大小：{len(parser.buffer)}")

# 检查帧头
print(f"buffer[0]: {parser.buffer[0]:02x} (STX0={parser.STX0:02x})")
print(f"buffer[1]: {parser.buffer[1]:02x} (STX1={parser.STX1:02x})")
print(f"帧头匹配：{parser.buffer[0] == parser.STX0 and parser.buffer[1] == parser.STX1}")

# 检查长度
print(f"帧长度足够：{len(parser.buffer) >= parser.FRAME_LEN}")

# 提取帧
frame_data = bytes(parser.buffer[:parser.FRAME_LEN])
print(f"frame_data 长度：{len(frame_data)}")

# CRC 校验
received_crc = frame_data[-1]
calculated_crc = parser.crc8(frame_data[:-1])
print(f"CRC 校验：received={received_crc}, calculated={calculated_crc}, match={received_crc == calculated_crc}")

# 消息类型
msg_id = frame_data[7]
print(f"MSGID: {msg_id} (期望={parser.MSG_ADS129X_DATA})")
print(f"消息类型匹配：{msg_id == parser.MSG_ADS129X_DATA}")
