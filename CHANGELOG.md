# Changelog

本文件记录 ECG-physio 各版本的显著变更。格式参考 [Keep a Changelog](https://keepachangelog.com/)。

## [1.0.0] - 2026-08-26

首个完整版本：协议 v2 端到端链路 + 自动整定的恒温控制。

### Added
- **协议 v2**：`0x55 0xAA` 可变长帧（LEN/SRC/DST/SEQ/MSGID/CRC8-poly0x07），
  覆盖 ECG/呼吸、SpO2 PPG 与结果、IBP/NIBP、温度遥测、导联脱落、设备状态
  及 PC 下行命令。STM32 与 Python 共享同一份帧定义（`3.FIRMWARE/protocol.h`）。
- **端到端数据链路**：STM32 → UART5@819200（32.768MHz APB 下零误差分频）→
  ESP32 WiFi 桥（透明转发）→ PC 上位机。实测 ~150 fps、CRC 零错。
- **AFE4490 SpO2 前端驱动**：自 LPC177x 旧工程移植并精简（SPI4，TIM8 8.197MHz 时钟）。
- **加热板 PID 重写**：前馈 + 条件积分抗饱和 + 过零积分泄放 + 微分先行 +
  输出斜率限制；全部参数为运行时可写全局量（J-Link RAM 写入免重编译）。
  实测：设定值阶跃过冲 ≤0.01℃，冷启动 29→38℃ 零过冲、稳态纹波 ±0.04℃。
- **上位机**：长度自适应协议解析器、30 分钟滚动温度曲线、可读状态栏、
  float32 波形缓冲（修复 pyqtgraph 整型溢出）。
- **命令行工具链**：零依赖 `build.py`（SIM=0/1 双模式）与 `flash.py`
  （J-Link 自动烧录），配套 FLASH_GUIDE.md / TOOLCHAIN.md。
- **模拟数据固件**（SIM=1 默认）：无需硬件即可验证上位机全功能。

### Fixed
- 修复 `physio_app.c` 注释结束符丢失导致 SIM=0（真实采集模式）编译失败、
  CH0 呼吸通道被静默丢弃的缺陷（曾随 921e29d 发布）。
- ESP32 桥任务栈溢出（Guru Meditation StoreProhibited）：缓冲区静态化 + 6KB 栈。
- 热电偶开路读数 404℃：加入合理性门限 + TC_OPEN 状态位。
- 波特率体系统一为 819200（16.384MHz HSE 时钟树下 BRR=40 精确分频）。

### Changed
- 移除未使用的双传感器 PID 遗留 API（RSencer/LSencer）；两种 SIM 模式零编译警告。
- 固件注释全面英文化；README/PROTOCOL/FLASH_GUIDE 路径与事实核对修正。

## 早期版本（1.0.0 之前）

项目前身包含 ECG 信号处理算法调研、Python 控制台 V1、ESP32 WiFi 桥初版
及四通道模拟波形等迭代，详见 git 历史。
