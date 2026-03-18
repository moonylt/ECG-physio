# -*- coding: utf-8 -*-
"""
串口配置面板
提供串口参数配置和连接控制
"""

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QGroupBox, QVBoxLayout,
                             QMessageBox)
from PyQt5.QtCore import pyqtSignal

from comms.serial_manager import SerialManager


class SerialPanel(QWidget):
    """
    串口配置面板
    """
    
    # 信号
    connect_requested = pyqtSignal(str, int, int, int, str)
    disconnect_requested = pyqtSignal()
    sampling_rate_changed = pyqtSignal(int)
    
    def __init__(self, serial_manager: SerialManager, parent=None):
        super().__init__(parent)
        
        self.serial_manager = serial_manager
        
        # 连接串口管理器信号
        self.serial_manager.connected.connect(self._on_connected)
        self.serial_manager.disconnected.connect(self._on_disconnected)
        self.serial_manager.error_occurred.connect(self._on_error)
        
        # 创建 UI
        self._init_ui()
        
        # 刷新端口列表
        self.refresh_ports()
    
    def _init_ui(self):
        """初始化 UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 端口选择
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("端口:"))
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(120)
        port_layout.addWidget(self.port_combo)
        
        # 波特率选择
        baud_layout = QHBoxLayout()
        baud_layout.addWidget(QLabel("波特率:"))
        self.baud_combo = QComboBox()
        self.baud_combo.setMinimumWidth(100)
        baud_rates = ['9600', '19200', '38400', '57600', '115200',
                      '230400', '460800', '921600']
        self.baud_combo.addItems(baud_rates)
        self.baud_combo.setCurrentText('115200')
        baud_layout.addWidget(self.baud_combo)

        # 采样率选择
        sr_layout = QHBoxLayout()
        sr_layout.addWidget(QLabel("采样率:"))
        self.sr_combo = QComboBox()
        self.sr_combo.setMinimumWidth(80)
        sampling_rates = ['250', '500', '1000', '2000']
        self.sr_combo.addItems(sampling_rates)
        self.sr_combo.setCurrentText('500')
        self.sr_combo.currentTextChanged.connect(lambda x: self.sampling_rate_changed.emit(int(x)))
        sr_layout.addWidget(self.sr_combo)
        
        # 数据位
        data_bits_layout = QHBoxLayout()
        data_bits_layout.addWidget(QLabel("数据位:"))
        self.data_bits_combo = QComboBox()
        self.data_bits_combo.addItems(['7', '8'])
        self.data_bits_combo.setCurrentText('8')
        self.data_bits_combo.setMaximumWidth(60)
        data_bits_layout.addWidget(self.data_bits_combo)
        
        # 停止位
        stop_bits_layout = QHBoxLayout()
        stop_bits_layout.addWidget(QLabel("停止位:"))
        self.stop_bits_combo = QComboBox()
        self.stop_bits_combo.addItems(['1', '2'])
        self.stop_bits_combo.setCurrentText('1')
        self.stop_bits_combo.setMaximumWidth(50)
        stop_bits_layout.addWidget(self.stop_bits_combo)
        
        # 校验位
        parity_layout = QHBoxLayout()
        parity_layout.addWidget(QLabel("校验:"))
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(['N', 'E', 'O'])
        self.parity_combo.setCurrentText('N')
        self.parity_combo.setMaximumWidth(50)
        parity_layout.addWidget(self.parity_combo)
        
        # 刷新按钮
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.setFixedWidth(60)
        self.refresh_btn.clicked.connect(self.refresh_ports)
        
        # 连接/断开按钮
        self.connect_btn = QPushButton("连接")
        self.connect_btn.setFixedWidth(80)
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.connect_btn.clicked.connect(self._toggle_connection)
        
        # 添加所有组件到主布局
        layout.addLayout(port_layout)
        layout.addLayout(baud_layout)
        layout.addLayout(sr_layout)
        layout.addLayout(data_bits_layout)
        layout.addLayout(stop_bits_layout)
        layout.addLayout(parity_layout)
        layout.addWidget(self.refresh_btn)
        layout.addStretch()
        layout.addWidget(self.connect_btn)
    
    def refresh_ports(self):
        """刷新串口列表"""
        current = self.port_combo.currentText()
        self.port_combo.clear()
        
        ports = self.serial_manager.get_available_ports()
        port_info = self.serial_manager.get_port_info()
        
        if ports:
            self.port_combo.addItems(port_info)
            # 尝试选择之前的端口
            for i, info in enumerate(port_info):
                if current in info:
                    self.port_combo.setCurrentIndex(i)
                    break
        else:
            self.port_combo.addItem("无可用串口")
    
    def _toggle_connection(self):
        """切换连接状态"""
        if self.serial_manager.is_connected:
            self.serial_manager.disconnect()
        else:
            # 获取当前配置
            port_info = self.port_combo.currentText()
            port = port_info.split(' - ')[0] if ' - ' in port_info else port_info
            
            if port == "无可用串口":
                QMessageBox.warning(self, "警告", "没有可用的串口！")
                return
            
            try:
                baudrate = int(self.baud_combo.currentText())
                data_bits = int(self.data_bits_combo.currentText())
                stop_bits = int(self.stop_bits_combo.currentText())
                parity = self.parity_combo.currentText()
                
                self.serial_manager.connect(port, baudrate, data_bits, stop_bits, parity)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"连接失败：{str(e)}")
    
    def _on_connected(self):
        """连接成功回调"""
        self.connect_btn.setText("断开")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        
        # 禁用配置控件
        self._set_controls_enabled(False)
    
    def _on_disconnected(self):
        """断开连接回调"""
        self.connect_btn.setText("连接")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        # 启用配置控件
        self._set_controls_enabled(True)
    
    def _on_error(self, error_msg: str):
        """错误回调"""
        QMessageBox.critical(self, "串口错误", error_msg)
        self._on_disconnected()
    
    def _set_controls_enabled(self, enabled: bool):
        """设置控件启用状态"""
        self.port_combo.setEnabled(enabled)
        self.baud_combo.setEnabled(enabled)
        self.sr_combo.setEnabled(enabled)
        self.data_bits_combo.setEnabled(enabled)
        self.stop_bits_combo.setEnabled(enabled)
        self.parity_combo.setEnabled(enabled)
        self.refresh_btn.setEnabled(enabled)
    
    def get_connection_status(self) -> str:
        """获取连接状态"""
        return self.serial_manager.get_status()
