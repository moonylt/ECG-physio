# -*- coding: utf-8 -*-
"""
WiFi 管理器模块
负责与 ESP32 建立 WiFi TCP 连接，提供类似 SerialManager 的接口
"""

import socket
from PyQt5.QtCore import QObject, pyqtSignal
from comms.tcp_client import TCPClient


class WiFiManager(QObject):
    """
    WiFi 管理器
    提供 WiFi 连接、断开、数据收发等功能
    """
    data_received = pyqtSignal(bytes)
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    error_occurred = pyqtSignal(str)
    connection_status_changed = pyqtSignal(bool)  # is_connected

    # ESP32 默认配置
    DEFAULT_ESP32_IP = "192.168.4.1"  # ESP32 SoftAP 默认 IP
    DEFAULT_PORT = 12345

    def __init__(self):
        super().__init__()
        self.tcp_client = TCPClient()
        self.is_connected = False

        # 连接 TCP 客户端信号
        self.tcp_client.data_received.connect(self.data_received)
        self.tcp_client.connected.connect(self._on_tcp_connected)
        self.tcp_client.disconnected.connect(self._on_tcp_disconnected)
        self.tcp_client.error_occurred.connect(self.error_occurred)

    def _on_tcp_connected(self):
        """TCP 连接成功回调"""
        self.is_connected = True
        self.connected.emit()
        self.connection_status_changed.emit(True)

    def _on_tcp_disconnected(self):
        """TCP 断开连接回调"""
        self.is_connected = False
        self.disconnected.emit()
        self.connection_status_changed.emit(False)

    def connect_to_esp32(self, ip: str = None, port: int = None) -> bool:
        """
        连接到 ESP32 TCP Server

        Args:
            ip: ESP32 IP 地址，默认 192.168.4.1
            port: TCP 端口，默认 12345

        Returns:
            True 如果连接成功，False 否则
        """
        target_ip = ip if ip else self.DEFAULT_ESP32_IP
        target_port = port if port else self.DEFAULT_PORT

        return self.tcp_client.connect(target_ip, target_port)

    def connect_to_custom(self, ip: str, port: int) -> bool:
        """
        连接到自定义 TCP 服务器

        Args:
            ip: 服务器 IP 地址
            port: 服务器端口

        Returns:
            True 如果连接成功，False 否则
        """
        return self.tcp_client.connect(ip, port)

    def disconnect(self):
        """断开 WiFi 连接"""
        self.tcp_client.disconnect()
        self.is_connected = False

    def write(self, data: bytes) -> bool:
        """
        发送数据

        Args:
            data: 要发送的数据

        Returns:
            True 如果发送成功
        """
        return self.tcp_client.write(data)

    def get_status(self) -> str:
        """
        获取连接状态

        Returns:
            状态字符串
        """
        return self.tcp_client.get_status()

    def test_connection(self, ip: str = None, port: int = None, timeout: float = 3.0) -> bool:
        """
        测试连接（同步，用于连接前探测）

        Args:
            ip: 目标 IP
            port: 目标端口
            timeout: 超时时间（秒）

        Returns:
            True 如果可连接，False 否则
        """
        target_ip = ip if ip else self.DEFAULT_ESP32_IP
        target_port = port if port else self.DEFAULT_PORT

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((target_ip, target_port))
            sock.close()
            return result == 0
        except socket.error:
            return False

    def get_available_aps(self) -> list:
        """
        获取可用的 WiFi AP 列表（需要系统支持）
        注意：此功能在不同平台实现不同，暂时返回空列表

        Returns:
            AP 名称列表
        """
        # TODO: 实现平台相关的 WiFi 扫描
        # Windows: 使用 wlanapi
        # macOS: 使用 CoreWLAN
        # Linux: 使用 iwlist/iw
        return []
