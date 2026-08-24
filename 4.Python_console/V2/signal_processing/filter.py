# -*- coding: utf-8 -*-
"""
数字滤波器模块
提供 50Hz 陷波、低通、高通、带通滤波功能
"""

import numpy as np
from scipy.signal import butter, filtfilt, iirnotch, lfilter
from typing import Optional, Tuple


class DigitalFilter:
    """
    数字滤波器
    提供多种滤波功能
    """
    
    def __init__(self, sampling_rate: int = 500):
        """
        初始化滤波器
        
        Args:
            sampling_rate: 采样率 (SPS)
        """
        self.sampling_rate = sampling_rate
        self._design_filters()
    
    def _design_filters(self):
        """设计各种滤波器系数"""
        nyquist = self.sampling_rate / 2
        
        # 50Hz 陷波滤波器 (工频干扰)
        self.notch_freq = 50.0  # 50Hz
        self.notch_q = 30.0     # 品质因数
        self.b_notch, self.a_notch = iirnotch(
            self.notch_freq / nyquist, 
            self.notch_q
        )
        
        # 低通滤波器 150Hz (ECG 信号上限)
        self.b_low, self.a_low = butter(4, 150.0 / nyquist, btype='low')
        
        # 高通滤波器 0.5Hz (去除基线漂移)
        self.b_high, self.a_high = butter(4, 0.5 / nyquist, btype='high')
        
        # 带通滤波器 0.5-150Hz (ECG 完整频段)
        self.b_band, self.a_band = butter(4, 
                                          [0.5 / nyquist, 150.0 / nyquist], 
                                          btype='band')
        
        # 呼吸带通滤波器 0.1-1Hz
        self.b_breath, self.a_breath = butter(2, 
                                              [0.1 / nyquist, 1.0 / nyquist], 
                                              btype='band')
    
    def notch_filter(self, signal: np.ndarray) -> np.ndarray:
        """
        50Hz 陷波滤波 (去除工频干扰)
        
        Args:
            signal: 输入信号
            
        Returns:
            滤波后信号
        """
        try:
            return filtfilt(self.b_notch, self.a_notch, signal)
        except Exception:
            return signal
    
    def lowpass_filter(self, signal: np.ndarray, 
                       cutoff: Optional[float] = None) -> np.ndarray:
        """
        低通滤波
        
        Args:
            signal: 输入信号
            cutoff: 截止频率，None 使用默认值
            
        Returns:
            滤波后信号
        """
        if cutoff is None:
            cutoff = 150.0
        
        nyquist = self.sampling_rate / 2
        try:
            b, a = butter(4, cutoff / nyquist, btype='low')
            return filtfilt(b, a, signal)
        except Exception:
            return signal
    
    def highpass_filter(self, signal: np.ndarray,
                        cutoff: Optional[float] = None) -> np.ndarray:
        """
        高通滤波 (去除基线漂移)
        
        Args:
            signal: 输入信号
            cutoff: 截止频率，None 使用默认值
            
        Returns:
            滤波后信号
        """
        if cutoff is None:
            cutoff = 0.5
        
        nyquist = self.sampling_rate / 2
        try:
            b, a = butter(4, cutoff / nyquist, btype='high')
            return filtfilt(b, a, signal)
        except Exception:
            return signal
    
    def bandpass_filter(self, signal: np.ndarray,
                        lowcut: Optional[float] = None,
                        highcut: Optional[float] = None) -> np.ndarray:
        """
        带通滤波
        
        Args:
            signal: 输入信号
            lowcut: 低截止频率
            highcut: 高截止频率
            
        Returns:
            滤波后信号
        """
        if lowcut is None:
            lowcut = 0.5
        if highcut is None:
            highcut = 150.0
        
        nyquist = self.sampling_rate / 2
        try:
            b, a = butter(4, [lowcut / nyquist, highcut / nyquist], btype='band')
            return filtfilt(b, a, signal)
        except Exception:
            return signal
    
    def ecg_filter(self, signal: np.ndarray, 
                   remove_baseline: bool = True,
                   remove_50hz: bool = True) -> np.ndarray:
        """
        ECG 信号专用滤波
        
        Args:
            signal: ECG 信号
            remove_baseline: 是否去除基线漂移
            remove_50hz: 是否去除 50Hz 工频干扰
            
        Returns:
            滤波后信号
        """
        result = signal.copy()
        
        # 去除基线漂移 (高通 0.5Hz)
        if remove_baseline:
            result = self.highpass_filter(result, 0.5)
        
        # 50Hz 陷波
        if remove_50hz:
            result = self.notch_filter(result)
        
        # 低通滤波 (150Hz)
        result = self.lowpass_filter(result, 150.0)
        
        return result
    
    def breath_filter(self, signal: np.ndarray) -> np.ndarray:
        """
        呼吸信号滤波 (0.1-1Hz)
        
        Args:
            signal: 呼吸阻抗信号
            
        Returns:
            滤波后信号
        """
        try:
            return filtfilt(self.b_breath, self.a_breath, signal)
        except Exception:
            return signal
    
    def apply_filter(self, signal: np.ndarray, 
                     filter_type: str = 'ecg',
                     **kwargs) -> np.ndarray:
        """
        应用指定类型的滤波
        
        Args:
            signal: 输入信号
            filter_type: 滤波类型 ('notch', 'lowpass', 'highpass', 'bandpass', 'ecg', 'breath')
            **kwargs: 传递给具体滤波函数的参数
            
        Returns:
            滤波后信号
        """
        if filter_type == 'notch':
            return self.notch_filter(signal)
        elif filter_type == 'lowpass':
            return self.lowpass_filter(signal, kwargs.get('cutoff'))
        elif filter_type == 'highpass':
            return self.highpass_filter(signal, kwargs.get('cutoff'))
        elif filter_type == 'bandpass':
            return self.bandpass_filter(signal, 
                                        kwargs.get('lowcut'),
                                        kwargs.get('highcut'))
        elif filter_type == 'ecg':
            return self.ecg_filter(signal,
                                   kwargs.get('remove_baseline', True),
                                   kwargs.get('remove_50hz', True))
        elif filter_type == 'breath':
            return self.breath_filter(signal)
        else:
            return signal
    
    def set_sampling_rate(self, sampling_rate: int):
        """
        设置采样率并重新设计滤波器
        
        Args:
            sampling_rate: 新的采样率
        """
        self.sampling_rate = sampling_rate
        self._design_filters()
    
    def get_filter_response(self, filter_type: str = 'ecg', 
                            num_points: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """
        获取滤波器频率响应 (用于调试)
        
        Args:
            filter_type: 滤波类型
            num_points: 频率点数
            
        Returns:
            (频率数组，增益数组 dB)
        """
        from scipy.signal import freqz
        
        if filter_type == 'notch':
            b, a = self.b_notch, self.a_notch
        elif filter_type == 'lowpass':
            b, a = self.b_low, self.a_low
        elif filter_type == 'highpass':
            b, a = self.b_high, self.a_high
        elif filter_type == 'bandpass':
            b, a = self.b_band, self.a_band
        elif filter_type == 'breath':
            b, a = self.b_breath, self.a_breath
        else:
            b, a = self.b_band, self.a_band
        
        # 计算频率响应
        w, h = freqz(b, a, worN=num_points)
        
        # 转换为频率 (Hz)
        freqs = w * self.sampling_rate / (2 * np.pi)
        
        # 转换为 dB
        gain_db = 20 * np.log10(np.abs(h) + 1e-10)
        
        return freqs, gain_db
