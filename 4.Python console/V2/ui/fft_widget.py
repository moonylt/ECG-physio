# -*- coding: utf-8 -*-
"""
FFT 频谱分析组件
实时显示各通道信号的频谱
"""

import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import QTimer
import numpy as np
from scipy.signal import welch
from typing import Optional

from data.circular_buffer import CircularBuffer


class FFTWidget(QWidget):
    """
    4 通道 FFT 频谱显示组件
    """
    
    # 通道颜色
    CHANNEL_COLORS = [
        '#ff6b6b',  # CH1
        '#51cf66',  # CH2
        '#339af0',  # CH3
        '#ffd43b'   # CH4
    ]
    
    # 通道名称
    CHANNEL_NAMES = ['CH1', 'CH2', 'CH3', 'CH4']
    
    def __init__(self, parent=None, sampling_rate: int = 500):
        super().__init__(parent)
        
        self.sampling_rate = sampling_rate
        self.fft_window_size = 256  # FFT 点数
        self.num_channels = 4
        
        # 数据缓冲
        self.data_buffers = [CircularBuffer(max_points=512, num_channels=1) for _ in range(4)]
        
        # 创建 UI
        self._init_ui()
        
        # FFT 更新定时器
        self.fft_timer = QTimer()
        self.fft_timer.timeout.connect(self._update_fft)
        self.fft_timer.start(100)  # 10 Hz 刷新率
        
        # 显示控制
        self.visible = True
        self.log_scale = True  # 对数坐标
    
    def _init_ui(self):
        """初始化 UI"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        
        # 标题
        title_label = QLabel("FFT 频谱分析 (0-250 Hz)")
        title_label.setStyleSheet("color: white; font-weight: bold;")
        self.layout.addWidget(title_label)
        
        # 创建 2x2 网格布局
        self.plots = []
        self.curves = []
        
        # 创建 4 个绘图区域
        for i in range(self.num_channels):
            plot = pg.PlotWidget()
            plot.setMenuEnabled(False)
            plot.showGrid(x=True, y=True, alpha=0.3)
            plot.setBackground('#1a1a2e')
            plot.setTitle(self.CHANNEL_NAMES[i])
            
            # 设置坐标轴
            plot.setLabel('left', 'Power', units='dB')
            plot.setLabel('bottom', 'Frequency', units='Hz')
            plot.setXRange(0, 250)  # 0-250 Hz
            plot.setYRange(-100, 20)  # dB 范围
            
            # 创建曲线
            pen = pg.mkPen(color=self.CHANNEL_COLORS[i], width=1.5)
            curve = plot.plot(pen=pen)
            
            self.plots.append(plot)
            self.curves.append(curve)
        
        # 使用网格布局 (2x2)
        grid_layout = QHBoxLayout()
        
        left_column = QVBoxLayout()
        left_column.addWidget(self.plots[0])
        left_column.addWidget(self.plots[1])
        
        right_column = QVBoxLayout()
        right_column.addWidget(self.plots[2])
        right_column.addWidget(self.plots[3])
        
        grid_layout.addLayout(left_column)
        grid_layout.addLayout(right_column)
        
        self.layout.addLayout(grid_layout)
        
        # 频率数组 (预计算)
        self.freqs = None
    
    def add_data(self, samples: np.ndarray):
        """
        添加新数据用于 FFT 分析
        
        Args:
            samples: 样本数组 shape: (num_samples, 4)
        """
        if not self.visible:
            return
        
        for ch in range(self.num_channels):
            ch_data = samples[:, ch]
            self.data_buffers[ch].add_data(ch_data.reshape(-1, 1))
    
    def _update_fft(self):
        """更新 FFT 显示"""
        if not self.visible:
            return
        
        for ch in range(self.num_channels):
            # 获取数据
            data = self.data_buffers[ch].get_channel_data(0, num_points=self.fft_window_size)
            
            if len(data) < self.fft_window_size:
                continue
            
            # 应用汉宁窗
            window = np.hanning(len(data))
            data_windowed = data * window
            
            # 计算功率谱密度 (Welch 方法)
            freqs, psd = welch(
                data_windowed, 
                fs=self.sampling_rate, 
                nperseg=self.fft_window_size,
                noverlap=self.fft_window_size // 2
            )
            
            # 转换为 dB
            psd_db = 10 * np.log10(psd + 1e-10)
            
            # 限制频率范围 (0-250 Hz)
            mask = freqs <= 250
            freqs_display = freqs[mask]
            psd_display = psd_db[mask]
            
            # 更新曲线
            self.curves[ch].setData(freqs_display, psd_display)
            
            # 更新 Y 轴范围
            if len(psd_display) > 0:
                y_min = np.nanmin(psd_display) - 10
                y_max = np.nanmax(psd_display) + 10
                self.plots[ch].setYRange(max(-120, y_min), max(20, y_max))
    
    def set_sampling_rate(self, rate: int):
        """设置采样率"""
        self.sampling_rate = rate
    
    def toggle_visibility(self, visible: bool):
        """切换可见性"""
        self.visible = visible
        for plot in self.plots:
            plot.setVisible(visible)
    
    def toggle_log_scale(self, log_scale: bool):
        """切换对数坐标"""
        self.log_scale = log_scale
        # pyqtgraph 的对数坐标需要使用 LogAxis
        # 这里简化处理，保持线性坐标
    
    def clear(self):
        """清空显示"""
        for ch in range(self.num_channels):
            self.data_buffers[ch].clear()
            self.curves[ch].setData([], [])


class FFTSummaryWidget(QWidget):
    """
    FFT 频谱摘要组件 (单行显示 4 通道频谱)
    """
    
    def __init__(self, parent=None, sampling_rate: int = 500):
        super().__init__(parent)
        
        self.sampling_rate = sampling_rate
        self.fft_window_size = 256
        
        self._init_ui()
        
        self.fft_timer = QTimer()
        self.fft_timer.timeout.connect(self._update_fft)
        self.fft_timer.start(200)  # 5 Hz 刷新率
    
    def _init_ui(self):
        """初始化 UI"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        
        # 标题
        title_label = QLabel("FFT 频谱摘要")
        title_label.setStyleSheet("color: white; font-weight: bold;")
        self.layout.addWidget(title_label)
        
        # 创建绘图区域
        self.plot = pg.PlotWidget()
        self.plot.setMenuEnabled(False)
        self.plot.showGrid(x=True, y=True, alpha=0.3)
        self.plot.setBackground('#1a1a2e')
        self.plot.setLabel('left', 'Power', units='dB')
        self.plot.setLabel('bottom', 'Frequency', units='Hz')
        self.plot.setXRange(0, 100)  # 重点显示 0-100 Hz
        self.plot.setYRange(-80, 20)
        
        # 创建 4 条曲线
        colors = ['#ff6b6b', '#51cf66', '#339af0', '#ffd43b']
        self.curves = []
        for i in range(4):
            pen = pg.mkPen(color=colors[i], width=1.5)
            curve = self.plot.plot(pen=pen)
            self.curves.append(curve)
        
        self.layout.addWidget(self.plot)
        
        # 图例
        legend_layout = QHBoxLayout()
        labels = ['CH1 (呼吸)', 'CH2 (RA)', 'CH3 (LA)', 'CH4 (LL)']
        colors = ['#ff6b6b', '#51cf66', '#339af0', '#ffd43b']
        
        for i in range(4):
            label = QLabel(f"■ {labels[i]}")
            label.setStyleSheet(f"color: {colors[i]};")
            legend_layout.addWidget(label)
        
        legend_layout.addStretch()
        self.layout.addLayout(legend_layout)
    
    def add_data(self, samples: np.ndarray):
        """添加数据"""
        # 简化实现，实际使用时需要缓冲数据
        pass
    
    def _update_fft(self):
        """更新 FFT"""
        # 简化实现
        pass
