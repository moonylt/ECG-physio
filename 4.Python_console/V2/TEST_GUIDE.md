# ECG Viewer 测试指南

## 概述
本文档说明如何使用 ECG 数据模拟器测试 ECG Viewer 上位机软件。

## 测试场景

### 场景 1: 使用虚拟串口测试 (推荐)

#### 1. 安装虚拟串口驱动

**方法 A: com0com (免费，Windows)**
1. 下载：http://com0com.sourceforge.net/
2. 安装后运行 "Setup Command Prompt"
3. 创建串口对：`install CNCA1 PortName=COM3` 和 `install CNCA2 PortName=COM4`
4. 或使用 GUI 工具 `hcnc` 创建串口对

**方法 B: VSPD (Virtual Serial Port Driver)**
1. 下载：https://www.eltima.com/products/vspdxp-free/
2. 安装后创建串口对 (如 COM3 <-> COM4)

#### 2. 测试步骤

```bash
# 步骤 1: 启动 ECG 模拟器
cd F:\FE\ecg_viewer
test_simulator.bat

# 步骤 2: 在模拟器中选择 COM3 (虚拟串口的一端)

# 步骤 3: 打开 ECG Viewer
python main.py

# 步骤 4: 在 ECG Viewer 中选择 COM4 (虚拟串口的另一端)

# 步骤 5: 点击"打开串口"按钮
```

#### 3. 预期结果
- 看到 4 个通道的 ECG 波形
- CH1-CH3: 心电图波形 (P 波、QRS 波群、T 波)
- CH4: 呼吸波形 (正弦波)
- 心率显示约 75 BPM
- 呼吸率显示约 15 RPM

---

### 场景 2: 使用真实硬件测试

#### 1. 连接硬件
- 使用 USB 转串口适配器连接下位机
- 记录 COM 端口号 (如 COM5)

#### 2. 测试步骤
```bash
# 打开 ECG Viewer
python main.py

# 选择对应的 COM 端口
# 点击"打开串口"按钮
```

#### 3. 预期结果
- 看到真实的 ECG 波形
- 心率、呼吸率正常显示

---

### 场景 3: 回环测试模式

此模式直接发送数据到指定串口，用于验证协议解析。

```bash
# 运行回环测试
python test_ecg_loopback.py

# 按提示选择串口号
# 在 ECG Viewer 中打开相同的串口
```

---

## 模拟器参数

### 可配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 采样率 | 500 SPS | 每秒采样数 |
| 心率 | 75 BPM | 模拟心跳速率 |
| 波特率 | 115200 | 串口通信速率 |

### 波形特征

**ECG 波形 (CH1-CH3):**
- P 波：0.15 mV
- QRS 波群：1.0 mV (R 波峰值)
- T 波：0.3 mV
- 基线漂移：±0.05 mV (呼吸引起)

**呼吸波形 (CH4):**
- 频率：0.25 Hz (15 次/分钟)
- 幅值：50,000 (任意单位)

---

## 协议格式

模拟器按照实际硬件协议发送数据：

```
帧格式 (57 字节):
[STX0][STX1][LEN_L][LEN_H][SRC][DST][SEQ][MSGID][DATA(48B)][CRC]

字段说明:
- STX0/STX1: 帧头 (0x55/0xAA)
- LEN: 数据长度 (48 字节)
- SRC: 源 ID (0x22)
- DST: 目标 ID (0x20)
- SEQ: 序列号 (0-255 循环)
- MSGID: 消息类型 (0x20)
- DATA: 10 个样本 × 4 通道 × 3 字节
- CRC: CRC8 校验
```

---

## 故障排除

### 问题 1: 找不到串口
**解决:**
- 检查虚拟串口驱动是否安装
- 使用 `device manager` 查看可用 COM 端口
- 确保没有其他程序占用串口

### 问题 2: 波形不显示
**解决:**
- 确认串口已正确打开
- 检查波特率设置 (应为 115200)
- 查看状态栏的误码率统计

### 问题 3: 波形杂乱
**解决:**
- 可能是 CRC 错误，检查协议格式
- 确认采样率设置正确
- 重启模拟器和 ECG Viewer

---

## 快速测试脚本

```bash
# 最简单的方式
cd F:\FE\ecg_viewer

# 方式 1: 使用批处理脚本
test_simulator.bat

# 方式 2: 手动运行
python test_ecg_loopback.py

# 方式 3: 使用虚拟串口
run_simulator.bat
```

---

## 性能指标

| 指标 | 目标值 | 实测值 |
|------|--------|--------|
| 数据帧率 | 50 FPS | - |
| 显示延迟 | < 100ms | - |
| CPU 占用 | < 10% | - |
| 内存占用 | < 200MB | - |

---

## 相关文件

- `test_ecg_loopback.py`: 回环测试模拟器
- `test_ecg_simulator.py`: 虚拟串口模拟器
- `test_simulator.bat`: 快速启动脚本
- `run_simulator.bat`: 虚拟串口启动脚本
- `comms/protocol_parser.py`: 协议解析器
- `utils/crc8.py`: CRC8 校验工具

---

## 联系支持

如有问题，请检查:
1. ECG Viewer 日志输出
2. 模拟器控制台信息
3. 串口连接状态
