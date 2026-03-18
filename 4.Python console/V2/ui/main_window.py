# -*- coding: utf-8 -*-
"""
主窗口
整合所有组件，实现完整的 ECG 查看器功能
"""

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QMessageBox, QFileDialog, QSplitter)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from comms.serial_manager import SerialManager
from comms.protocol_parser import ProtocolParser, ECGFrame
from data.circular_buffer import CircularBuffer
from data.data_saver import DataSaver, ScreenshotSaver
from signal_processing.heart_rate import HeartRateDetector
from signal_processing.breath_rate import BreathRateDetector
from signal_processing.filter import DigitalFilter

from ui.serial_panel import SerialPanel
from ui.waveform_widget import WaveformWidget
from ui.fft_widget import FFTWidget
from ui.status_bar import StatusBar, ControlPanel


class MainWindow(QMainWindow):
    """
    ECG 查看器主窗口
    """
    
    def __init__(self):
        super().__init__()
        
        # 初始化核心组件
        self.serial_manager = SerialManager()
        self.parser = ProtocolParser()
        self.data_saver = DataSaver()
        self.screenshot_saver = ScreenshotSaver()
        
        # 信号处理组件
        self.heart_rate_detector = HeartRateDetector(sampling_rate=500)
        self.breath_rate_detector = BreathRateDetector(sampling_rate=500)
        self.digital_filter = DigitalFilter(sampling_rate=500)
        
        # 数据缓冲
        self.ecg_buffer = CircularBuffer(max_points=5000, num_channels=4)
        
        # 状态变量
        self.is_connected = False
        self.is_paused = False
        self.is_filter_enabled = True
        self.frames_count = 0
        self.bytes_received = 0
        
        # 创建 UI
        self._init_ui()
        
        # 连接信号
        self._connect_signals()
        
        # 数据处理定时器
        self.process_timer = QTimer()
        self.process_timer.timeout.connect(self._process_data)
        self.process_timer.start(50)  # 20 Hz 处理频率
        
        # 窗口状态
        self.setWindowTitle("ECG Viewer - ADS1294R 调试工具")
        self.resize(1400, 900)
    
    def _init_ui(self):
        """初始化 UI"""
        # 中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 串口配置面板
        self.serial_panel = SerialPanel(self.serial_manager)
        main_layout.addWidget(self.serial_panel)
        
        # 工具控制面板
        self.control_panel = ControlPanel()
        main_layout.addWidget(self.control_panel)
        
        # 分割器 (波形 + FFT)
        splitter = QSplitter(Qt.Vertical)
        
        # 波形显示组件
        self.waveform_widget = WaveformWidget()
        splitter.addWidget(self.waveform_widget)
        
        # FFT 频谱组件
        self.fft_widget = FFTWidget(sampling_rate=500)
        splitter.addWidget(self.fft_widget)
        
        # 设置分割比例
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # 状态栏
        self.status_bar = StatusBar()
        main_layout.addWidget(self.status_bar)
    
    def _connect_signals(self):
        """连接信号"""
        # 串口管理器信号
        self.serial_manager.data_received.connect(self._on_data_received)
        self.serial_manager.connected.connect(self._on_serial_connected)
        self.serial_manager.disconnected.connect(self._on_serial_disconnected)

        # 采样率变化信号
        self.serial_panel.sampling_rate_changed.connect(self.set_sampling_rate)

        # 控制面板信号
        self.control_panel.save_csv_requested.connect(self._save_csv)
        self.control_panel.save_edf_requested.connect(self._save_edf)
        self.control_panel.save_mat_requested.connect(self._save_mat)
        self.control_panel.export_report_requested.connect(self._export_report)
        self.control_panel.screenshot_requested.connect(self._take_screenshot)
        self.control_panel.pause_toggled.connect(self._on_pause_toggled)
        self.control_panel.filter_toggled.connect(self._on_filter_toggled)
        self.control_panel.clear_requested.connect(self._clear_display)
    
    def _on_data_received(self, data: bytes):
        """
        处理串口接收数据
        
        Args:
            data: 原始字节数据
        """
        self.bytes_received += len(data)
        
        # 解析数据帧
        frames = self.parser.parse(data)
        
        # 处理每一帧
        for frame in frames:
            self._process_frame(frame)
            self.frames_count += 1
    
    def _process_frame(self, frame: ECGFrame):
        """
        处理单帧数据

        Args:
            frame: ECG 数据帧
        """
        if self.is_paused:
            return

        # 获取样本数据
        samples = frame.samples.copy()  # shape: (4, 4)
        
        # 应用数字滤波
        if self.is_filter_enabled:
            for ch in range(4):
                samples[:, ch] = self.digital_filter.ecg_filter(samples[:, ch])
        
        # 添加到缓冲区
        self.ecg_buffer.add_data(samples)
        self.waveform_widget.add_data(frame)
        
        # 添加到 FFT 分析
        self.fft_widget.add_data(samples)
        
        # 心率和呼吸率检测 (使用 CH2-CH4 合成 II 导联检测心率，CH1 检测呼吸)
        if self.ecg_buffer.get_length() >= 500:  # 至少 1 秒数据
            # 获取最新数据
            ecg_data = self.ecg_buffer.get_channel_data(1, num_points=1000)  # CH2 for HR
            
            if len(ecg_data) >= 500:
                # 心率检测
                bpm, _ = self.heart_rate_detector.process(ecg_data)
                self.status_bar.set_heart_rate(bpm)
                
                # 呼吸检测 (使用 CH1)
                breath_data = self.ecg_buffer.get_channel_data(0, num_points=2500)  # 5 秒数据
                if len(breath_data) >= 500:
                    rpm, _, _ = self.breath_rate_detector.process(breath_data)
                    self.status_bar.set_breath_rate(rpm)
    
    def _process_data(self):
        """定期处理数据"""
        # 更新统计信息
        parser_stats = self.parser.get_stats()
        self.status_bar.update_stats(
            frames=self.frames_count,
            bytes_count=self.bytes_received,
            errors=parser_stats['error_count']
        )
        
        # 更新采样率显示
        self.status_bar.set_sampling_rate(self.waveform_widget.sampling_rate)
    
    def _on_serial_connected(self):
        """串口连接成功"""
        self.is_connected = True
        self.status_bar.set_connected(True)
        self.parser.reset()
        self.frames_count = 0
        self.bytes_received = 0
    
    def _on_serial_disconnected(self):
        """串口断开连接"""
        self.is_connected = False
        self.status_bar.set_connected(False)
    
    def _on_pause_toggled(self, paused: bool):
        """暂停切换"""
        self.is_paused = paused
        if paused:
            self.control_panel.pause_btn.setText("▶ 继续")
        else:
            self.control_panel.pause_btn.setText("⏸ 暂停")
    
    def _on_filter_toggled(self, enabled: bool):
        """滤波开关切换"""
        self.is_filter_enabled = enabled
    
    def _save_csv(self):
        """保存 CSV"""
        # 获取当前数据
        data = self.ecg_buffer.get_all_channels()

        if len(data) == 0:
            QMessageBox.information(self, "提示", "没有数据可保存！")
            return

        # 选择保存路径
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "保存 ECG 数据",
            "",
            "CSV 文件 (*.csv);;所有文件 (*.*)"
        )

        if filename:
            try:
                filepath = self.data_saver.save_to_csv(
                    data,
                    filename=os.path.basename(filename),
                    sampling_rate=self.waveform_widget.sampling_rate,
                    metadata={
                        'Device': 'ADS1294R',
                        'Channels': 4,
                        'Software': 'ECG Viewer'
                    }
                )
                QMessageBox.information(
                    self,
                    "保存成功",
                    f"数据已保存到:\n{filepath}"
                )
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"错误：{str(e)}")

    def _save_edf(self):
        """保存 EDF 格式 (医学标准格式)"""
        data = self.ecg_buffer.get_all_channels()

        if len(data) == 0:
            QMessageBox.information(self, "提示", "没有数据可保存！")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "保存 ECG 数据 (EDF 格式)",
            "",
            "EDF 文件 (*.edf);;所有文件 (*.*)"
        )

        if filename:
            try:
                patient_info = {
                    'id': 'Patient_001',
                    'name': 'Anonymous'
                }
                filepath = self.data_saver.save_to_edf(
                    data,
                    filename=os.path.basename(filename),
                    sampling_rate=self.waveform_widget.sampling_rate,
                    patient_info=patient_info
                )
                QMessageBox.information(
                    self,
                    "保存成功",
                    f"数据已保存到:\n{filepath}\n\n此文件可用 EDF 查看器（如 EDFBrowser）打开"
                )
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"错误：{str(e)}")

    def _save_mat(self):
        """保存 MATLAB 格式"""
        data = self.ecg_buffer.get_all_channels()

        if len(data) == 0:
            QMessageBox.information(self, "提示", "没有数据可保存！")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "保存 ECG 数据 (MATLAB)",
            "",
            "MATLAB 文件 (*.mat);;所有文件 (*.*)"
        )

        if filename:
            try:
                filepath = self.data_saver.save_to_mat(
                    data,
                    filename=os.path.basename(filename),
                    sampling_rate=self.waveform_widget.sampling_rate,
                    metadata={
                        'Device': 'ADS1294R',
                        'Software': 'ECG Viewer'
                    }
                )
                QMessageBox.information(
                    self,
                    "保存成功",
                    f"数据已保存到:\n{filepath}\n\n可在 MATLAB 中使用 load() 函数打开"
                )
            except ImportError as e:
                QMessageBox.critical(
                    self, "依赖缺失",
                    f"需要安装 scipy 库:\n{str(e)}\n\n请运行：pip install scipy"
                )
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"错误：{str(e)}")

    def _export_report(self):
        """导出分析报告"""
        data = self.ecg_buffer.get_all_channels()

        if len(data) == 0:
            QMessageBox.information(self, "提示", "没有数据可保存！")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "导出分析报告",
            "",
            "JSON 文件 (*.json);;所有文件 (*.*)"
        )

        if filename:
            try:
                # 获取当前心率和呼吸率
                heart_rate = self.status_bar.heart_rate
                breath_rate = self.status_bar.breath_rate

                filepath = self.data_saver.export_report(
                    data,
                    heart_rate=heart_rate,
                    breath_rate=breath_rate,
                    filename=os.path.basename(filename)
                )
                QMessageBox.information(
                    self,
                    "导出成功",
                    f"报告已保存到:\n{filepath}"
                )
            except Exception as e:
                QMessageBox.critical(self, "导出失败", f"错误：{str(e)}")
    
    def _take_screenshot(self):
        """截图"""
        # 截取中央组件
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "保存截图",
            "",
            "PNG 图像 (*.png);;所有文件 (*.*)"
        )
        
        if filename:
            try:
                pixmap = self.centralWidget().grab()
                pixmap.save(filename, 'PNG')
                QMessageBox.information(
                    self,
                    "截图成功",
                    f"截图已保存到:\n{filename}"
                )
            except Exception as e:
                QMessageBox.critical(self, "截图失败", f"错误：{str(e)}")
    
    def _clear_display(self):
        """清除显示"""
        self.ecg_buffer.clear()
        self.waveform_widget.clear()
        self.fft_widget.clear()
        self.heart_rate_detector.reset()
        self.breath_rate_detector.reset()
        self.status_bar.set_heart_rate(0)
        self.status_bar.set_breath_rate(0)
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 断开串口连接
        if self.is_connected:
            self.serial_manager.disconnect()
        
        event.accept()
    
    def set_sampling_rate(self, rate: int):
        """
        设置采样率
        
        Args:
            rate: 采样率 (SPS)
        """
        self.waveform_widget.set_sampling_rate(rate)
        self.fft_widget.set_sampling_rate(rate)
        self.heart_rate_detector.set_sampling_rate(rate)
        self.breath_rate_detector.set_sampling_rate(rate)
        self.digital_filter.set_sampling_rate(rate)
