# -*- coding: utf-8 -*-
"""
数据保存模块
支持 CSV、EDF、MAT 等格式
"""

import os
import json
from datetime import datetime


class DataSaver:
    """
    数据保存器
    支持多种格式保存 ECG 数据
    """

    def __init__(self, output_dir: str = None):
        """
        初始化数据保存器

        Args:
            output_dir: 输出目录，默认为当前目录下的 data 文件夹
        """
        self.output_dir = output_dir or os.path.join(os.getcwd(), 'data')
        os.makedirs(self.output_dir, exist_ok=True)

    def save_to_csv(self, data, filename: str = None, sampling_rate: int = 500,
                    metadata: dict = None) -> str:
        """
        保存为 CSV 格式

        Args:
            data: 数据数组，shape=(num_points, num_channels)
            filename: 文件名
            sampling_rate: 采样率
            metadata: 元数据

        Returns:
            保存的文件路径
        """
        if filename is None:
            filename = f"ecg_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        filepath = os.path.join(self.output_dir, filename)

        import numpy as np
        num_points, num_channels = data.shape

        with open(filepath, 'w', encoding='utf-8') as f:
            # 写入元数据
            if metadata:
                f.write(f"# Metadata: {json.dumps(metadata)}\n")
            f.write(f"# Sampling Rate: {sampling_rate} Hz\n")
            f.write(f"# Timestamp: {datetime.now().isoformat()}\n")

            # 写入表头
            headers = ['Time(s)'] + [f'CH{i+1}' for i in range(num_channels)]
            f.write(','.join(headers) + '\n')

            # 写入数据
            for i, row in enumerate(data):
                time_val = i / sampling_rate
                line = f"{time_val:.6f}," + ','.join(f"{v:.6f}" for v in row)
                f.write(line + '\n')

        return filepath

    def save_to_edf(self, data, filename: str = None, sampling_rate: int = 500,
                    patient_info: dict = None) -> str:
        """
        保存为 EDF 格式 (欧洲数据格式)

        Args:
            data: 数据数组
            filename: 文件名
            sampling_rate: 采样率
            patient_info: 患者信息

        Returns:
            保存的文件路径
        """
        if filename is None:
            filename = f"ecg_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.edf"

        filepath = os.path.join(self.output_dir, filename)

        # EDF 格式需要特定结构，这里提供简化实现
        # 实际应用中应使用 pyedflib 库

        try:
            import pyedflib
            # 使用 pyedflib 库保存
            num_points, num_channels = data.shape
            duration = num_points / sampling_rate

            with pyedflib.EdfWriter(filepath, num_channels, pyedflib.FILETYPE_EDFPLUS) as f:
                f.setPatientCode(patient_info.get('id', 'X') if patient_info else 'X')
                f.setPatientName(patient_info.get('name', 'X') if patient_info else 'X')

                for ch in range(num_channels):
                    channel_info = {
                        'label': f'CH{ch+1}',
                        'dimension': 'uV',
                        'sample_rate': sampling_rate,
                        'physical_min': -5000,
                        'physical_max': 5000,
                    }
                    f.setSignalHeader(ch, channel_info)
                    f.writePhysicalSamples(data[:, ch])

        except ImportError:
            # 如果没有 pyedflib，保存为简单文本格式
            with open(filepath, 'w') as f:
                f.write(f"# ECG Data (EDF-like format)\n")
                f.write(f"# Sampling Rate: {sampling_rate} Hz\n")
                for row in data:
                    f.write(' '.join(f"{v:.2f}" for v in row) + '\n')

        return filepath

    def save_to_mat(self, data, filename: str = None, sampling_rate: int = 500,
                    metadata: dict = None) -> str:
        """
        保存为 MATLAB .mat 格式

        Args:
            data: 数据数组
            filename: 文件名
            sampling_rate: 采样率
            metadata: 元数据

        Returns:
            保存的文件路径
        """
        if filename is None:
            filename = f"ecg_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mat"

        filepath = os.path.join(self.output_dir, filename)

        try:
            from scipy.io import savemat

            mat_data = {
                'ecg_data': data,
                'sampling_rate': sampling_rate,
                'timestamp': datetime.now().isoformat(),
            }
            if metadata:
                mat_data['metadata'] = metadata

            savemat(filepath, mat_data)

        except ImportError:
            raise ImportError("scipy 库未安装，无法保存 .mat 文件")

        return filepath

    def export_report(self, data, filename: str = None,
                      heart_rate: float = 0, breath_rate: float = 0,
                      metadata: dict = None) -> str:
        """
        导出分析报告 (JSON 格式)

        Args:
            data: 数据数组
            filename: 文件名
            heart_rate: 心率
            breath_rate: 呼吸率
            metadata: 元数据

        Returns:
            保存的文件路径
        """
        if filename is None:
            filename = f"ecg_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = os.path.join(self.output_dir, filename)

        import numpy as np

        report = {
            'timestamp': datetime.now().isoformat(),
            'data_points': len(data),
            'channels': data.shape[1] if len(data.shape) > 1 else 1,
            'heart_rate_bpm': heart_rate,
            'breath_rate_rpm': breath_rate,
            'statistics': {},
        }

        # 计算统计信息
        if len(data) > 0:
            for ch in range(data.shape[1] if len(data.shape) > 1 else 1):
                ch_data = data[:, ch] if len(data.shape) > 1 else data
                report['statistics'][f'CH{ch+1}'] = {
                    'mean': float(np.mean(ch_data)),
                    'std': float(np.std(ch_data)),
                    'min': float(np.min(ch_data)),
                    'max': float(np.max(ch_data)),
                }

        if metadata:
            report['metadata'] = metadata

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return filepath


class ScreenshotSaver:
    """截图保存器"""

    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(os.getcwd(), 'screenshots')
        os.makedirs(self.output_dir, exist_ok=True)

    def save(self, pixmap, filename: str = None) -> str:
        """
        保存截图

        Args:
            pixmap: QPixmap 对象
            filename: 文件名

        Returns:
            保存的文件路径
        """
        if filename is None:
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        filepath = os.path.join(self.output_dir, filename)
        pixmap.save(filepath, 'PNG')

        return filepath