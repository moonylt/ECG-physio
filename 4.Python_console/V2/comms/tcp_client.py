# -*- coding: utf-8 -*-
"""
TCP 客户端
负责与 ESP32 TCP Server 建立连接并收发数据
"""

import socket
import threading
from PyQt5.QtCore import QObject, pyqtSignal, QThread


class TCPClientWorker(QThread):
    """
    TCP 客户端工作线程
    在独立线程中运行，避免阻塞 UI
    """
    data_received = pyqtSignal(bytes)
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, host: str, port: int, timeout: float = 1.0):
        super().__init__()
        self.host = host
        self.port = port
        self.timeout = timeout
        self.running = True
        self.sock = None
        self.is_connected = False

    def run(self):
        """线程运行函数"""
        try:
            # 创建 socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)

            # 连接服务器
            self.sock.connect((self.host, self.port))
            self.sock.setblocking(False)  # 设置为非阻塞模式

            self.is_connected = True
            self.connected.emit()

            # 循环读取数据
            while self.running:
                try:
                    data = self.sock.recv(4096)
                    if data:
                        self.data_received.emit(data)
                    else:
                        # 连接关闭
                        break
                except socket.timeout:
                    continue
                except BlockingIOError:
                    # 非阻塞模式下没有数据时抛出
                    self.msleep(10)
                    continue
                except ConnectionResetError:
                    break

        except socket.error as e:
            self.error_occurred.emit(f"TCP 连接错误：{str(e)}")
        except Exception as e:
            self.error_occurred.emit(f"未知错误：{str(e)}")
        finally:
            self._cleanup()

    def _cleanup(self):
        """清理资源"""
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        self.is_connected = False
        self.disconnected.emit()

    def stop(self):
        """停止线程"""
        self.running = False
        self.wait()

    def write(self, data: bytes) -> bool:
        """发送数据"""
        if self.sock and self.is_connected:
            try:
                self.sock.sendall(data)
                return True
            except socket.error:
                return False
        return False


class TCPClient(QObject):
    """
    TCP 客户端管理器
    提供 TCP 连接、断开、数据收发等功能
    """
    data_received = pyqtSignal(bytes)
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.worker = None
        self.is_connected = False
        self.target_host = "192.168.4.1"
        self.target_port = 12345

    def connect(self, host: str = None, port: int = None) -> bool:
        """
        连接到 TCP 服务器

        Args:
            host: 服务器 IP 地址，默认 192.168.4.1（ESP32 AP 模式）
            port: 服务器端口，默认 12345

        Returns:
            True 如果连接成功，False 否则
        """
        if self.is_connected:
            self.disconnect()

        if host:
            self.target_host = host
        if port:
            self.target_port = port

        try:
            self.worker = TCPClientWorker(self.target_host, self.target_port)
            self.worker.data_received.connect(self.data_received)
            self.worker.connected.connect(self._on_connected)
            self.worker.disconnected.connect(self._on_disconnected)
            self.worker.error_occurred.connect(self._on_worker_error)
            self.worker.start()
            return True
        except Exception as e:
            self.error_occurred.emit(f"连接失败：{str(e)}")
            return False

    def disconnect(self):
        """断开 TCP 连接"""
        if self.worker:
            self.worker.stop()
            self.worker = None
        self.is_connected = False

    def write(self, data: bytes) -> bool:
        """
        发送数据

        Args:
            data: 要发送的数据

        Returns:
            True 如果发送成功
        """
        if self.worker and self.is_connected:
            return self.worker.write(data)
        return False

    def _on_connected(self):
        """连接成功回调"""
        self.is_connected = True
        self.connected.emit()

    def _on_disconnected(self):
        """断开连接回调"""
        self.is_connected = False
        self.disconnected.emit()

    def _on_worker_error(self, error_msg: str):
        """处理工作线程错误"""
        self.error_occurred.emit(error_msg)
        self.disconnect()

    def get_status(self) -> str:
        """
        获取连接状态

        Returns:
            状态字符串
        """
        if self.is_connected:
            return f"已连接到 {self.target_host}:{self.target_port}"
        return "未连接"
