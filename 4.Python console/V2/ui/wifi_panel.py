# -*- coding: utf-8 -*-
"""
WiFi Connection Panel (Compact Version)
Provides WiFi device discovery and TCP connection control in a single row
"""

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QMessageBox,
                             QLineEdit, QApplication)
from PyQt5.QtCore import pyqtSignal, QTimer

from comms.wifi_manager import WiFiManager


class WiFiPanel(QWidget):
    """
    WiFi Configuration Panel (Compact)
    All controls in a single horizontal row
    """

    # Signals
    connect_requested = pyqtSignal(str, int)
    disconnect_requested = pyqtSignal()

    def __init__(self, wifi_manager: WiFiManager, parent=None):
        super().__init__(parent)

        self.wifi_manager = wifi_manager

        # Connect WiFi manager signals
        self.wifi_manager.connected.connect(self._on_connected)
        self.wifi_manager.disconnected.connect(self._on_disconnected)
        self.wifi_manager.error_occurred.connect(self._on_error)
        self.wifi_manager.devices_found.connect(self._on_devices_found)

        # Create UI
        self._init_ui()

        # Timers
        self.wifi_status_timer = QTimer()
        self.wifi_status_timer.timeout.connect(self._update_wifi_status)
        self.wifi_status_timer.start(5000)

    def _init_ui(self):
        """Initialize UI - single row layout"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(8)

        # Scan button
        self.scan_btn = QPushButton("Scan")
        self.scan_btn.setFixedWidth(50)
        self.scan_btn.clicked.connect(self._scan_devices)
        layout.addWidget(self.scan_btn)

        # Device list
        self.device_combo = QComboBox()
        self.device_combo.setMinimumWidth(180)
        self.device_combo.setMaximumWidth(250)
        self.device_combo.addItem("Click Scan")
        self.device_combo.currentIndexChanged.connect(self._on_device_selected)
        layout.addWidget(self.device_combo)

        # Separator
        layout.addWidget(QLabel("|"))

        # IP
        layout.addWidget(QLabel("IP:"))
        self.ip_edit = QLineEdit("192.168.4.1")
        self.ip_edit.setFixedWidth(100)
        layout.addWidget(self.ip_edit)

        # Port
        layout.addWidget(QLabel("Port:"))
        self.port_edit = QLineEdit("12345")
        self.port_edit.setFixedWidth(50)
        layout.addWidget(self.port_edit)

        # Test button
        self.test_btn = QPushButton("Test")
        self.test_btn.setFixedWidth(40)
        self.test_btn.clicked.connect(self._test_connection)
        layout.addWidget(self.test_btn)

        # Status label (compact)
        self.status_label = QLabel("Not connected")
        self.status_label.setStyleSheet("color: #666;")
        self.status_label.setFixedWidth(120)
        layout.addWidget(self.status_label)

        # Stretch
        layout.addStretch()

        # Connect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setFixedWidth(70)
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 4px 10px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1976D2; }
            QPushButton:pressed { background-color: #0D47A1; }
        """)
        self.connect_btn.clicked.connect(self._toggle_connection)
        layout.addWidget(self.connect_btn)

        # Initial status update
        self._update_wifi_status()

    # ==================== Device Discovery ====================

    def _scan_devices(self):
        """Scan for ECG devices"""
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("...")
        self.device_combo.clear()
        self.device_combo.addItem("Scanning...")
        self.wifi_manager.scan_esp32_devices_async()

    def _on_devices_found(self, devices: list):
        """Devices found callback"""
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("Scan")
        self.device_combo.clear()

        if devices:
            for d in devices:
                self.device_combo.addItem(f"{d['ssid']} ({d['signal']}%)", d)
        else:
            self.device_combo.addItem("No devices")

    def _on_device_selected(self, index: int):
        """Device selected callback"""
        device_data = self.device_combo.currentData()
        if device_data:
            self.status_label.setText(f"Found: {device_data['ssid']}")
            self.status_label.setStyleSheet("color: #4CAF50;")

    # ==================== WiFi Status ====================

    def _update_wifi_status(self):
        """Update WiFi connection status"""
        conn = self.wifi_manager.get_current_wifi_connection()
        ssid = conn.get('ssid', '')

        if ssid.startswith("ECG-Physio"):
            self.status_label.setText(f"WiFi: {ssid}")
            self.status_label.setStyleSheet("color: #4CAF50;")
        elif ssid:
            self.status_label.setText(f"WiFi: {ssid}")
            self.status_label.setStyleSheet("color: #FF9800;")
        else:
            if not self.wifi_manager.is_connected:
                self.status_label.setText("No WiFi")
                self.status_label.setStyleSheet("color: #666;")

    # ==================== TCP Connection ====================

    def _test_connection(self):
        """Test TCP connection"""
        ip = self.ip_edit.text().strip()
        try:
            port = int(self.port_edit.text().strip())
        except ValueError:
            return

        self.test_btn.setEnabled(False)
        self.test_btn.setText("..")

        import threading
        def test_thread():
            result = self.wifi_manager.test_connection(ip, port)
            QApplication.processEvents()
            self.test_timer_singleShot(0, lambda: self._on_test_result(result))

        threading.Thread(target=test_thread, daemon=True).start()

    def test_timer_singleShot(self, ms, callback):
        """Helper for single shot timer"""
        QTimer.singleShot(ms, callback)

    def _on_test_result(self, result: bool):
        """Test result callback"""
        self.test_btn.setEnabled(True)
        self.test_btn.setText("Test")
        if result:
            self.status_label.setText("Reachable")
            self.status_label.setStyleSheet("color: #4CAF50;")
        else:
            self.status_label.setText("Unreachable")
            self.status_label.setStyleSheet("color: #f44336;")

    def _toggle_connection(self):
        """Toggle connection state"""
        if self.wifi_manager.is_connected:
            self.wifi_manager.disconnect()
        else:
            ip = self.ip_edit.text().strip()
            try:
                port = int(self.port_edit.text().strip())
            except ValueError:
                return

            self.connect_btn.setEnabled(False)
            self.connect_btn.setText("...")
            self.wifi_manager.connect_to_custom(ip, port)

    def _on_connected(self):
        """Connected callback"""
        self.connect_btn.setEnabled(True)
        self.connect_btn.setText("Disconnect")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 4px 10px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #da190b; }
        """)
        self.status_label.setText("Connected")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        self._set_controls_enabled(False)

    def _on_disconnected(self):
        """Disconnected callback"""
        self.connect_btn.setEnabled(True)
        self.connect_btn.setText("Connect")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 4px 10px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        self.status_label.setText("Disconnected")
        self.status_label.setStyleSheet("color: #666;")
        self._set_controls_enabled(True)

    def _on_error(self, error_msg: str):
        """Error callback"""
        self.connect_btn.setEnabled(True)
        self.connect_btn.setText("Connect")
        self.status_label.setText(f"Error")
        self.status_label.setStyleSheet("color: #f44336;")
        self._on_disconnected()

    def _set_controls_enabled(self, enabled: bool):
        """Set controls enabled state"""
        self.scan_btn.setEnabled(enabled)
        self.device_combo.setEnabled(enabled)
        self.ip_edit.setEnabled(enabled)
        self.port_edit.setEnabled(enabled)
        self.test_btn.setEnabled(enabled)
        if enabled:
            self.wifi_status_timer.start(5000)
        else:
            self.wifi_status_timer.stop()

    def get_connection_status(self) -> str:
        """Get connection status"""
        return self.wifi_manager.get_status()