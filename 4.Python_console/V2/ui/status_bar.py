# -*- coding: utf-8 -*-
"""
Status bar widget.
Shows system status, statistics and physiological parameters.
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QPushButton
from PyQt5.QtCore import QTimer, pyqtSignal, Qt
from typing import Optional


class StatusBar(QWidget):
    """
    Status bar: heart rate, breath rate, sampling rate, connection state.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # A QWidget subclass must opt in or the stylesheet background is not
        # painted (white text on a light background would be unreadable)
        self.setAttribute(Qt.WA_StyledBackground, True)

        # state variables (initialize before _init_ui)
        self.heart_rate = 0
        self.breath_rate = 0
        self.sampling_rate = 500
        self.is_connected = False
        self.frames_received = 0
        self.bytes_received = 0
        self.error_count = 0
        self.tcp_client = None   # injected via attach_tcp_client for downlink commands

        # build the UI
        self._init_ui()

        # status refresh timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(500)  # refresh every 500ms
    
    def _init_ui(self):
        """Initialize UI - compact status bar."""
        self.setStyleSheet("""
            StatusBar {
                background-color: #2d2d44;
                border-top: 1px solid #3d3d5c;
                padding: 2px;
            }
            QLabel {
                color: #e8eaf6;
                padding: 1px 6px;
                font-size: 13px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)

        # Heart rate (compact)
        self.hr_label = QLabel("HR: --")
        self.hr_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(self.hr_label)

        layout.addWidget(self._create_separator())

        # Breath rate (compact)
        self.br_label = QLabel("BR: --")
        self.br_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(self.br_label)

        layout.addWidget(self._create_separator())

        # Sampling rate (compact)
        self.sr_label = QLabel(f"SPS: {self.sampling_rate}")
        layout.addWidget(self.sr_label)

        layout.addWidget(self._create_separator())

        # SpO2 (MSGID 0x22)
        self.spo2_label = QLabel("SpO2: --")
        self.spo2_label.setStyleSheet("color: #80deea; font-weight: bold; font-size: 13px;")
        layout.addWidget(self.spo2_label)

        layout.addWidget(self._create_separator())

        # Temperatures (MSGID 0x25)
        self.temp_label = QLabel("T: --")
        self.temp_label.setStyleSheet("color: #80deea; font-weight: bold; font-size: 13px;")
        layout.addWidget(self.temp_label)

        layout.addWidget(self._create_separator())

        # Heater setpoint control (downlink 0xA1)
        from PyQt5.QtWidgets import QDoubleSpinBox
        self.target_spin = QDoubleSpinBox()
        self.target_spin.setRange(20.0, 60.0)
        self.target_spin.setDecimals(1)
        self.target_spin.setSingleStep(0.5)
        self.target_spin.setValue(38.0)
        self.target_spin.setStyleSheet("color: #ffb74d; font-size: 13px; background: transparent;")
        self.target_spin.setFixedWidth(64)
        self.target_btn = QPushButton("Set")
        self.target_btn.setFixedHeight(22)
        self.target_btn.clicked.connect(self._on_set_target)
        layout.addWidget(QLabel("Set:"))
        layout.addWidget(self.target_spin)
        layout.addWidget(self.target_btn)

        layout.addWidget(self._create_separator())

        # Connection status
        self.status_indicator = QLabel("Offline")
        self.status_indicator.setStyleSheet("color: #9e9e9e;")
        layout.addWidget(self.status_indicator)

        layout.addStretch()

        # Stats (compact)
        self.stats_label = QLabel("Rx: 0")
        layout.addWidget(self.stats_label)

        # Errors
        self.error_label = QLabel("Err: 0")
        layout.addWidget(self.error_label)
    
    def _create_separator(self) -> QFrame:
        """Create a separator line."""
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFixedWidth(1)
        line.setStyleSheet("background-color: #3d3d5c;")
        return line

    def _on_set_target(self):
        """Set 按钮：下发 0xA1 目标温度（tcp_client 引用由 main_window 注入）"""
        if self.tcp_client is not None:
            self.tcp_client.send_set_temp_target(float(self.target_spin.value()))

    def attach_tcp_client(self, tcp_client):
        """注入 TCP 客户端以启用下行命令"""
        self.tcp_client = tcp_client
    
    def set_heart_rate(self, bpm: float):
        """Set heart rate."""
        self.heart_rate = bpm
        if bpm > 0:
            self.hr_label.setText(f"HR: {bpm:.0f}")
            if 60 <= bpm <= 100:
                self.hr_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 13px;")
            elif bpm < 50 or bpm > 120:
                self.hr_label.setStyleSheet("color: #f44336; font-weight: bold; font-size: 13px;")
            else:
                self.hr_label.setStyleSheet("color: #ff9800; font-weight: bold; font-size: 13px;")
        else:
            self.hr_label.setText("HR: --")
            self.hr_label.setStyleSheet("font-weight: bold; font-size: 13px;")

    def set_breath_rate(self, rpm: float):
        """Set breath rate."""
        self.breath_rate = rpm
        if rpm > 0:
            self.br_label.setText(f"BR: {rpm:.1f}")
            if 12 <= rpm <= 20:
                self.br_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 13px;")
            elif rpm < 10 or rpm > 30:
                self.br_label.setStyleSheet("color: #f44336; font-weight: bold; font-size: 13px;")
            else:
                self.br_label.setStyleSheet("color: #ff9800; font-weight: bold; font-size: 13px;")
        else:
            self.br_label.setText("BR: --")
            self.br_label.setStyleSheet("font-weight: bold; font-size: 13px;")

    def set_sampling_rate(self, rate: int):
        """Set sampling rate."""
        self.sampling_rate = rate
        self.sr_label.setText(f"SPS: {rate}")

    def set_spo2(self, spo2: float, pulse_rate: int = 0):
        """Set SpO2 (MSGID 0x22)."""
        if spo2 > 0:
            text = f"SpO2: {spo2:.0f}%"
            if pulse_rate > 0:
                text += f" ({pulse_rate})"
            self.spo2_label.setText(text)
            color = "#4CAF50" if spo2 >= 95 else ("#ff9800" if spo2 >= 90 else "#f44336")
            self.spo2_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 13px;")
        else:
            self.spo2_label.setText("SpO2: --")
            self.spo2_label.setStyleSheet("color: #80deea; font-weight: bold; font-size: 13px;")

    def set_temperatures(self, t_skin: float = None, t_rect: float = None, t_heater: float = None):
        """Set temperatures (MSGID 0x25)."""
        parts = []
        if t_skin is not None:
            parts.append(f"sk {t_skin:.1f}")
        if t_rect is not None:
            parts.append(f"rc {t_rect:.1f}")
        if t_heater is not None:
            parts.append(f"ht {t_heater:.1f}")
        if parts:
            self.temp_label.setText("T: " + "/".join(parts) + " C")
        else:
            self.temp_label.setText("T: --")

    def set_connected(self, connected: bool):
        """Set connection status."""
        self.is_connected = connected
        if connected:
            self.status_indicator.setText("Online")
            self.status_indicator.setStyleSheet("color: #4CAF50;")
        else:
            self.status_indicator.setText("Offline")
            self.status_indicator.setStyleSheet("color: #9e9e9e;")

    def update_stats(self, frames: int, bytes_count: int, errors: int = 0):
        """Update statistics."""
        self.frames_received = frames
        self.bytes_received = bytes_count
        self.error_count = errors

        if frames >= 1000:
            frames_str = f"{frames/1000:.1f}k"
        else:
            frames_str = str(frames)

        self.stats_label.setText(f"Rx: {frames_str}")

        if errors > 0:
            self.error_label.setText(f"Err: {errors}")
            self.error_label.setStyleSheet("color: #f44336;")
        else:
            self.error_label.setText("Err: 0")
            self.error_label.setStyleSheet("color: #4CAF50;")
    
    def _update_display(self):
        """Periodic display refresh."""
        # 可以在这里添加自动刷新逻辑
        pass
    
    def reset(self):
        """Reset the status bar."""
        self.set_heart_rate(0)
        self.set_breath_rate(0)
        self.update_stats(0, 0, 0)
        self.set_connected(False)


class ControlPanel(QWidget):
    """
    工具控制面板
    包含保存、截图、暂停、滤波等控制按钮
    """

    # 信号
    save_csv_requested = pyqtSignal()
    save_edf_requested = pyqtSignal()
    save_mat_requested = pyqtSignal()
    export_report_requested = pyqtSignal()
    screenshot_requested = pyqtSignal()
    pause_toggled = pyqtSignal(bool)
    filter_toggled = pyqtSignal(bool)
    clear_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize UI - compact control panel"""
        self.setStyleSheet("""
            ControlPanel {
                background-color: #2d2d44;
                border-bottom: 1px solid #3d3d5c;
                padding: 2px;
            }
            QPushButton {
                background-color: #3d3d5c;
                color: white;
                border: none;
                padding: 3px 8px;
                border-radius: 2px;
                margin: 0 1px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #4d4d6c; }
            QPushButton:pressed { background-color: #2d2d44; }
            QPushButton:checked { background-color: #4CAF50; }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(3)

        # Save button with dropdown
        from PyQt5.QtWidgets import QMenu
        save_menu = QMenu()
        save_menu.addAction("CSV", lambda: self.save_csv_requested.emit())
        save_menu.addAction("EDF", lambda: self.save_edf_requested.emit())
        save_menu.addAction("MAT", lambda: self.save_mat_requested.emit())
        save_menu.addAction("Report", lambda: self.export_report_requested.emit())

        self.save_btn = QPushButton("Export")
        self.save_btn.setMenu(save_menu)
        layout.addWidget(self.save_btn)

        # Screenshot
        self.screenshot_btn = QPushButton("Screenshot")
        self.screenshot_btn.clicked.connect(lambda: self.screenshot_requested.emit())
        layout.addWidget(self.screenshot_btn)

        # Pause
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setCheckable(True)
        self.pause_btn.toggled.connect(lambda: self.pause_toggled.emit(self.pause_btn.isChecked()))
        layout.addWidget(self.pause_btn)

        # Filter
        self.filter_btn = QPushButton("Filter")
        self.filter_btn.setCheckable(True)
        self.filter_btn.setChecked(True)
        self.filter_btn.toggled.connect(self._on_filter_toggled)
        layout.addWidget(self.filter_btn)

        layout.addStretch()

        # Clear
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(lambda: self.clear_requested.emit())
        layout.addWidget(self.clear_btn)

    def _on_filter_toggled(self, checked: bool):
        """Filter toggle"""
        self.filter_toggled.emit(checked)
