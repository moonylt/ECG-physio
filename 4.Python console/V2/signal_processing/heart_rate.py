# -*- coding: utf-8 -*-
"""
心率检测算法
基于 R 波检测的心率计算
"""

import numpy as np
from scipy.signal import butter, filtfilt, find_peaks
from collections import deque
from typing import Tuple, Optional


class HeartRateDetector:
    """
    心率检测器
    从 ECG 信号中检测 R 波并计算心率 (BPM)
    """
    
    def __init__(self, sampling_rate: int = 500):
        """
        初始化心率检测器
        
        Args:
            sampling_rate: 采样率 (SPS)
        """
        self.sampling_rate = sampling_rate
        self._design_filter()
        
        # R 波检测历史
        self.rr_intervals = deque(maxlen=10)  # 保存最近 10 个 RR 间期
        self.peak_history = deque(maxlen=100)  # 峰值历史
        
        # 检测结果
        self.current_bpm = 0
        self.last_peaks = []
        
        # 滤波器系数
        self.b = None
        self.a = None
    
    def _design_filter(self):
        """设计带通滤波器 (0.5-40Hz ECG 频段)"""
        nyquist = self.sampling_rate / 2
        low = 0.5 / nyquist
        high = 40.0 / nyquist
        self.b, self.a = butter(4, [low, high], btype='band')
    
    def detect_peaks(self, ecg_signal: np.ndarray) -> np.ndarray:
        """
        检测 R 波峰值位置
        
        Args:
            ecg_signal: ECG 信号数组
            
        Returns:
            R 波峰值位置数组
        """
        if len(ecg_signal) < self.sampling_rate:  # 至少需要 1 秒数据
            return np.array([])
        
        # 带通滤波
        filtered = self._bandpass_filter(ecg_signal)
        
        # 动态阈值
        signal_std = np.std(filtered)
        signal_mean = np.mean(filtered)
        
        # R 波检测参数
        min_distance = int(self.sampling_rate * 0.25)  # 最小 RR 间期 250ms (对应 240 BPM)
        max_distance = int(self.sampling_rate * 2.5)   # 最大 RR 间期 2.5s (对应 24 BPM)
        height_threshold = signal_mean + 1.5 * signal_std
        prominence_threshold = 0.3 * signal_std
        
        # 找峰值
        peaks, properties = find_peaks(
            filtered,
            height=height_threshold,
            prominence=prominence_threshold,
            distance=min_distance,
            width=int(self.sampling_rate * 0.04)  # 最小宽度 40ms
        )
        
        # 保存峰值历史
        for peak in peaks:
            self.peak_history.append(peak)
        
        self.last_peaks = peaks
        return peaks
    
    def calculate_bpm(self, peaks: np.ndarray, ecg_signal: np.ndarray) -> float:
        """
        计算心率 (BPM)
        
        Args:
            peaks: R 波峰值位置
            ecg_signal: 原始 ECG 信号
            
        Returns:
            心率值 (BPM)
        """
        if len(peaks) < 2:
            return 0
        
        # 计算 RR 间期
        rr_intervals = np.diff(peaks) / self.sampling_rate  # 转换为秒
        
        # 过滤异常值 (正常 RR 间期 0.3-2.0 秒)
        valid_rr = rr_intervals[(rr_intervals >= 0.3) & (rr_intervals <= 2.0)]
        
        if len(valid_rr) < 1:
            return 0
        
        # 使用中值计算心率 (抗异常值)
        median_rr = np.median(valid_rr)
        
        # 保存到历史
        self.rr_intervals.append(median_rr)
        
        # 计算 BPM
        bpm = 60.0 / median_rr
        
        # 合理性检查 (30-200 BPM)
        if 30 <= bpm <= 200:
            self.current_bpm = bpm
        else:
            # 使用历史平均值
            if len(self.rr_intervals) > 0:
                avg_rr = np.median(list(self.rr_intervals))
                self.current_bpm = 60.0 / avg_rr
        
        return self.current_bpm
    
    def _bandpass_filter(self, signal: np.ndarray) -> np.ndarray:
        """
        带通滤波
        
        Args:
            signal: 输入信号
            
        Returns:
            滤波后信号
        """
        try:
            # 使用 filtfilt 实现零相位滤波
            return filtfilt(self.b, self.a, signal)
        except Exception:
            return signal
    
    def process(self, ecg_signal: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        处理 ECG 信号，返回心率和 R 波位置
        
        Args:
            ecg_signal: ECG 信号数组
            
        Returns:
            (心率 BPM, R 波位置数组)
        """
        peaks = self.detect_peaks(ecg_signal)
        bpm = self.calculate_bpm(peaks, ecg_signal)
        return bpm, peaks
    
    def get_rr_intervals(self) -> np.ndarray:
        """获取 RR 间期历史"""
        return np.array(list(self.rr_intervals))
    
    def get_hrv_metrics(self) -> dict:
        """
        获取心率变异性 (HRV) 指标
        
        Returns:
            HRV 指标字典
        """
        if len(self.rr_intervals) < 2:
            return {'sdnn': 0, 'rmssd': 0}
        
        rr_array = np.array(list(self.rr_intervals))
        
        # SDNN: RR 间期的标准差
        sdnn = np.std(rr_array)
        
        # RMSSD: 相邻 RR 间期差值的均方根
        diff_rr = np.diff(rr_array)
        rmssd = np.sqrt(np.mean(diff_rr ** 2))
        
        return {
            'sdnn': sdnn,
            'rmssd': rmssd,
            'mean_rr': np.mean(rr_array),
            'std_rr': np.std(rr_array)
        }
    
    def reset(self):
        """重置检测器状态"""
        self.rr_intervals.clear()
        self.peak_history.clear()
        self.current_bpm = 0
        self.last_peaks = []
    
    def set_sampling_rate(self, sampling_rate: int):
        """设置采样率"""
        self.sampling_rate = sampling_rate
        self._design_filter()
