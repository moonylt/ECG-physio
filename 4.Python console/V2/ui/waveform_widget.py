# -*- coding: utf-8 -*-
"""
波形显示组件
使用 pyqtgraph 实现高性能实时波形显示
"""

import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPen
import numpy as np
from typing import Optional, List

from data.circular_buffer import CircularBuffer
from comms.protocol_parser import ECGFrame


class WaveformWidget(QWidget):
    """
    4 通道 ECG 波形显示组件
    """
    
    # 通道颜色
    CHANNEL_COLORS = [
        QColor('#ff6b6b'),  # CH1 - 红色
        QColor('#51cf66'),  # CH2 - 绿色
        QColor('#339af0'),  # CH3 - 蓝色
        QColor('#ffd43b')   # CH4 - 黄色
    ]
    
    # 通道名称
    CHANNEL_NAMES = ['CH1 (呼吸)', 'CH2 (RA)', 'CH3 (LA)', 'CH4 (LL)']
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 显示参数
        self.sampling_rate = 500  # SPS
        self.seconds_per_div = 1.0  # 每格秒数
        self.num_channels = 4
        
        # 数据缓冲区
        self.buffer = CircularBuffer(max_points=10000, num_channels=self.num_channels)
        
        # 创建 UI
        self._init_ui()
        
        # 创建定时器用于自动刷新
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._update_plots)
        self.refresh_timer.start(33)  # ~30 FPS
        
        # 显示控制
        self.channel_visible = [True] * self.num_channels
        self.auto_scale = True
        self.paused = False
        
        # Y 轴范围 (自动缩放用)
        self.y_ranges = [(-500, 500)] * self.num_channels
    
    def _init_ui(self):
        """初始化 UI"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        # 创建 4 个绘图区域
        self.plots = []
        self.curves = []
        self.x_data = np.array([])

        # 配置 pyqtgraph 全局选项（性能优化）
        pg.setConfigOptions(antialias=False)  # 禁用抗锯齿提高性能
        pg.setConfigOptions(enableExperimental=True)  # 启用实验性功能

        for i in range(self.num_channels):
            # 创建绘图组件
            plot = pg.PlotWidget()
            plot.setMenuEnabled(False)
            plot.showGrid(x=True, y=True, alpha=0.3)
            plot.setBackground('#1a1a2e')
            plot.setTitle(f'{self.CHANNEL_NAMES[i]}')

            # 优化绘图选项
            plot.setMouseEnabled(False, False)  # 禁用鼠标交互提高性能
            plot.hideButtons()  # 隐藏自动缩放按钮

            # 设置坐标轴
            plot.setLabel('left', '')
            plot.setLabel('bottom', 'Time', units='s')

            # 设置 X 轴范围
            plot.setXRange(0, self.seconds_per_div * 10)

            # 创建曲线（优化）
            pen = pg.mkPen(color=self.CHANNEL_COLORS[i], width=1.5)
            curve = plot.plot(pen=pen, downsample='auto', clipToView=True)

            self.plots.append(plot)
            self.curves.append(curve)
            self.layout.addWidget(plot)

        # 初始化 X 轴数据
        self._update_x_data()
    
    def _update_x_data(self):
        """更新 X 轴时间数据"""
        num_points = int(self.seconds_per_div * 10 * self.sampling_rate)
        self.x_data = np.arange(num_points) / self.sampling_rate
    
    def add_data(self, frame: ECGFrame):
        """
        添加新数据帧

        Args:
            frame: ECG 数据帧
        """
        if self.paused:
            return

        # 添加 4 个样本到缓冲区 (不是 10 个)
        self.buffer.add_data(frame.samples)

        # 更新 Y 轴范围
        self._update_y_ranges()
    
    def _update_y_ranges(self):
        """更新 Y 轴显示范围"""
        for ch in range(self.num_channels):
            data = self.buffer.get_channel_data(ch, num_points=1000)
            if len(data) > 0:
                # 计算合适的 Y 轴范围
                data_min = np.nanmin(data)
                data_max = np.nanmax(data)
                data_range = data_max - data_min
                
                if data_range < 100:
                    data_range = 100
                
                center = (data_max + data_min) / 2
                margin = data_range * 0.2
                
                self.y_ranges[ch] = (center - data_range/2 - margin, 
                                     center + data_range/2 + margin)
    
    def _update_plots(self):
        """更新波形显示（优化版本）"""
        if self.paused:
            return

        num_points = int(self.seconds_per_div * 10 * self.sampling_rate)

        # 批量更新所有曲线
        updates_needed = []
        for ch in range(self.num_channels):
            if not self.channel_visible[ch]:
                continue

            # 获取最新数据
            data = self.buffer.get_channel_data(ch, num_points=num_points)

            if len(data) > 0:
                updates_needed.append(ch)

                # 更新 X 轴
                x_data = np.arange(len(data)) / self.sampling_rate
                
                # 使用 setData 的直接模式提高性能
                self.curves[ch].setData(x_data, data)

                # 自动缩放 Y 轴
                if self.auto_scale:
                    self.plots[ch].setYRange(*self.y_ranges[ch])
                else:
                    # 固定范围
                    scale = 1000
                    self.plots[ch].setYRange(-scale, scale)

                # 更新标题
                self.plots[ch].setTitle(f'{self.CHANNEL_NAMES[ch]}  Gain: ×{self.buffer.gains[ch]:.1f}')
        
        # 强制重绘（仅在有更新时）
        if updates_needed and not self.paused:
            for ch in updates_needed:
                self.plots[ch].repaint()
    
    def set_sampling_rate(self, rate: int):
        """设置采样率"""
        self.sampling_rate = rate
        self._update_x_data()
    
    def set_channel_visibility(self, channel: int, visible: bool):
        """设置通道可见性"""
        if 0 <= channel < self.num_channels:
            self.channel_visible[channel] = visible
            self.curves[channel].setVisible(visible)
    
    def set_channel_gain(self, channel: int, gain: float):
        """设置通道增益"""
        if 0 <= channel < self.num_channels:
            self.buffer.set_gain(channel, gain)
    
    def toggle_auto_scale(self, enable: bool):
        """切换自动缩放"""
        self.auto_scale = enable
    
    def toggle_pause(self, pause: bool):
        """切换暂停状态"""
        self.paused = pause
    
    def clear(self):
        """清空显示"""
        self.buffer.clear()
        for curve in self.curves:
            curve.setData([], [])
    
    def set_seconds_per_div(self, seconds: float):
        """设置 X 轴每格秒数"""
        self.seconds_per_div = seconds
        self._update_x_data()
        
        # 更新所有绘图区域的 X 轴范围
        for plot in self.plots:
            plot.setXRange(0, seconds * 10)
    
    def get_buffer_stats(self) -> dict:
        """获取缓冲区统计信息"""
        return self.buffer.get_stats()


class WaveformLegend(QWidget):
    """
    波形图例组件
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        
        self.labels = []
        colors = ['#ff6b6b', '#51cf66', '#339af0', '#ffd43b']
        names = ['CH1 (呼吸)', 'CH2 (RA)', 'CH3 (LA)', 'CH4 (LL)']
        
        for i in range(4):
            label_widget = QWidget()
            label_layout = QHBoxLayout(label_widget)
            label_layout.setContentsMargins(5, 0, 5, 0)
            
            # 颜色指示
            color_label = QLabel()
            color_label.setStyleSheet(f"background-color: {colors[i]};")
            color_label.setFixedSize(20, 10)
            
            # 名称
            name_label = QLabel(names[i])
            name_label.setStyleSheet("color: white;")
            
            label_layout.addWidget(color_label)
            label_layout.addWidget(name_label)
            label_layout.addStretch()
            
            self.labels.append(name_label)
            self.layout.addWidget(label_widget)
