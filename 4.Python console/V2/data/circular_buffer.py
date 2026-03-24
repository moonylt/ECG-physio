# -*- coding: utf-8 -*-
"""
循环缓冲区
用于存储 ECG 数据，支持实时显示
"""

import numpy as np


class CircularBuffer:
    """
    循环缓冲区
    支持多通道数据存储
    """

    def __init__(self, max_points: int = 5000, num_channels: int = 4):
        """
        初始化循环缓冲区

        Args:
            max_points: 最大数据点数
            num_channels: 通道数
        """
        self.max_points = max_points
        self.num_channels = num_channels

        # 数据存储
        self.data = np.zeros((max_points, num_channels), dtype=np.float32)
        self.index = 0
        self.count = 0

    def add_data(self, samples: np.ndarray):
        """
        添加数据

        Args:
            samples: 数据数组，shape=(num_samples, num_channels)
        """
        num_samples = len(samples)

        for i in range(num_samples):
            self.data[self.index] = samples[i]
            self.index = (self.index + 1) % self.max_points
            if self.count < self.max_points:
                self.count += 1

    def get_channel_data(self, channel: int, num_points: int = None) -> np.ndarray:
        """
        获取单个通道的数据

        Args:
            channel: 通道索引 (0-based)
            num_points: 要获取的点数，None 表示全部

        Returns:
            数据数组
        """
        if num_points is None or num_points > self.count:
            num_points = self.count

        if self.count < self.max_points:
            # 缓冲区未满
            return self.data[:self.count, channel].copy()
        else:
            # 缓冲区已满，需要按正确顺序返回
            result = np.zeros(num_points)
            start = (self.index - num_points) % self.max_points
            for i in range(num_points):
                result[i] = self.data[(start + i) % self.max_points, channel]
            return result

    def get_all_channels(self) -> np.ndarray:
        """
        获取所有通道的数据

        Returns:
            数据数组，shape=(num_points, num_channels)
        """
        if self.count < self.max_points:
            return self.data[:self.count].copy()
        else:
            # 重新排列数据
            result = np.zeros_like(self.data)
            result[:self.max_points - self.index] = self.data[self.index:]
            result[self.max_points - self.index:] = self.data[:self.index]
            return result

    def get_length(self) -> int:
        """获取当前数据点数"""
        return self.count

    def clear(self):
        """清空缓冲区"""
        self.data.fill(0)
        self.index = 0
        self.count = 0