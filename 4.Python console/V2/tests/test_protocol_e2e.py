# -*- coding: utf-8 -*-
"""
协议端到端测试
验证 ESP32 模拟数据与上位机解析器的匹配
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.crc8 import crc8
from comms.protocol_parser import ProtocolParser


def build_esp32_frame(seq: int) -> bytes:
    """
    构造一个符合 ESP32 协议的帧
    """
    frame = bytearray(57)
    idx = 0

    # 帧头
    frame[idx] = 0x55
    idx += 1
    frame[idx] = 0xAA
    idx += 1

    # 数据长度
    frame[idx] = 48
    idx += 1
    frame[idx] = 0
    idx += 1

    # 源和目标地址
    frame[idx] = 0x01
    idx += 1
    frame[idx] = 0x00
    idx += 1

    # 序列号
    frame[idx] = seq & 0xFF
    idx += 1

    # 消息类型
    frame[idx] = 0x20  # ADS129X_DATA
    idx += 1

    # 模拟数据 (48 字节)
    for i in range(48):
        frame[idx] = (i * 17 + seq) & 0xFF
        idx += 1

    # CRC8
    frame[idx] = crc8(bytes(frame[:-1]))

    return bytes(frame)


def test_protocol_match():
    """测试协议匹配"""
    print("=" * 50)
    print("协议端到端测试")
    print("=" * 50)

    parser = ProtocolParser()

    # 发送 10 帧数据
    print("\n发送 10 帧数据...")
    frames_received = []

    for i in range(10):
        frame = build_esp32_frame(i)
        parsed = parser.parse(frame)
        frames_received.extend(parsed)

    print(f"成功解析: {len(frames_received)} 帧")

    if len(frames_received) == 10:
        print("\n[PASS] 协议匹配测试")
        print(f"  帧序号: {[f.seq for f in frames_received]}")

        # 显示样本数据
        frame = frames_received[0]
        print(f"  样本数据形状: {frame.samples.shape}")
        print(f"  CH1 样本: {frame.samples[:, 0]}")
        return True
    else:
        print("\n[FAIL] 协议匹配测试")
        print(f"  期望 10 帧，实际 {len(frames_received)} 帧")

        # 调试信息
        stats = parser.get_stats()
        print(f"  解析器统计: {stats}")
        return False


def test_crc_verification():
    """测试 CRC 校验"""
    print("\n" + "=" * 50)
    print("CRC 校验测试")
    print("=" * 50)

    frame = build_esp32_frame(0)

    # 验证 CRC
    received_crc = frame[-1]
    calculated_crc = crc8(frame[:-1])

    print(f"接收 CRC: 0x{received_crc:02X}")
    print(f"计算 CRC: 0x{calculated_crc:02X}")

    if received_crc == calculated_crc:
        print("\n[PASS] CRC 校验测试")
        return True
    else:
        print("\n[FAIL] CRC 校验测试")
        return False


def test_frame_structure():
    """测试帧结构"""
    print("\n" + "=" * 50)
    print("帧结构测试")
    print("=" * 50)

    frame = build_esp32_frame(42)

    print(f"帧长度: {len(frame)} 字节 (期望 57)")
    print(f"帧头: 0x{frame[0]:02X} 0x{frame[1]:02X} (期望 0x55 0xAA)")
    print(f"数据长度: {frame[2] + (frame[3] << 8)} (期望 48)")
    print(f"序列号: {frame[6]} (期望 42)")
    print(f"消息类型: 0x{frame[7]:02X} (期望 0x20)")

    checks = [
        len(frame) == 57,
        frame[0] == 0x55,
        frame[1] == 0xAA,
        frame[2] == 48,
        frame[6] == 42,
        frame[7] == 0x20,
    ]

    if all(checks):
        print("\n[PASS] 帧结构测试")
        return True
    else:
        print("\n[FAIL] 帧结构测试")
        return False


def main():
    results = []

    results.append(test_frame_structure())
    results.append(test_crc_verification())
    results.append(test_protocol_match())

    print("\n" + "=" * 50)
    print("测试汇总")
    print("=" * 50)

    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)