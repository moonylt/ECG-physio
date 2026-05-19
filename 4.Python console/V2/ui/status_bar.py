# -*- coding: utf-8 -*-
"""
状态栏组件
显示系统状态、统计信息和生理参数
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QPushButton
from PyQt5.QtCore import QTimer, pyqtSignal
from typing import Optional


class StatusBar(QWidget):
    """
    状态栏组件
    显示心率、呼吸率、采样率、连接状态等信息
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)

        # 状态变量（在 _init_ui 之前初始化）
        self.heart_rate = 0
        self.breath_rate = 0
        self.sampling_rate = 500
        self.is_connected = False
        self.frames_received = 0
        self.bytes_received = 0
        self.error_count = 0

        # 创建 UI
        self._init_ui()

        # 状态更新定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(500)  # 500ms 刷新一次
    
    def _init_ui(self):
        """Initialize UI - compact status bar"""
        self.setStyleSheet("""
            StatusBar {
                background-color: #2d2d44;
                border-top: 1px solid #3d3d5c;
                padding: 2px;
            }
            QLabel {
                color: #ffffff;
                padding: 1px 5px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)

        # Heart rate (compact)
        self.hr_label = QLabel("HR: --")
        self.hr_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(self.hr_label)

        layout.addWidget(self._create_separator())

        # Breath rate (compact)
        self.br_label = QLabel("BR: --")
        self.br_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(self.br_label)

        layout.addWidget(self._create_separator())

        # Sampling rate (compact)
        self.sr_label = QLabel(f"SPS: {self.sampling_rate}")
        layout.addWidget(self.sr_label)

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
        """创建分隔线"""
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFixedWidth(1)
        line.setStyleSheet("background-color: #3d3d5c;")
        return line
    
    def set_heart_rate(self, bpm: float):
        """Set heart rate"""
        self.heart_rate = bpm
        if bpm > 0:
            self.hr_label.setText(f"HR: {bpm:.0f}")
            if 60 <= bpm <= 100:
                self.hr_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 12px;")
            elif bpm < 50 or bpm > 120:
                self.hr_label.setStyleSheet("color: #f44336; font-weight: bold; font-size: 12px;")
            else:
                self.hr_label.setStyleSheet("color: #ff9800; font-weight: bold; font-size: 12px;")
        else:
            self.hr_label.setText("HR: --")
            self.hr_label.setStyleSheet("font-weight: bold; font-size: 12px;")

    def set_breath_rate(self, rpm: float):
        """Set breath rate"""
        self.breath_rate = rpm
        if rpm > 0:
            self.br_label.setText(f"BR: {rpm:.1f}")
            if 12 <= rpm <= 20:
                self.br_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 12px;")
            elif rpm < 10 or rpm > 30:
                self.br_label.setStyleSheet("color: #f44336; font-weight: bold; font-size: 12px;")
            else:
                self.br_label.setStyleSheet("color: #ff9800; font-weight: bold; font-size: 12px;")
        else:
            self.br_label.setText("BR: --")
            self.br_label.setStyleSheet("font-weight: bold; font-size: 12px;")

    def set_sampling_rate(self, rate: int):
        """Set sampling rate"""
        self.sampling_rate = rate
        self.sr_label.setText(f"SPS: {rate}")

    def set_connected(self, connected: bool):
        """Set connection status"""
        self.is_connected = connected
        if connected:
            self.status_indicator.setText("Online")
            self.status_indicator.setStyleSheet("color: #4CAF50;")
        else:
            self.status_indicator.setText("Offline")
            self.status_indicator.setStyleSheet("color: #9e9e9e;")

    def update_stats(self, frames: int, bytes_count: int, errors: int = 0):
        """Update statistics"""
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
        """定期更新显示"""
        # 可以在这里添加自动刷新逻辑
        pass
    
    def reset(self):
        """重置状态栏"""
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
