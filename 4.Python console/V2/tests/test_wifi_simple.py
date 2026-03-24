# -*- coding: utf-8 -*-
"""
WiFi 连接自动化测试 (简化版)
直接测试 TCP 连接功能，不依赖 PyQt 信号
"""

import socket
import threading
import time
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockESP32Server:
    """模拟 ESP32 TCP 服务器"""

    def __init__(self, host='127.0.0.1', port=12345):
        self.host = host
        self.port = port
        self.sock = None
        self.client_sock = None
        self.running = False
        self._thread = None

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        self.sock.settimeout(0.5)
        self.running = True
        self._thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._thread.start()
        time.sleep(0.3)
        print(f"[MockServer] 启动于 {self.host}:{self.port}")

    def _accept_loop(self):
        while self.running:
            try:
                self.client_sock, addr = self.sock.accept()
                print(f"[MockServer] 客户端连接: {addr}")
            except socket.timeout:
                continue
            except:
                break

    def stop(self):
        self.running = False
        if self.client_sock:
            self.client_sock.close()
        if self.sock:
            self.sock.close()
        print("[MockServer] 停止")

    def send_data(self, data: bytes):
        if self.client_sock:
            self.client_sock.sendall(data)


def test_tcp_socket():
    """测试 1: 原始 TCP Socket 连接"""
    print("\n=== 测试 1: TCP Socket 连接 ===")

    server = MockESP32Server(port=12346)
    server.start()

    try:
        # 客户端连接
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(2.0)
        client.connect(('127.0.0.1', 12346))

        time.sleep(0.2)  # 等待连接建立

        # 发送数据
        test_data = b"Hello ESP32!"
        server.send_data(test_data)

        # 接收数据
        received = client.recv(1024)

        if received == test_data:
            print("[PASS] TCP Socket 连接测试")
            result = True
        else:
            print(f"[FAIL] 数据不匹配: {received}")
            result = False

        client.close()
    except Exception as e:
        print(f"[FAIL] 异常: {e}")
        result = False
    finally:
        server.stop()

    return result


def test_tcp_client_class():
    """测试 2: TCPClient 类（需要 PyQt）"""
    print("\n=== 测试 2: TCPClient 类 ===")

    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QEventLoop

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    server = MockESP32Server(port=12347)
    server.start()

    from comms.tcp_client import TCPClient

    client = TCPClient()
    connected = False

    def on_connected():
        nonlocal connected
        connected = True
        print("  [信号] connected")

    client.connected.connect(on_connected)

    try:
        # 启动连接
        client.connect('127.0.0.1', 12347)

        # 处理事件循环
        for _ in range(30):  # 3秒超时
            app.processEvents()
            if connected:
                break
            time.sleep(0.1)

        if connected and client.is_connected:
            print("[PASS] TCPClient 类测试")
            result = True
        else:
            print(f"[FAIL] connected={connected}, is_connected={client.is_connected}")
            result = False

        client.disconnect()
    except Exception as e:
        print(f"[FAIL] 异常: {e}")
        result = False
    finally:
        server.stop()

    return result


def test_wifi_manager():
    """测试 3: WiFiManager 类"""
    print("\n=== 测试 3: WiFiManager 类 ===")

    from PyQt5.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    server = MockESP32Server(port=12348)
    server.start()

    from comms.wifi_manager import WiFiManager

    wifi = WiFiManager()
    connected = False

    def on_connected():
        nonlocal connected
        connected = True
        print("  [信号] WiFi connected")

    wifi.connected.connect(on_connected)

    try:
        wifi.connect_to_custom('127.0.0.1', 12348)

        # 处理事件循环
        for _ in range(30):
            app.processEvents()
            if connected:
                break
            time.sleep(0.1)

        if connected and wifi.is_connected:
            status = wifi.get_status()
            print(f"[PASS] WiFiManager 测试 - {status}")
            result = True
        else:
            print(f"[FAIL] connected={connected}, is_connected={wifi.is_connected}")
            result = False

        wifi.disconnect()
    except Exception as e:
        print(f"[FAIL] 异常: {e}")
        result = False
    finally:
        server.stop()

    return result


def test_data_transfer():
    """测试 4: 数据传输"""
    print("\n=== 测试 4: 数据传输 ===")

    from PyQt5.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    server = MockESP32Server(port=12349)
    server.start()

    from comms.tcp_client import TCPClient

    client = TCPClient()
    connected = False
    received_data = []

    def on_connected():
        nonlocal connected
        connected = True

    def on_data(data):
        received_data.append(data)

    client.connected.connect(on_connected)
    client.data_received.connect(on_data)

    try:
        client.connect('127.0.0.1', 12349)

        # 等待连接
        for _ in range(20):
            app.processEvents()
            if connected:
                break
            time.sleep(0.1)

        if not connected:
            print("[FAIL] 连接超时")
            return False

        # 发送数据
        test_data = b"ECG_DATA_12345"
        server.send_data(test_data)

        # 等待接收
        for _ in range(20):
            app.processEvents()
            if received_data:
                break
            time.sleep(0.1)

        if received_data and test_data in received_data[0]:
            print(f"[PASS] 数据传输测试 - 收到 {len(received_data)} 个数据包")
            result = True
        else:
            print(f"[FAIL] 数据未收到 - received_data={received_data}")
            result = False

        client.disconnect()
    except Exception as e:
        print(f"[FAIL] 异常: {e}")
        result = False
    finally:
        server.stop()

    return result


def main():
    print("=" * 50)
    print("WiFi 功能自动化测试 (简化版)")
    print("=" * 50)

    tests = [
        test_tcp_socket,
        test_tcp_client_class,
        test_wifi_manager,
        test_data_transfer,
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"[ERROR] {test.__name__}: {e}")
            results.append(False)
        time.sleep(0.3)

    print("\n" + "=" * 50)
    print("测试汇总")
    print("=" * 50)

    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total} ({passed/total*100:.0f}%)")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)