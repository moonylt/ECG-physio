# -*- coding: utf-8 -*-
"""
模拟 ESP32 测试服务器
在本地运行，模拟 ESP32 发送 ECG 数据，用于测试上位机

运行方法：
    python tests/mock_esp32_server.py

然后在上位机中选择 WiFi 模式，连接 127.0.0.1:12345
"""

import socket
import threading
import time
import struct
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.crc8 import crc8


class MockESP32Server:
    """
    模拟 ESP32 TCP 服务器
    发送符合协议格式的模拟 ECG 数据
    """

    # 协议常量
    STX0 = 0x55
    STX1 = 0xAA
    MSG_ADS129X_DATA = 0x20
    FRAME_SIZE = 57
    NUM_CHANNELS = 4
    SAMPLES_PER_FRAME = 4

    def __init__(self, host='127.0.0.1', port=12345):
        self.host = host
        self.port = port
        self.running = False
        self.client_connected = False
        self.frame_counter = 0
        self.ecg_phase = [0.0] * 4

    def _generate_ecg_sample(self, channel: int, phase: float) -> int:
        """
        生成模拟 ECG 样本值
        使用正弦波叠加模拟 ECG 波形
        """
        value = 0.0

        # P 波
        p_phase = phase - 0.1
        if -0.1 < p_phase < 0.1:
            value += 0.15 * (0.1 - abs(p_phase)) * 10 * (1 if p_phase > 0 else -1)

        # QRS 复合波
        qrs_phase = phase - 0.3
        if -0.05 < qrs_phase < 0.05:
            value += 1.0 * (0.05 - abs(qrs_phase)) * 20
        if -0.02 < qrs_phase < 0.02:
            value += 0.3 * (0.02 - abs(qrs_phase)) * 50

        # T 波
        t_phase = phase - 0.5
        if -0.15 < t_phase < 0.15:
            value += 0.3 * (0.15 - abs(t_phase)) * 3.33

        # 通道偏移
        value += channel * 0.1

        # 添加噪声
        import random
        value += (random.random() - 0.5) * 0.02

        # 缩放到 24 位范围
        sample = int(value * 4000000)
        return sample

    def _build_frame(self) -> bytes:
        """
        构造一个 ECG 数据帧
        帧格式：STX0(1B) + STX1(1B) + LEN_L(1B) + LEN_H(1B) + SRC(1B) + DST(1B) + SEQ(1B) + MSGID(1B) + DATA(48B) + CRC(1B)
        """
        frame = bytearray(self.FRAME_SIZE)
        idx = 0

        # 帧头
        frame[idx] = self.STX0
        idx += 1
        frame[idx] = self.STX1
        idx += 1

        # 数据长度
        frame[idx] = 48
        idx += 1
        frame[idx] = 0
        idx += 1

        # 源和目标地址
        frame[idx] = 0x01  # SRC: ESP32
        idx += 1
        frame[idx] = 0x00  # DST: PC
        idx += 1

        # 序列号
        frame[idx] = self.frame_counter & 0xFF
        idx += 1
        self.frame_counter += 1

        # 消息类型
        frame[idx] = self.MSG_ADS129X_DATA
        idx += 1

        # 生成 4 个样本，每个样本 4 个通道
        for sample_idx in range(self.SAMPLES_PER_FRAME):
            for ch in range(self.NUM_CHANNELS):
                # 更新相位
                self.ecg_phase[ch] += 0.02
                if self.ecg_phase[ch] > 1.0:
                    self.ecg_phase[ch] -= 1.0

                # 生成样本
                value = self._generate_ecg_sample(ch, self.ecg_phase[ch])

                # 3 字节，大端序
                frame[idx] = (value >> 16) & 0xFF
                idx += 1
                frame[idx] = (value >> 8) & 0xFF
                idx += 1
                frame[idx] = value & 0xFF
                idx += 1

        # CRC8 校验
        frame[idx] = crc8(bytes(frame[:-1]))

        return bytes(frame)

    def start(self):
        """启动服务器"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.running = True

        print(f"[MockESP32] 服务器启动于 {self.host}:{self.port}")
        print(f"[MockESP32] 等待上位机连接...")

        # 启动接受连接线程
        self._accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._accept_thread.start()

    def _accept_loop(self):
        """接受连接循环"""
        while self.running:
            try:
                self.server_socket.settimeout(1.0)
                client, addr = self.server_socket.accept()
                print(f"[MockESP32] 上位机连接: {addr}")
                self.client_connected = True
                self._handle_client(client)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"[MockESP32] 接受连接错误: {e}")

    def _handle_client(self, client_socket):
        """处理客户端连接"""
        frame_interval = 1.0 / 125  # 125 FPS
        frames_sent = 0
        start_time = time.time()

        try:
            while self.running and self.client_connected:
                # 构造并发送帧
                frame = self._build_frame()
                client_socket.sendall(frame)
                frames_sent += 1

                # 控制帧率
                time.sleep(frame_interval)

                # 每 5 秒打印统计
                if frames_sent % 625 == 0:
                    elapsed = time.time() - start_time
                    rate = frames_sent / elapsed
                    print(f"[MockESP32] 已发送 {frames_sent} 帧, 速率: {rate:.1f} FPS")

        except BrokenPipeError:
            print("[MockESP32] 客户端断开连接")
        except Exception as e:
            print(f"[MockESP32] 发送错误: {e}")
        finally:
            self.client_connected = False
            client_socket.close()
            elapsed = time.time() - start_time
            print(f"[MockESP32] 统计: 共发送 {frames_sent} 帧, 耗时 {elapsed:.1f}s")

    def stop(self):
        """停止服务器"""
        self.running = False
        self.client_connected = False
        if hasattr(self, 'server_socket'):
            self.server_socket.close()
        print("[MockESP32] 服务器停止")


def main():
    print("=" * 50)
    print("ECG Physio 模拟 ESP32 服务器")
    print("=" * 50)
    print()
    print("此工具模拟 ESP32 发送 ECG 数据，用于测试上位机")
    print()
    print("使用方法:")
    print("  1. 运行此脚本")
    print("  2. 启动上位机 (python main.py)")
    print("  3. 选择 'WiFi 模式' 选项卡")
    print("  4. 选择 '自定义 TCP 服务器'")
    print("  5. 输入 IP: 127.0.0.1, 端口: 12345")
    print("  6. 点击 '测试' 然后 '连接'")
    print()
    print("帧格式: 57 字节")
    print("  STX0(1B) + STX1(1B) + LEN(2B) + SRC(1B) + DST(1B) + SEQ(1B) + MSGID(1B) + DATA(48B) + CRC(1B)")
    print()
    print("按 Ctrl+C 停止")
    print("-" * 50)

    server = MockESP32Server()
    server.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n用户中断")
    finally:
        server.stop()


if __name__ == "__main__":
    main()