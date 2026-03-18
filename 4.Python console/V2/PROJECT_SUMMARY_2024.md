# ECG Viewer 项目摘要

## 项目概览

**ECG Viewer** 是一款基于 Python 的心电信号（ECG）上位机软件，专为 ADS1294R 硬件设计。提供实时波形显示、生理参数检测、数据记录和多种医疗标准格式导出功能。

---

## 技术栈

| 类别 | 技术 |
|------|------|
| **语言** | Python 3.11 |
| **GUI 框架** | PyQt5 |
| **数据处理** | NumPy, SciPy |
| **波形绘制** | pyqtgraph |
| **串口通信** | pyserial |
| **打包工具** | PyInstaller |

---

## 核心功能

### 1. 数据采集
- ✅ 串口通信（支持 9600-921600 波特率）
- ✅ 57 字节协议解析（CRC8 校验）
- ✅ 4 通道同步采集（24 位分辨率）

### 2. 波形显示
- ✅ 4 通道独立波形显示
- ✅ 30 FPS 实时刷新
- ✅ 自动缩放和增益调整
- ✅ 性能优化（禁用抗锯齿、下采样）

### 3. 生理参数检测
- ✅ 心率检测（500 SPS，基于 CH2）
- ✅ 呼吸率检测（基于 CH1 阻抗）
- ✅ 正常/异常范围提示（颜色编码）

### 4. 信号处理
- ✅ 50/60 Hz 工频陷波
- ✅ 0.5 Hz 高通滤波（基线漂移校正）
- ✅ 40 Hz 低通滤波（噪声抑制）

### 5. 数据导出
| 格式 | 用途 | 兼容性 |
|------|------|--------|
| **CSV** | 通用数据 | Excel, pandas |
| **EDF** | 医学标准 | EDFBrowser, BioSig |
| **MATLAB** | 科研分析 | MATLAB, Octave |
| **JSON** | 统计报告 | 任意文本编辑器 |

### 6. 可配置参数
- **采样率**: 250/500/1000/2000 SPS
- **波特率**: 9600-921600 bps
- **数据位**: 7/8 位
- **停止位**: 1/2 位
- **校验位**: N/E/O

---

## 协议规格

### 帧格式（57 字节）

```
┌──────┬──────┬─────────┬─────┬─────┬─────┬──────┬────────┬──────────┬─────┐
│ STX0 │ STX1 │   LEN   │ SRC │ DST │ SEQ │ MSGID │  DATA  │   CRC    │
│ 1B   │ 1B   │  2B     │ 1B  │ 1B  │ 1B  │  1B   │  48B   │   1B     │
│ 0x55 │ 0xAA │ 0x0030  │0x22 │0x20 │  N  │ 0x20  │ 样本数据│ CRC8-CCITT│
└──────┴──────┴─────────┴─────┴─────┴─────┴──────┴────────┴──────────┴─────┘
```

### 数据载荷（48 字节）

```
4 样本 × 4 通道 × 3 字节/通道 = 48 字节

每样本结构:
[CH1_24bit_MSb][CH2_24bit_MSb][CH3_24bit_MSb][CH4_24bit_MSb]

通道定义:
- CH1: 呼吸阻抗 (Breath Impedance)
- CH2: RA 导联 (Right Arm - ECG)
- CH3: LA 导联 (Left Arm - ECG)
- CH4: LL 导联 (Left Leg - ECG)
```

### 时序参数

- **采样率**: 500 SPS（默认）
- **帧率**: 125 FPS（500 ÷ 4 样本/帧）
- **帧间隔**: 8 ms

---

## 项目结构

```
F:\FE\ecg_viewer\
├── main.py                 # 主入口（支持--test 参数）
├── requirements.txt        # Python 依赖
├── build_exe.bat          # PyInstaller 打包脚本
├── ECG Viewer.spec        # PyInstaller 配置文件
│
├── comms/                 # 通信模块
│   ├── serial_manager.py  # 串口管理
│   └── protocol_parser.py # 协议解析（4 样本/帧）
│
├── ui/                    # 用户界面
│   ├── main_window.py     # 主窗口
│   ├── serial_panel.py    # 串口配置面板（含采样率选择）
│   ├── waveform_widget.py # 波形显示（性能优化）
│   ├── fft_widget.py      # FFT 频谱
│   └── status_bar.py      # 状态栏和控制面板
│
├── signal_processing/     # 信号处理
│   ├── filter.py          # 数字滤波器
│   ├── heart_rate.py      # 心率检测
│   └── breath_rate.py     # 呼吸率检测
│
├── data/                  # 数据管理
│   ├── circular_buffer.py # 环形缓冲区
│   └── data_saver.py      # 数据导出（CSV/EDF/MAT/JSON）
│
├── utils/                 # 工具函数
│   └── crc8.py           # CRC8 校验
│
├── saves/                 # 数据保存目录
├── screenshots/           # 截图保存目录
└── venv/                  # Python 虚拟环境
```

---

## 关键文件修改历史

### 2024-01-01 最新改进

1. **数据导出增强** (`data/data_saver.py`)
   - 新增 EDF 格式支持（医学标准）
   - 新增 MATLAB 格式支持
   - 新增 JSON 统计报告
   - 新增分通道导出

2. **UI 改进** (`ui/status_bar.py`)
   - 导出按钮改为下拉菜单
   - 新增 4 种导出选项

3. **采样率配置** (`ui/serial_panel.py`)
   - 新增采样率选择器（250/500/1000/2000 SPS）
   - 信号连接到主窗口

4. **性能优化** (`ui/waveform_widget.py`)
   - 禁用抗锯齿提高渲染速度
   - 启用自动下采样
   - 禁用不必要的鼠标交互
   - 批量更新优化

5. **文档修复**
   - 修正所有"10 样本"注释为"4 样本"
   - 更新协议文档
   - 创建用户指南 (USER_GUIDE.md)

---

## 运行命令

### 开发模式
```bash
cd F:\FE\ecg_viewer
call venv\Scripts\activate.bat
python main.py
```

### 测试模式（无硬件）
```bash
python main.py --test
```

### 打包 EXE
```bash
build_exe.bat
```

### 运行测试
```bash
python test_ecg_auto.py      # 串口模拟器
python test_ecg_direct.py    # 直接注入测试
```

---

## 已知问题与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| numpy C 扩展缺失 | PyInstaller 未包含 | 使用--collect-all numpy |
| 模块命名冲突 | signal 与标准库冲突 | 重命名为 signal_processing |
| 帧格式不匹配 | 文档 10 样本 vs 实际 4 样本 | 统一修改为 4 样本 |
| CRC 错误 | 多项式或表错误 | 使用标准 CRC8-CCITT |

---

## 待办事项 (TODO)

### 短期目标
- [ ] 多语言支持（中文/英文）
- [ ] 电极脱落检测
- [ ] 数据回放功能
- [ ] 网络传输支持（TCP/UDP）

### 长期目标
- [ ] 12 导联 ECG 支持
- [ ] AI 心律失常检测
- [ ] 云端数据存储
- [ ] 移动端 App

---

## 测试验证

### 虚拟串口测试
- **工具**: com0com / VSPD
- **配置**: COM4 ↔ COM5
- **结果**: ✅ 1609+ 帧，0 CRC 错误，125 FPS

### 性能指标
- **CPU 使用率**: < 5%
- **内存占用**: ~150 MB
- **刷新率**: 30 FPS（波形）
- **延迟**: < 100 ms

---

## 依赖版本

```
PyQt5==5.15.9
pyqtgraph==0.13.3
numpy==1.24.3
scipy==1.10.1
pyserial==3.5
pyinstaller==5.13.0
```

---

## 联系与支持

- **项目位置**: F:\FE\ecg_viewer
- **文档**: USER_GUIDE.md, README.md
- **测试指南**: TEST_GUIDE.md, QUICK_TEST.md

---

**最后更新**: 2024-01-01  
**版本**: 1.0.0
