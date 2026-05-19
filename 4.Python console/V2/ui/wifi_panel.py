# -*- coding: utf-8 -*-
"""
WiFi Connection Panel
Provides WiFi device discovery and TCP connection control
"""

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QGroupBox, QVBoxLayout,
                             QMessageBox, QLineEdit, QApplication)
from PyQt5.QtCore import pyqtSignal, QTimer

from comms.wifi_manager import WiFiManager


class WiFiPanel(QWidget):
    """
    WiFi Configuration Panel
    Supports device discovery via WiFi AP scanning
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
        self.test_timer = QTimer()
        self.test_timer.timeout.connect(self._on_test_timeout)

        self.wifi_status_timer = QTimer()
        self.wifi_status_timer.timeout.connect(self._update_wifi_status)

        # Start WiFi status update timer (reduce frequency to avoid lag)
        self.wifi_status_timer.start(5000)  # Update every 5 seconds

    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # ==================== Device Discovery Section ====================
        discovery_group = QGroupBox("Device Discovery")
        discovery_layout = QVBoxLayout()

        # Scan button
        scan_btn_layout = QHBoxLayout()
        self.scan_btn = QPushButton("Scan Devices")
        self.scan_btn.setFixedWidth(120)
        self.scan_btn.clicked.connect(self._scan_devices)
        scan_btn_layout.addWidget(self.scan_btn)
        scan_btn_layout.addStretch()
        discovery_layout.addLayout(scan_btn_layout)

        # Device list
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("ECG Devices:"))
        self.device_combo = QComboBox()
        self.device_combo.setMinimumWidth(200)
        self.device_combo.addItem("Click 'Scan' to find devices")
        self.device_combo.currentIndexChanged.connect(self._on_device_selected)
        device_layout.addWidget(self.device_combo)
        discovery_layout.addLayout(device_layout)

        # Device info label
        self.device_info_label = QLabel("")
        self.device_info_label.setStyleSheet("color: #666; font-size: 11px;")
        discovery_layout.addWidget(self.device_info_label)

        discovery_group.setLayout(discovery_layout)
        layout.addWidget(discovery_group)

        # ==================== WiFi Status Section ====================
        wifi_status_group = QGroupBox("WiFi Status")
        wifi_status_layout = QVBoxLayout()

        # Current WiFi connection
        self.wifi_status_label = QLabel("Current WiFi: Checking...")
        self.wifi_status_label.setStyleSheet("color: #666;")
        wifi_status_layout.addWidget(self.wifi_status_label)

        # ECG connection status
        self.ecg_ap_status_label = QLabel("ECG AP: Not connected")
        self.ecg_ap_status_label.setStyleSheet("color: #f44336;")
        wifi_status_layout.addWidget(self.ecg_ap_status_label)

        # Hint label
        self.hint_label = QLabel("Hint: Use system WiFi settings to connect to 'ECG-Physio' AP")
        self.hint_label.setStyleSheet("color: #2196F3; font-size: 11px;")
        wifi_status_layout.addWidget(self.hint_label)

        wifi_status_group.setLayout(wifi_status_layout)
        layout.addWidget(wifi_status_group)

        # ==================== TCP Connection Section ====================
        tcp_group = QGroupBox("TCP Connection")
        tcp_layout = QVBoxLayout()

        # IP/Port row
        config_layout = QHBoxLayout()
        config_layout.addWidget(QLabel("IP:"))
        self.ip_edit = QLineEdit("192.168.4.1")
        self.ip_edit.setFixedWidth(130)
        self.ip_edit.setEnabled(True)  # Allow manual input for custom cases
        config_layout.addWidget(self.ip_edit)

        config_layout.addWidget(QLabel("Port:"))
        self.port_edit = QLineEdit("12345")
        self.port_edit.setFixedWidth(60)
        config_layout.addWidget(self.port_edit)

        config_layout.addStretch()
        tcp_layout.addLayout(config_layout)

        # Buttons row
        btn_layout = QHBoxLayout()

        self.test_btn = QPushButton("Test")
        self.test_btn.setFixedWidth(60)
        self.test_btn.clicked.connect(self._test_connection)
        btn_layout.addWidget(self.test_btn)

        btn_layout.addStretch()

        self.connect_btn = QPushButton("Connect")
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

        tcp_layout.addLayout(btn_layout)

        # Status label
        self.tcp_status_label = QLabel("Status: Not connected")
        self.tcp_status_label.setStyleSheet("color: #666;")
        tcp_layout.addWidget(self.tcp_status_label)

        tcp_group.setLayout(tcp_layout)
        layout.addWidget(tcp_group)

        # Initial WiFi status update
        self._update_wifi_status()

    # ==================== Device Discovery ====================

    def _scan_devices(self):
        """Scan for ECG devices"""
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("Scanning...")
        self.device_combo.clear()
        self.device_combo.addItem("Scanning...")

        # Use async scan
        self.wifi_manager.scan_esp32_devices_async()

    def _on_devices_found(self, devices: list):
        """Devices found callback"""
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("Scan Devices")
        self.device_combo.clear()

        if devices:
            for d in devices:
                signal_text = f"{d['signal']}%"
                self.device_combo.addItem(f"{d['ssid']} ({signal_text})", d)

            self.device_info_label.setText(f"Found {len(devices)} ECG-Physio device(s)")
            self.device_info_label.setStyleSheet("color: #4CAF50; font-size: 11px;")
        else:
            self.device_combo.addItem("No ECG devices found")
            self.device_info_label.setText("Make sure ESP32 is powered on")
            self.device_info_label.setStyleSheet("color: #f44336; font-size: 11px;")
            QMessageBox.information(
                self, "No Devices Found",
                "No ECG-Physio devices found.\n\n"
                "Please check:\n"
                "• ESP32 is powered on\n"
                "• ESP32 firmware is running\n"
                "• WiFi AP 'ECG-Physio' is active"
            )

    def _on_device_selected(self, index: int):
        """Device selected callback"""
        if index < 0:
            return

        device_data = self.device_combo.currentData()
        if device_data:
            # Update device info label
            bssid = device_data.get('bssid', 'Unknown')
            channel = device_data.get('channel', 'Unknown')
            security = device_data.get('security', 'Unknown')
            self.device_info_label.setText(f"MAC: {bssid} | Channel: {channel} | Security: {security}")
            self.device_info_label.setStyleSheet("color: #4CAF50; font-size: 11px;")

    # ==================== WiFi Status ====================

    def _update_wifi_status(self):
        """Update WiFi connection status"""
        conn = self.wifi_manager.get_current_wifi_connection()
        ssid = conn.get('ssid', '')
        connected = conn.get('connected', False)

        if connected and ssid:
            self.wifi_status_label.setText(f"Current WiFi: {ssid}")
            self.wifi_status_label.setStyleSheet("color: #4CAF50;")

            # Check if connected to ECG AP
            if ssid.startswith("ECG-Physio"):
                self.ecg_ap_status_label.setText("ECG AP: Connected")
                self.ecg_ap_status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
                self.hint_label.setText("Ready to connect! Click 'Connect' button")
                self.hint_label.setStyleSheet("color: #4CAF50; font-size: 11px;")
            else:
                self.ecg_ap_status_label.setText("ECG AP: Not connected (connected to other WiFi)")
                self.ecg_ap_status_label.setStyleSheet("color: #f44336;")
                self.hint_label.setText("Please disconnect current WiFi and connect to 'ECG-Physio' AP")
                self.hint_label.setStyleSheet("color: #FF9800; font-size: 11px;")
        else:
            self.wifi_status_label.setText("Current WiFi: Not connected")
            self.wifi_status_label.setStyleSheet("color: #666;")
            self.ecg_ap_status_label.setText("ECG AP: Not connected")
            self.ecg_ap_status_label.setStyleSheet("color: #f44336;")
            self.hint_label.setText("Hint: Use system WiFi settings to connect to 'ECG-Physio' AP")
            self.hint_label.setStyleSheet("color: #2196F3; font-size: 11px;")

    # ==================== TCP Connection ====================

    def _test_connection(self):
        """Test TCP connection"""
        ip = self.ip_edit.text().strip()
        try:
            port = int(self.port_edit.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Warning", "Port must be a number!")
            return

        if not ip:
            QMessageBox.warning(self, "Warning", "Please enter IP address!")
            return

        self.test_btn.setEnabled(False)
        self.test_btn.setText("Testing...")
        self.tcp_status_label.setText("Status: Testing connection...")
        self.tcp_status_label.setStyleSheet("color: #2196F3;")

        # Test in background thread
        import threading
        def test_thread():
            result = self.wifi_manager.test_connection(ip, port)
            QApplication.processEvents()
            self.test_timer.singleShot(0, lambda: self._on_test_result(result, ip, port))

        threading.Thread(target=test_thread, daemon=True).start()

    def _on_test_timeout(self):
        """Test timeout"""
        pass

    def _on_test_result(self, result: bool, ip: str, port: int):
        """Test result callback"""
        self.test_btn.setEnabled(True)
        self.test_btn.setText("Test")

        if result:
            self.tcp_status_label.setText(f"Status: Can connect to {ip}:{port}")
            self.tcp_status_label.setStyleSheet("color: #4CAF50;")
            QMessageBox.information(
                self, "Test Success",
                f"Can connect to {ip}:{port}\n\nClick 'Connect' to establish connection"
            )
        else:
            self.tcp_status_label.setText(f"Status: Cannot connect to {ip}:{port}")
            self.tcp_status_label.setStyleSheet("color: #f44336;")
            QMessageBox.warning(
                self, "Test Failed",
                f"Cannot connect to {ip}:{port}\n\n"
                "Please check:\n"
                "• ESP32 is powered on\n"
                "• Computer is connected to 'ECG-Physio' WiFi AP\n"
                "• IP and port are correct"
            )

    def _toggle_connection(self):
        """Toggle connection state"""
        if self.wifi_manager.is_connected:
            self.wifi_manager.disconnect()
        else:
            # Check WiFi connection first
            if not self.wifi_manager.is_connected_to_ecg_ap():
                conn = self.wifi_manager.get_current_wifi_connection()
                current_ssid = conn.get('ssid', '')

                reply = QMessageBox.question(
                    self, "WiFi Not Connected",
                    f"You are currently connected to: {current_ssid or 'No WiFi'}\n\n"
                    "Please connect to 'ECG-Physio' WiFi AP first.\n\n"
                    "Continue anyway?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if reply == QMessageBox.No:
                    return

            # Get IP and port
            ip = self.ip_edit.text().strip()
            try:
                port = int(self.port_edit.text().strip())
            except ValueError:
                QMessageBox.warning(self, "Warning", "Port must be a number!")
                return

            if not ip:
                QMessageBox.warning(self, "Warning", "Please enter IP address!")
                return

            self.connect_btn.setEnabled(False)
            self.connect_btn.setText("Connecting...")
            self.tcp_status_label.setText("Status: Connecting...")
            self.tcp_status_label.setStyleSheet("color: #2196F3;")

            # Connect
            success = self.wifi_manager.connect_to_custom(ip, port)

            if not success:
                self.connect_btn.setEnabled(True)
                self.connect_btn.setText("Connect")

    def _on_connected(self):
        """Connected callback"""
        self.connect_btn.setEnabled(True)
        self.connect_btn.setText("Disconnect")
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

        self.tcp_status_label.setText(f"Status: Connected - {self.wifi_manager.get_status()}")
        self.tcp_status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")

        # Disable controls
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
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)

        self.tcp_status_label.setText("Status: Not connected")
        self.tcp_status_label.setStyleSheet("color: #666;")

        # Enable controls
        self._set_controls_enabled(True)

    def _on_error(self, error_msg: str):
        """Error callback"""
        self.connect_btn.setEnabled(True)
        self.connect_btn.setText("Connect")
        self.tcp_status_label.setText(f"Status: Error - {error_msg}")
        self.tcp_status_label.setStyleSheet("color: #f44336;")

        QMessageBox.critical(self, "WiFi Connection Error", error_msg)
        self._on_disconnected()

    def _set_controls_enabled(self, enabled: bool):
        """Set controls enabled state"""
        self.scan_btn.setEnabled(enabled)
        self.device_combo.setEnabled(enabled)
        self.ip_edit.setEnabled(enabled)
        self.port_edit.setEnabled(enabled)
        self.test_btn.setEnabled(enabled)

        # Stop WiFi status timer when connected (avoid lag during data streaming)
        if enabled:
            self.wifi_status_timer.start(5000)
        else:
            self.wifi_status_timer.stop()

    def get_connection_status(self) -> str:
        """Get connection status"""
        return self.wifi_manager.get_status()