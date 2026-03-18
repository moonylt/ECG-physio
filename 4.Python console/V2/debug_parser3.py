# -*- coding: utf-8 -*-
"""详细调试协议解析器"""

import sys
sys.path.insert(0, '.')

from comms.protocol_parser import ProtocolParser

# 构建测试帧
frame = bytearray()
frame.append(0x55)  # STX0
frame.append(0xAA)  # STX1
frame.append(48)    # LEN_L
frame.append(0)     # LEN_H
frame.append(0x22)  # SRC (OWN_FU_ID)
frame.append(0x20)  # DST (HOST_FU_ID)
frame.append(0)     # SEQ
frame.append(0x20)  # MSGID (MSG_ADS129X_DATA)
frame.extend([0] * 48)  # DATA

# 计算 CRC 并添加
from utils.crc8 import crc8
calc_crc = crc8(bytes(frame))
frame.append(calc_crc)

print(f"帧长度：{len(frame)} 字节")
print(f"帧内容：{bytes(frame).hex()}")
print(f"CRC: {calc_crc:02x}")
print()

# 创建解析器
parser = ProtocolParser()

# 打印解析器常量
print(f"解析器常量:")
print(f"  STX0: {parser.STX0:02x}")
print(f"  STX1: {parser.STX1:02x}")
print(f"  MSG_ADS129X_DATA: {parser.MSG_ADS129X_DATA:02x}")
print(f"  FRAME_LEN: {parser.FRAME_LEN}")
print(f"  HEADER_LEN: {parser.HEADER_LEN}")
print(f"  DATA_LEN: {parser.DATA_LEN}")
print()

# 解析
print("开始解析...")
frames = parser.parse(bytes(frame))

print(f"解析结果：{len(frames)} 帧")
print(f"Buffer 大小：{len(parser.buffer)}")
print(f"CRC 错误：{parser.crc_errors}")
print(f"同步错误：{parser.sync_errors}")
print(f"成功帧：{parser.frame_count}")

# 手动检查帧头
print()
print("手动检查帧头:")
print(f"  buffer[0]: {parser.buffer[0]:02x} (期望：{parser.STX0:02x})")
print(f"  buffer[1]: {parser.buffer[1]:02x} (期望：{parser.STX1:02x})")
print(f"  buffer[6]: {parser.buffer[6]:02x} (SEQ)")
print(f"  buffer[7]: {parser.buffer[7]:02x} (MSGID, 期望：{parser.MSG_ADS129X_DATA:02x})")
