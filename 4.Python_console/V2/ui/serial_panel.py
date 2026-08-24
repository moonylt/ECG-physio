# -*- coding: utf-8 -*-
"""
Serial Port Panel (Compact Version)
Provides serial port configuration and connection control in a single row
"""

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QMessageBox)
from PyQt5.QtCore import pyqtSignal

from comms.serial_manager import SerialManager


class SerialPanel(QWidget):
    """
    Serial Port Configuration Panel (Compact)
    All controls in a single horizontal row
    """

    # Signals
    connect_requested = pyqtSignal(str, int, int, int, str)
    disconnect_requested = pyqtSignal()
    sampling_rate_changed = pyqtSignal(int)

    def __init__(self, serial_manager: SerialManager, parent=None):
        super().__init__(parent)

        self.serial_manager = serial_manager

        # Connect signals
        self.serial_manager.connected.connect(self._on_connected)
        self.serial_manager.disconnected.connect(self._on_disconnected)
        self.serial_manager.error_occurred.connect(self._on_error)

        # Create UI
        self._init_ui()

        # Refresh port list
        self.refresh_ports()

    def _init_ui(self):
        """Initialize UI - single row layout"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(8)

        # Port
        layout.addWidget(QLabel("Port:"))
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(120)
        self.port_combo.setMaximumWidth(150)
        layout.addWidget(self.port_combo)

        # Refresh button
        self.refresh_btn = QPushButton("R")
        self.refresh_btn.setFixedWidth(25)
        self.refresh_btn.clicked.connect(self.refresh_ports)
        layout.addWidget(self.refresh_btn)

        # Separator
        layout.addWidget(QLabel("|"))

        # Baudrate
        layout.addWidget(QLabel("Baud:"))
        self.baud_combo = QComboBox()
        self.baud_combo.setMinimumWidth(80)
        self.baud_combo.setMaximumWidth(100)
        baud_rates = ['115200', '9600', '57600', '230400', '460800', '921600']
        self.baud_combo.addItems(baud_rates)
        layout.addWidget(self.baud_combo)

        # Sampling rate
        layout.addWidget(QLabel("SPS:"))
        self.sr_combo = QComboBox()
        self.sr_combo.setMinimumWidth(60)
        self.sr_combo.setMaximumWidth(80)
        sampling_rates = ['500', '250', '1000', '2000']
        self.sr_combo.addItems(sampling_rates)
        self.sr_combo.currentTextChanged.connect(lambda x: self.sampling_rate_changed.emit(int(x)))
        layout.addWidget(self.sr_combo)

        # Separator
        layout.addWidget(QLabel("|"))

        # Status label
        self.status_label = QLabel("Not connected")
        self.status_label.setStyleSheet("color: #666;")
        self.status_label.setFixedWidth(100)
        layout.addWidget(self.status_label)

        # Stretch
        layout.addStretch()

        # Connect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setFixedWidth(70)
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 4px 10px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #3d8b40; }
        """)
        self.connect_btn.clicked.connect(self._toggle_connection)
        layout.addWidget(self.connect_btn)

    def refresh_ports(self):
        """Refresh port list"""
        current = self.port_combo.currentText()
        self.port_combo.clear()

        ports = self.serial_manager.get_available_ports()
        port_info = self.serial_manager.get_port_info()

        if ports:
            self.port_combo.addItems(port_info)
            for i, info in enumerate(port_info):
                if current in info:
                    self.port_combo.setCurrentIndex(i)
                    break
        else:
            self.port_combo.addItem("No ports")

    def _toggle_connection(self):
        """Toggle connection state"""
        if self.serial_manager.is_connected:
            self.serial_manager.disconnect()
        else:
            port_info = self.port_combo.currentText()
            port = port_info.split(' - ')[0] if ' - ' in port_info else port_info

            if port == "No ports":
                QMessageBox.warning(self, "Warning", "No serial ports available!")
                return

            try:
                baudrate = int(self.baud_combo.currentText())
                # Fixed serial config: 8N1
                self.serial_manager.connect(port, baudrate, 8, 1, 'N')
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Connection failed: {str(e)}")

    def _on_connected(self):
        """Connected callback"""
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
        self.connect_btn.setText("Connect")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 4px 10px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.status_label.setText("Disconnected")
        self.status_label.setStyleSheet("color: #666;")
        self._set_controls_enabled(True)

    def _on_error(self, error_msg: str):
        """Error callback"""
        self._on_disconnected()
        QMessageBox.critical(self, "Serial Error", error_msg)

    def _set_controls_enabled(self, enabled: bool):
        """Set controls enabled state"""
        self.port_combo.setEnabled(enabled)
        self.baud_combo.setEnabled(enabled)
        self.sr_combo.setEnabled(enabled)
        self.refresh_btn.setEnabled(enabled)

    def get_connection_status(self) -> str:
        """Get connection status"""
        return self.serial_manager.get_status()