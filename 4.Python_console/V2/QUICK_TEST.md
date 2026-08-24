# ECG Viewer 快速测试指南

## 快速开始 (3 步测试)

### 步骤 1: 打开 ECG Viewer
```bash
cd F:\FE\ecg_viewer
python main.py
```

### 步骤 2: 运行模拟器
```bash
# 在新命令行窗口中运行
python test_ecg_auto.py
```

### 步骤 3: 在 ECG Viewer 中连接串口
1. 选择串口 (与模拟器相同的 COM 口)
2. 波特率：115200
3. 点击"打开串口"

**完成!** 你应该看到 4 个通道的 ECG 波形。

---

## 模拟器说明

### 生成的波形

**CH1-CH3: ECG 心电图**
- 正常窦性心律
- 包含 P 波、QRS 波群、T 波
- 心率：75 BPM
- 幅值：约 1 mV

**CH4: 呼吸阻抗**
- 正弦波
- 频率：0.25 Hz (15 次/分钟)
- 模拟呼吸引起的阻抗变化

### 协议参数

```
采样率：500 SPS (每秒 500 个样本)
帧格式：每帧 10 个样本 × 4 通道
帧率：50 FPS (500/10)
波特率：115200 bps
```

---

## 测试工具

| 文件 | 说明 | 使用方式 |
|------|------|----------|
| `test_ecg_auto.py` | 自动测试模式 | `python test_ecg_auto.py` |
| `test_ecg_loopback.py` | 回环测试 (需交互) | `python test_ecg_loopback.py` |
| `test_simulator.bat` | 批处理启动脚本 | 双击运行 |
| `TEST_GUIDE.md` | 完整测试指南 | 阅读参考 |

---

## 预期结果

### 正常显示
- ✅ CH1-CH3 显示周期性 ECG 波形
- ✅ R 波峰值约 1000 μV
- ✅ 心率显示 70-80 BPM
- ✅ CH4 显示缓慢变化的呼吸波
- ✅ 状态栏显示正常帧率 (约 50 FPS)
- ✅ 误码率为 0

### 异常情况及解决

**问题 1: 无波形显示**
- 检查串口是否选择正确
- 确认串口已打开
- 查看状态栏是否有误码

**问题 2: 波形杂乱**
- 可能是 CRC 错误
- 检查波特率设置 (应为 115200)
- 重启模拟器

**问题 3: 心率显示异常**
- 等待几秒钟让算法收敛
- 检查波形是否正常
- 确认采样率设置正确

---

## 高级测试

### 使用虚拟串口

安装 com0com 或 VSPD 创建串口对 (如 COM3 <-> COM4)

```bash
# 终端 1: 运行模拟器
python test_ecg_simulator.py
# 选择 COM3

# 终端 2: 运行 ECG Viewer
python main.py
# 选择 COM4
```

### 修改心率

编辑 `test_ecg_auto.py`:
```python
HEART_RATE = 60  # 改为 60 BPM (正常范围 60-100)
```

### 修改采样率

编辑 `test_ecg_auto.py`:
```python
SAMPLE_RATE = 250  # 改为 250 SPS
```

---

## 技术细节

### 数据帧格式

```
帧长度：57 字节
├─ 帧头：2 字节 (0x55 0xAA)
├─ 长度：2 字节 (48)
├─ 源 ID: 1 字节 (0x22)
├─ 目标 ID: 1 字节 (0x20)
├─ 序列号：1 字节 (0-255)
├─ 消息 ID: 1 字节 (0x20)
├─ 数据：48 字节 (10 样本 × 4 通道 × 3 字节)
└─ CRC: 1 字节 (CRC8)
```

### ECG 生成算法

使用高斯函数模拟：
- P 波：σ=0.015, 幅值 0.15 mV
- QRS 波群：σ=0.02, 幅值 1.0 mV
- T 波：σ=0.04, 幅值 0.3 mV

添加：
- 高斯白噪声：σ=0.02 mV
- 基线漂移：0.05 mV (呼吸引起)

---

## 性能测试

运行 10 分钟测试:
```bash
# 记录统计信息
python test_ecg_auto.py
# 运行 10 分钟后按 Ctrl+C

# 查看输出:
# - 发送帧数
# - 平均速率
# - 持续时间
```

**预期性能:**
- 帧率稳定在 50 FPS
- 无丢帧
- CPU 占用 < 5%
- 内存占用 < 100 MB

---

## 故障排除工具

### 查看可用串口
```bash
python -c "from serial.tools import list_ports; print([p.device for p in list_ports.comports()])"
```

### 测试串口连接
```bash
python -c "import serial; s=serial.Serial('COM3', 115200); print('OK' if s.is_open else 'FAIL')"
```

### 协议分析
```bash
# 使用 diagnose.py 诊断
python diagnose.py
```

---

## 联系与支持

如遇到问题:
1. 查看控制台错误信息
2. 检查 `TEST_GUIDE.md` 详细指南
3. 确认所有依赖已安装
