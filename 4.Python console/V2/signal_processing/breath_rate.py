# -*- coding: utf-8 -*-
"""
呼吸率检测算法
从呼吸阻抗信号中提取呼吸波形并计算呼吸率
"""

import numpy as np
from scipy.signal import butter, filtfilt, find_peaks, hilbert
from collections import deque
from typing import Tuple, Optional


class BreathRateDetector:
    """
    呼吸率检测器
    从呼吸阻抗信号 (CH1) 中提取呼吸波形并计算呼吸率 (RPM)
    """
    
    def __init__(self, sampling_rate: int = 500):
        """
        初始化呼吸率检测器
        
        Args:
            sampling_rate: 采样率 (SPS)
        """
        self.sampling_rate = sampling_rate
        self._design_filter()
        
        # 检测历史
        self.breath_peaks = deque(maxlen=20)
        self.breath_intervals = deque(maxlen=10)
        
        # 检测结果
        self.current_rpm = 0
        self.envelope = None
        
        # 滤波器系数
        self.b_low = None
        self.a_low = None
        self.b_high = None
        self.a_high = None
    
    def _design_filter(self):
        """
        设计滤波器
        
        呼吸频率范围：0.1-1 Hz (6-60 次/分钟)
        正常成人静息呼吸：12-20 次/分钟 (0.2-0.33 Hz)
        """
        nyquist = self.sampling_rate / 2
        
        # 带通滤波 0.1-1 Hz
        low_cutoff = 0.1 / nyquist
        high_cutoff = 1.0 / nyquist
        self.b_low, self.a_low = butter(2, [low_cutoff, high_cutoff], btype='band')
        
        # 低通滤波 0.5 Hz (用于包络平滑)
        self.b_high, self.a_high = butter(2, 0.5 / nyquist, btype='low')
    
    def extract_breath_wave(self, signal: np.ndarray) -> np.ndarray:
        """
        提取呼吸波
        
        Args:
            signal: 原始信号 (包含呼吸和交流成分)
            
        Returns:
            呼吸波信号
        """
        if len(signal) < self.sampling_rate * 2:  # 至少 2 秒数据
            return signal
        
        # 带通滤波提取呼吸成分
        breath_wave = self._bandpass_filter(signal)
        
        return breath_wave
    
    def detect_peaks(self, breath_signal: np.ndarray) -> np.ndarray:
        """
        检测呼吸波峰值
        
        Args:
            breath_signal: 呼吸波信号
            
        Returns:
            峰值位置数组
        """
        if len(breath_signal) < self.sampling_rate * 2:
            return np.array([])
        
        # 使用希尔伯特变换提取包络
        analytic_signal = hilbert(breath_signal)
        self.envelope = np.abs(analytic_signal)
        
        # 平滑包络
        try:
            envelope_smooth = filtfilt(self.b_high, self.a_high, self.envelope)
        except Exception:
            envelope_smooth = self.envelope
        
        # 检测峰值
        min_distance = int(self.sampling_rate * 0.8)  # 最小呼吸周期 0.8 秒 (75 RPM)
        max_distance = int(self.sampling_rate * 10)    # 最大呼吸周期 10 秒 (6 RPM)
        
        # 动态阈值
        signal_mean = np.mean(envelope_smooth)
        signal_std = np.std(envelope_smooth)
        
        peaks, _ = find_peaks(
            envelope_smooth,
            height=signal_mean + 0.5 * signal_std,
            distance=min_distance,
            prominence=0.3 * signal_std
        )
        
        # 保存峰值历史
        for peak in peaks:
            self.breath_peaks.append(peak)
        
        return peaks
    
    def calculate_rpm(self, peaks: np.ndarray) -> float:
        """
        计算呼吸率 (RPM - Respirations Per Minute)
        
        Args:
            peaks: 呼吸波峰值位置
            
        Returns:
            呼吸率值 (RPM)
        """
        if len(peaks) < 2:
            # 如果峰值不足，使用包络的频谱分析估算
            if self.envelope is not None and len(self.envelope) > self.sampling_rate * 4:
                return self._estimate_rpm_from_spectrum()
            return 0
        
        # 计算呼吸间期
        breath_intervals = np.diff(peaks) / self.sampling_rate  # 转换为秒
        
        # 过滤异常值 (正常呼吸周期 1-10 秒)
        valid_intervals = breath_intervals[(breath_intervals >= 1.0) & (breath_intervals <= 10.0)]
        
        if len(valid_intervals) < 1:
            return 0
        
        # 使用中值计算呼吸率
        median_interval = np.median(valid_intervals)
        
        # 保存到历史
        self.breath_intervals.append(median_interval)
        
        # 计算 RPM
        rpm = 60.0 / median_interval
        
        # 合理性检查 (4-60 RPM)
        if 4 <= rpm <= 60:
            self.current_rpm = rpm
        else:
            # 使用历史平均值
            if len(self.breath_intervals) > 0:
                avg_interval = np.median(list(self.breath_intervals))
                self.current_rpm = 60.0 / avg_interval
        
        return self.current_rpm
    
    def _estimate_rpm_from_spectrum(self) -> float:
        """
        从频谱分析估算呼吸率
        
        Returns:
            估算的呼吸率
        """
        if self.envelope is None:
            return 0
        
        # FFT 分析
        fft_result = np.fft.fft(self.envelope)
        freqs = np.fft.fftfreq(len(self.envelope), 1/self.sampling_rate)
        
        # 只考虑正频率和呼吸频段 (0.1-1 Hz)
        positive_freqs = freqs[:len(freqs)//2]
        positive_fft = np.abs(fft_result[:len(fft_result)//2])
        
        # 找到呼吸频段的最大值
        breath_band = (positive_freqs >= 0.1) & (positive_freqs <= 1.0)
        if np.sum(breath_band) > 0:
            breath_fft = positive_fft.copy()
            breath_fft[~breath_band] = 0
            peak_idx = np.argmax(breath_fft)
            peak_freq = positive_freqs[peak_idx]
            
            # 转换为 RPM
            rpm = peak_freq * 60
            
            if 4 <= rpm <= 60:
                self.current_rpm = rpm
                return rpm
        
        return 0
    
    def _bandpass_filter(self, signal: np.ndarray) -> np.ndarray:
        """带通滤波"""
        try:
            return filtfilt(self.b_low, self.a_low, signal)
        except Exception:
            return signal
    
    def process(self, breath_signal: np.ndarray) -> Tuple[float, np.ndarray, np.ndarray]:
        """
        处理呼吸信号
        
        Args:
            breath_signal: 呼吸阻抗信号
            
        Returns:
            (呼吸率 RPM, 呼吸波，峰值位置)
        """
        # 提取呼吸波
        breath_wave = self.extract_breath_wave(breath_signal)
        
        # 检测峰值
        peaks = self.detect_peaks(breath_wave)
        
        # 计算呼吸率
        rpm = self.calculate_rpm(peaks)
        
        return rpm, breath_wave, peaks
    
    def get_breath_wave(self) -> np.ndarray:
        """获取提取的呼吸波"""
        return self.envelope if self.envelope is not None else np.array([])
    
    def reset(self):
        """重置检测器状态"""
        self.breath_peaks.clear()
        self.breath_intervals.clear()
        self.current_rpm = 0
        self.envelope = None
    
    def set_sampling_rate(self, sampling_rate: int):
        """设置采样率"""
        self.sampling_rate = sampling_rate
        self._design_filter()
