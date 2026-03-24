# -*- coding: utf-8 -*-
"""
WiFi 连接面板
提供 WiFi 参数配置和连接控制
"""

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QGroupBox, QVBoxLayout,
                             QMessageBox, QLineEdit, QRadioButton)
from PyQt5.QtCore import pyqtSignal, QTimer

from comms.wifi_manager import WiFiManager


class WiFiPanel(QWidget):
    """
    WiFi 配置面板
    """

    # 信号
    connect_requested = pyqtSignal(str, int)
    disconnect_requested = pyqtSignal()

    def __init__(self, wifi_manager: WiFiManager, parent=None):
        super().__init__(parent)

        self.wifi_manager = wifi_manager

        # 连接 WiFi 管理器信号
        self.wifi_manager.connected.connect(self._on_connected)
        self.wifi_manager.disconnected.connect(self._on_disconnected)
        self.wifi_manager.error_occurred.connect(self._on_error)

        # 创建 UI
        self._init_ui()

        # 测试定时器
        self.test_timer = QTimer()
        self.test_timer.timeout.connect(self._on_test_timeout)

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # 连接模式选择
        mode_group = QGroupBox("连接模式")
        mode_layout = QHBoxLayout()

        self.esp32_ap_radio = QRadioButton("ESP32 AP 模式 (192.168.4.1)")
        self.esp32_ap_radio.setChecked(True)
        self.esp32_ap_radio.toggled.connect(self._on_mode_changed)

        self.custom_radio = QRadioButton("自定义 TCP 服务器")
        self.custom_radio.toggled.connect(self._on_mode_changed)

        mode_layout.addWidget(self.esp32_ap_radio)
        mode_layout.addWidget(self.custom_radio)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # IP 和端口配置
        config_group = QGroupBox("服务器配置")
        config_layout = QHBoxLayout()

        # IP 地址输入
        config_layout.addWidget(QLabel("IP 地址:"))
        self.ip_edit = QLineEdit("192.168.4.1")
        self.ip_edit.setFixedWidth(130)
        self.ip_edit.setEnabled(False)  # 默认禁用，ESP32 AP 模式下自动使用
        config_layout.addWidget(self.ip_edit)

        # 端口输入
        config_layout.addWidget(QLabel("端口:"))
        self.port_edit = QLineEdit("12345")
        self.port_edit.setFixedWidth(60)
        self.port_edit.setEnabled(False)
        config_layout.addWidget(self.port_edit)

        # 测试连接按钮
        self.test_btn = QPushButton("测试")
        self.test_btn.setFixedWidth(50)
        self.test_btn.clicked.connect(self._test_connection)
        config_layout.addWidget(self.test_btn)

        config_group.setLayout(config_layout)
        layout.addWidget(config_group)

        # 连接/断开按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.connect_btn = QPushButton("连接")
        self.connect_btn.setFixedWidth(100)
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        self.connect_btn.clicked.connect(self._toggle_connection)
        btn_layout.addWidget(self.connect_btn)

        layout.addLayout(btn_layout)

        # 状态标签
        self.status_label = QLabel("状态：未连接")
        self.status_label.setStyleSheet("color: #666;")
        layout.addWidget(self.status_label)

    def _on_mode_changed(self):
        """模式切换"""
        if self.esp32_ap_radio.isChecked():
            self.ip_edit.setEnabled(False)
            self.ip_edit.setText("192.168.4.1")
            self.port_edit.setEnabled(False)
            self.port_edit.setText("12345")
        else:
            self.ip_edit.setEnabled(True)
            self.port_edit.setEnabled(True)

    def _toggle_connection(self):
        """切换连接状态"""
        if self.wifi_manager.is_connected:
            self.wifi_manager.disconnect()
        else:
            # 获取配置
            if self.esp32_ap_radio.isChecked():
                ip = "192.168.4.1"
                port = 12345
            else:
                ip = self.ip_edit.text().strip()
                port_str = self.port_edit.text().strip()
                try:
                    port = int(port_str)
                except ValueError:
                    QMessageBox.warning(self, "警告", "端口号必须是数字！")
                    return

                if not ip:
                    QMessageBox.warning(self, "警告", "请输入 IP 地址！")
                    return

            self.connect_btn.setEnabled(False)
            self.connect_btn.setText("连接中...")

            # 异步连接
            success = self.wifi_manager.connect_to_custom(ip, port) if not self.esp32_ap_radio.isChecked() \
                else self.wifi_manager.connect_to_esp32()

            if not success:
                self.connect_btn.setEnabled(True)
                self.connect_btn.setText("连接")

    def _test_connection(self):
        """测试连接"""
        if self.esp32_ap_radio.isChecked():
            ip = "192.168.4.1"
            port = 12345
        else:
            ip = self.ip_edit.text().strip()
            try:
                port = int(self.port_edit.text().strip())
            except ValueError:
                QMessageBox.warning(self, "警告", "端口号必须是数字！")
                return

        if not ip:
            QMessageBox.warning(self, "警告", "请输入 IP 地址！")
            return

        self.test_btn.setEnabled(False)
        self.test_btn.setText("测试中...")
        self.status_label.setText("状态：正在测试连接...")

        # 在后台线程测试
        import threading
        def test_thread():
            result = self.wifi_manager.test_connection(ip, port)
            self.test_timer.singleShot(0, lambda: self._on_test_result(result, ip, port))

        threading.Thread(target=test_thread, daemon=True).start()

    def _on_test_timeout(self):
        """测试超时"""
        pass

    def _on_test_result(self, result: bool, ip: str, port: int):
        """测试结果回调"""
        self.test_btn.setEnabled(True)
        self.test_btn.setText("测试")

        if result:
            self.status_label.setText(f"状态：可连接到 {ip}:{port}")
            self.status_label.setStyleSheet("color: #4CAF50;")
            QMessageBox.information(
                self, "测试成功",
                f"可以连接到 {ip}:{port}\n请点击'连接'按钮建立连接"
            )
        else:
            self.status_label.setText(f"状态：无法连接到 {ip}:{port}")
            self.status_label.setStyleSheet("color: #f44336;")
            QMessageBox.warning(
                self, "测试失败",
                f"无法连接到 {ip}:{port}\n\n请检查:\n1. ESP32 是否已上电并运行固件\n2. 电脑是否已连接到 ESP32 热点\n3. IP 地址和端口是否正确"
            )

    def _on_connected(self):
        """连接成功回调"""
        self.connect_btn.setEnabled(True)
        self.connect_btn.setText("断开")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)

        self.status_label.setText(f"状态：已连接 - {self.wifi_manager.get_status()}")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")

        # 禁用配置
        self._set_controls_enabled(False)

    def _on_disconnected(self):
        """断开连接回调"""
        self.connect_btn.setEnabled(True)
        self.connect_btn.setText("连接")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)

        self.status_label.setText("状态：未连接")
        self.status_label.setStyleSheet("color: #666;")

        # 启用配置
        self._set_controls_enabled(True)

    def _on_error(self, error_msg: str):
        """错误回调"""
        self.connect_btn.setEnabled(True)
        self.connect_btn.setText("连接")
        self.status_label.setText(f"状态：错误 - {error_msg}")
        self.status_label.setStyleSheet("color: #f44336;")

        QMessageBox.critical(self, "WiFi 连接错误", error_msg)
        self._on_disconnected()

    def _set_controls_enabled(self, enabled: bool):
        """设置控件启用状态"""
        self.esp32_ap_radio.setEnabled(enabled)
        self.custom_radio.setEnabled(enabled)
        if not self.esp32_ap_radio.isChecked():
            self.ip_edit.setEnabled(enabled)
            self.port_edit.setEnabled(enabled)
        self.test_btn.setEnabled(enabled)

    def get_connection_status(self) -> str:
        """获取连接状态"""
        return self.wifi_manager.get_status()
