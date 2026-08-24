# -*- coding: utf-8 -*-
"""
串口管理模块
负责串口的打开、关闭、数据读取
"""

import sys
from PyQt5.QtCore import QObject, pyqtSignal, QThread

# 导入 pyserial 的 list_ports 模块
# 使用绝对导入避免与当前包名冲突
from serial.tools.list_ports import comports
import serial as pyserial


class SerialWorker(QThread):
    """
    串口工作线程
    在独立线程中运行，避免阻塞 UI
    """
    data_received = pyqtSignal(bytes)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, port: str, baudrate: int, data_bits: int, 
                 stop_bits: int, parity: str):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.data_bits = data_bits
        self.stop_bits = stop_bits
        self.parity = parity
        self.running = True
        self.serial = None
    
    def run(self):
        """线程运行函数"""
        try:
            # 映射参数
            parity_map = {
                'N': pyserial.PARITY_NONE,
                'E': pyserial.PARITY_EVEN,
                'O': pyserial.PARITY_ODD
            }
            stop_bits_map = {
                1: pyserial.STOPBITS_ONE,
                2: pyserial.STOPBITS_TWO
            }
            
            # 打开串口
            self.serial = pyserial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.data_bits,
                stopbits=stop_bits_map.get(self.stop_bits, pyserial.STOPBITS_ONE),
                parity=parity_map.get(self.parity, pyserial.PARITY_NONE),
                timeout=0.1
            )
            
            # 循环读取数据
            while self.running:
                if self.serial.in_waiting:
                    data = self.serial.read(self.serial.in_waiting)
                    self.data_received.emit(data)
                    
        except pyserial.SerialException as e:
            self.error_occurred.emit(f"串口错误：{str(e)}")
        except Exception as e:
            self.error_occurred.emit(f"未知错误：{str(e)}")
    
    def stop(self):
        """停止线程"""
        self.running = False
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.wait()
    
    def write(self, data: bytes):
        """发送数据"""
        if self.serial and self.serial.is_open:
            self.serial.write(data)


class SerialManager(QObject):
    """
    串口管理器
    提供串口连接、断开、数据收发等功能
    """
    data_received = pyqtSignal(bytes)
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.is_connected = False
    
    def get_available_ports(self) -> list:
        """
        获取可用串口列表
        
        Returns:
            串口名称列表，如 ['COM1', 'COM3']
        """
        ports = comports()
        return [p.device for p in ports]
    
    def get_port_info(self) -> list:
        """
        获取串口详细信息
        
        Returns:
            包含串口信息的列表
        """
        ports = comports()
        return [f"{p.device} - {p.description}" for p in ports]
    
    def connect(self, port: str, baudrate: int = 115200, 
                data_bits: int = 8, stop_bits: int = 1, 
                parity: str = 'N') -> bool:
        """
        连接串口
        
        Args:
            port: 串口名称，如 'COM3'
            baudrate: 波特率
            data_bits: 数据位 (7 或 8)
            stop_bits: 停止位 (1 或 2)
            parity: 校验位 ('N', 'E', 'O')
            
        Returns:
            True 如果连接成功，False 否则
        """
        if self.is_connected:
            self.disconnect()
        
        try:
            self.worker = SerialWorker(port, baudrate, data_bits, stop_bits, parity)
            self.worker.data_received.connect(self.data_received)
            self.worker.error_occurred.connect(self._on_worker_error)
            self.worker.start()
            
            # 等待线程启动
            self.worker.msleep(100)
            
            if self.worker.serial and self.worker.serial.is_open:
                self.is_connected = True
                self.connected.emit()
                return True
            else:
                return False
                
        except Exception as e:
            self.error_occurred.emit(f"连接失败：{str(e)}")
            return False
    
    def disconnect(self):
        """断开串口连接"""
        if self.worker:
            self.worker.stop()
            self.worker = None
        self.is_connected = False
        self.disconnected.emit()
    
    def write(self, data: bytes) -> bool:
        """
        发送数据
        
        Args:
            data: 要发送的数据
            
        Returns:
            True 如果发送成功
        """
        if self.worker and self.is_connected:
            self.worker.write(data)
            return True
        return False
    
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
        if self.is_connected and self.worker:
            return f"已连接 - {self.worker.port} @ {self.worker.baudrate}"
        return "未连接"
