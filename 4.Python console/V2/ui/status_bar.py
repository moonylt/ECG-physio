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
        """初始化 UI"""
        self.setStyleSheet("""
            StatusBar {
                background-color: #2d2d44;
                border-top: 1px solid #3d3d5c;
                padding: 5px;
            }
            QLabel {
                color: #ffffff;
                padding: 2px 10px;
            }
            .highlight {
                color: #4CAF50;
                font-weight: bold;
            }
            .warning {
                color: #ff9800;
            }
            .error {
                color: #f44336;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 心率显示
        self.hr_label = QLabel("♥ 心率：-- BPM")
        self.hr_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(self.hr_label)
        
        # 分隔线
        layout.addWidget(self._create_separator())
        
        # 呼吸率显示
        self.br_label = QLabel("🫁 呼吸：-- RPM")
        self.br_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(self.br_label)
        
        # 分隔线
        layout.addWidget(self._create_separator())
        
        # 采样率显示
        self.sr_label = QLabel(f"📊 采样率：{self.sampling_rate} SPS")
        layout.addWidget(self.sr_label)
        
        # 分隔线
        layout.addWidget(self._create_separator())
        
        # 连接状态
        self.status_indicator = QLabel("● 未连接")
        self.status_indicator.setStyleSheet("color: #9e9e9e;")
        layout.addWidget(self.status_indicator)
        
        layout.addStretch()
        
        # 接收统计
        self.stats_label = "📥 接收：0 帧 | 0 B"
        self.stats_label = QLabel(self.stats_label)
        layout.addWidget(self.stats_label)
        
        # 错误计数
        self.error_label = QLabel("⚠ 错误：0")
        layout.addWidget(self.error_label)
    
    def _create_separator(self) -> QFrame:
        """创建分隔线"""
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFixedWidth(1)
        line.setStyleSheet("background-color: #3d3d5c;")
        return line
    
    def set_heart_rate(self, bpm: float):
        """设置心率值"""
        self.heart_rate = bpm
        if bpm > 0:
            self.hr_label.setText(f"♥ 心率：{bpm:.0f} BPM")
            
            # 根据心率设置颜色
            if 60 <= bpm <= 100:
                self.hr_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 13px;")
            elif bpm < 50 or bpm > 120:
                self.hr_label.setStyleSheet("color: #f44336; font-weight: bold; font-size: 13px;")
            else:
                self.hr_label.setStyleSheet("color: #ff9800; font-weight: bold; font-size: 13px;")
        else:
            self.hr_label.setText("♥ 心率：-- BPM")
    
    def set_breath_rate(self, rpm: float):
        """设置呼吸率值"""
        self.breath_rate = rpm
        if rpm > 0:
            self.br_label.setText(f"🫁 呼吸：{rpm:.1f} RPM")
            
            # 根据呼吸率设置颜色
            if 12 <= rpm <= 20:
                self.br_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 13px;")
            elif rpm < 10 or rpm > 30:
                self.br_label.setStyleSheet("color: #f44336; font-weight: bold; font-size: 13px;")
            else:
                self.br_label.setStyleSheet("color: #ff9800; font-weight: bold; font-size: 13px;")
        else:
            self.br_label.setText("🫁 呼吸：-- RPM")
    
    def set_sampling_rate(self, rate: int):
        """设置采样率"""
        self.sampling_rate = rate
        self.sr_label.setText(f"📊 采样率：{rate} SPS")
    
    def set_connected(self, connected: bool):
        """设置连接状态"""
        self.is_connected = connected
        if connected:
            self.status_indicator.setText("● 运行中")
            self.status_indicator.setStyleSheet("color: #4CAF50;")
        else:
            self.status_indicator.setText("○ 未连接")
            self.status_indicator.setStyleSheet("color: #9e9e9e;")
    
    def update_stats(self, frames: int, bytes_count: int, errors: int = 0):
        """更新统计信息"""
        self.frames_received = frames
        self.bytes_received = bytes_count
        self.error_count = errors
        
        # 格式化显示
        if frames >= 1000:
            frames_str = f"{frames/1000:.1f}k"
        else:
            frames_str = str(frames)
        
        if bytes_count >= 1000000:
            bytes_str = f"{bytes_count/1000000:.1f}MB"
        elif bytes_count >= 1000:
            bytes_str = f"{bytes_count/1000:.1f}kB"
        else:
            bytes_str = str(bytes_count)
        
        self.stats_label.setText(f"📥 接收：{frames_str} 帧 | {bytes_str}")
        
        if errors > 0:
            self.error_label.setText(f"⚠ 错误：{errors}")
            self.error_label.setStyleSheet("color: #f44336;")
        else:
            self.error_label.setText("⚠ 错误：0")
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
        """初始化 UI"""
        self.setStyleSheet("""
            ControlPanel {
                background-color: #2d2d44;
                border-bottom: 1px solid #3d3d5c;
                padding: 5px;
            }
            QPushButton {
                background-color: #3d3d5c;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                margin: 0 2px;
            }
            QPushButton:hover {
                background-color: #4d4d6c;
            }
            QPushButton:pressed {
                background-color: #2d2d44;
            }
            QPushButton:checked {
                background-color: #4CAF50;
            }
            QPushButton:menu-indicator {
                image: none;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # 保存按钮 (带下拉菜单)
        from PyQt5.QtWidgets import QMenu
        save_menu = QMenu()
        save_menu.addAction("CSV 格式", lambda: self.save_csv_requested.emit())
        save_menu.addAction("EDF 格式 (医学标准)", lambda: self.save_edf_requested.emit())
        save_menu.addAction("MATLAB 格式", lambda: self.save_mat_requested.emit())
        save_menu.addAction("导出报告 (JSON)", lambda: self.export_report_requested.emit())
        
        self.save_btn = QPushButton("💾 导出数据")
        self.save_btn.setMenu(save_menu)
        layout.addWidget(self.save_btn)

        # 截图按钮
        self.screenshot_btn = QPushButton("📷 截图")
        self.screenshot_btn.clicked.connect(lambda: self.screenshot_requested.emit())
        layout.addWidget(self.screenshot_btn)

        # 暂停按钮
        self.pause_btn = QPushButton("⏸ 暂停")
        self.pause_btn.setCheckable(True)
        self.pause_btn.toggled.connect(lambda: self.pause_toggled.emit(self.pause_btn.isChecked()))
        layout.addWidget(self.pause_btn)

        # 滤波开关
        self.filter_btn = QPushButton("🔧 滤波：开")
        self.filter_btn.setCheckable(True)
        self.filter_btn.setChecked(True)
        self.filter_btn.toggled.connect(self._on_filter_toggled)
        layout.addWidget(self.filter_btn)

        # 自动缩放
        self.auto_scale_btn = QPushButton("📐 自动缩放")
        self.auto_scale_btn.setCheckable(True)
        self.auto_scale_btn.setChecked(True)
        layout.addWidget(self.auto_scale_btn)

        layout.addStretch()

        # 清除按钮
        self.clear_btn = QPushButton("🗑 清除")
        self.clear_btn.clicked.connect(lambda: self.clear_requested.emit())
        layout.addWidget(self.clear_btn)

    def _on_filter_toggled(self, checked: bool):
        """滤波开关切换"""
        if checked:
            self.filter_btn.setText("🔧 滤波：开")
        else:
            self.filter_btn.setText("🔧 滤波：关")
        self.filter_toggled.emit(checked)
