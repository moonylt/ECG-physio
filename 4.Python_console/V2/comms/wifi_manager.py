# -*- coding: utf-8 -*-
"""
WiFi Manager Module
Manages WiFi TCP connection with ESP32, provides SerialManager-like interface
Supports device discovery via WiFi AP scanning
"""

import socket
from typing import List, Dict
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from comms.tcp_client import TCPClient
from comms.wifi_scanner import WiFiScanner, WiFiScannerWorker, WiFiAPInfo


class WiFiManager(QObject):
    """
    WiFi Manager
    Provides WiFi connection, disconnect, data send/receive and device discovery
    """

    # Signals
    data_received = pyqtSignal(bytes)
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    error_occurred = pyqtSignal(str)
    connection_status_changed = pyqtSignal(bool)  # is_connected
    devices_found = pyqtSignal(list)  # List of ECG device dicts

    # ESP32 default config
    DEFAULT_ESP32_IP = "192.168.4.1"  # ESP32 SoftAP default IP
    DEFAULT_PORT = 12345

    def __init__(self):
        super().__init__()
        self.tcp_client = TCPClient()
        self.is_connected = False
        self._scanner = WiFiScanner()
        self._scan_worker = None

        # Connect TCP client signals
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
        Get available WiFi AP list (legacy method, returns all APs)

        Returns:
            AP name list
        """
        all_aps = self._scanner.scan()
        return [ap.ssid for ap in all_aps]

    # ==================== New Device Discovery Methods ====================

    def scan_esp32_devices(self) -> List[Dict]:
        """
        Scan for ECG-Physio ESP32 devices (synchronous)

        Returns:
            List of device dicts with ssid, bssid, signal, channel
        """
        devices = self._scanner.scan_ecg_devices()
        return [
            {
                'ssid': d.ssid,
                'bssid': d.bssid,
                'signal': d.signal,
                'channel': d.channel,
                'security': d.security
            }
            for d in devices
        ]

    def scan_esp32_devices_async(self):
        """
        Scan for ECG-Physio devices asynchronously

        Emits devices_found signal when scan completes
        """
        if self._scan_worker and self._scan_worker.isRunning():
            return  # Already scanning

        self._scan_worker = WiFiScannerWorker(filter_ecg=True)
        self._scan_worker.scan_complete.connect(self._on_scan_complete)
        self._scan_worker.scan_error.connect(self._on_scan_error)
        self._scan_worker.start()

    def _on_scan_complete(self, devices: list):
        """Scan complete callback"""
        self.devices_found.emit(devices)

    def _on_scan_error(self, error: str):
        """Scan error callback"""
        self.error_occurred.emit(f"WiFi scan error: {error}")

    def get_current_wifi_ssid(self) -> str:
        """
        Get currently connected WiFi SSID

        Returns:
            SSID string or empty if not connected
        """
        conn = self._scanner.get_current_connection()
        return conn.get('ssid', '')

    def get_current_wifi_connection(self) -> Dict:
        """
        Get current WiFi connection details

        Returns:
            dict with ssid, bssid, connected
        """
        return self._scanner.get_current_connection()

    def is_connected_to_ecg_ap(self) -> bool:
        """
        Check if currently connected to ECG-Physio AP

        Returns:
            True if connected to ECG-Physio AP
        """
        ssid = self.get_current_wifi_ssid()
        return ssid.startswith(WiFiScanner.TARGET_SSID_PREFIX)

    def get_selected_device_ip(self) -> str:
        """
        Get IP address for selected ECG device

        ESP32 SoftAP always uses 192.168.4.1

        Returns:
            Default ESP32 IP address
        """
        return self.DEFAULT_ESP32_IP
