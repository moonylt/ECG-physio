# PHYSIO 通信协议 v2（基于新协议扩展）

适用链路：**STM32F429 ↔ ESP32（UART）↔ PC（WiFi TCP）**，同时兼容 PC 直连串口。
本文档是 STM32 固件、ESP32 固件与 Python 上位机三方的唯一协议依据。

---

## 1. 帧结构（可变长）

```
┌──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬────────┬──────┐
│ STX0 │ STX1 │ LEN_L│ LEN_H│ SRC  │ DST  │ SEQ  │ MSGID│ DATA[N]│ CRC8 │
│ 0x55 │ 0xAA │  N低 │  N高 │ 1B   │ 1B   │ 1B   │ 1B   │  N B   │  1B  │
└──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴────────┴──────┘
```

| 字段 | 说明 |
|------|------|
| STX0/STX1 | 帧同步字 `0x55 0xAA`（注意：旧协议为 `0xAA 0x55`，已废弃） |
| LEN | DATA 载荷字节数，**小端 16 位** |
| SRC | 源地址，见 §2 |
| DST | 目的地址 |
| SEQ | 帧序列号，u8 回绕；接收方据此检测丢帧 |
| MSGID | 消息类型，见 §3 |
| CRC8 | 多项式 0x07、初值 0x00，覆盖**除 CRC 外的全部字节**（含帧头） |

总帧长 = 8（帧头）+ N（DATA）+ 1（CRC）。

## 2. 地址分配

| 地址 | 设备 |
|------|------|
| 0x00 | PC 上位机 |
| 0x01 | ESP32 WiFi 桥 |
| 0x02 | STM32 主控 |

ESP32 透传 STM32 数据时**不改写 SRC/DST/SEQ**，仅做字节转发。

## 3. MSGID 分配

### 3.1 波形数据帧（设备 → PC）

| MSGID | 名称 | DATA 长度 | 载荷 |
|-------|------|-----------|------|
| 0x20 | ADS129X_DATA（ECG/呼吸） | 48 | 4 样本 × 4 通道 × 3B。CH0=呼吸阻抗，CH1~CH3=ECG 导联。24bit 有符号大端 |
| 0x21 | SPO2_PPG_DATA（血氧 PPG） | 24 | 4 样本 × 2 通道 × 3B。CH0=IR，CH1=RED。24bit 有符号大端 |
| 0x22 | SPO2_RESULT（血氧结果） | 8 | SpO2 u16（%×10）、脉率 u16（bpm）、状态 u8、保留 u8。**当前固件不发送此帧**：原始 PPG（0x21）直接上传，SpO2 算法由上位机计算 |
| 0x23 | IBP_DATA（有创血压波形） | 24 | 4 样本 × 2 通道 × 3B。CH0=P1，CH1=P2。24bit 有符号大端 |
| 0x24 | NIBP_RESULT（无创血压结果） | 8 | 收缩压/舒张压/平均压 u16（mmHg×10）、状态 u8、保留 u8 |
| 0x25 | TEMP_DATA（温度遥测） | 17 | 4 × f32（体表/肛温/加热板/冷结）+ 状态位 u8 |
| 0x26 | LEADOFF_STATUS（导联脱落） | 2 | 通道脱落位掩码 u16，bit0~bit15 对应通道 0~15，1=脱落 |

波形帧每帧固定 4 个样本，帧率 = 采样率 / 4。

**TEMP_DATA 状态位（u8）**：
`bit0` 体表探头在位、`bit1` 肛温探头在位、`bit2` 加热板过温告警、`bit3` 热电偶开路。

### 3.2 设备状态与配置（双向）

| MSGID | 名称 | 方向 | DATA 长度 | 载荷 |
|-------|------|------|-----------|------|
| 0xF0 | DEVICE_STATUS | 设备→PC | 4 | accessory 掩码 u16（见下）+ 固件版本 u8 + 错误码 u8 |
| 0xA0 | SET_GAIN | PC→设备 | 2 | 通道号 u8 + 增益码 u8 |
| 0xA1 | SET_TEMP_TARGET | PC→设备 | 4 | 目标温度 f32 |
| 0xA2 | START_ACQ / STOP_ACQ | PC→设备 | 1 | 0x01=启动，0x00=停止，bit4~7 选择 accessory 组。当前实现：bit0 控制波形流（0x20/0x21）启停，温度遥测与 PID 恒温不受影响 |

**DEVICE_STATUS accessory 掩码（u16）**：

| bit | accessory | 对应硬件 |
|-----|-----------|----------|
| 0 | ECG/呼吸 | ADS1298R（隔离域，U144） |
| 1 | 血氧 | AFE4490（U1，SPI4） |
| 2 | 体表温度 | TMP117 |
| 3 | 肛温 | MAX31856 热电偶（SPI2） |
| 4 | 有创血压 | IBP 输入 |
| 5 | 无创血压 | NIBP 模块 |
| 6 | 加热板 | PNP Heater + PID |
| 7~15 | 保留 | — |

设备上线、accessory 插拔变化时应主动发送 DEVICE_STATUS，PC 也可请求。

## 4. 旧协议（已废弃，仅供对照）

STM32 旧 118 字节帧（`0xAA 0x55` + TLV + 固定校验 0x89，经 SPI5→USM USB 桥输出）
随 V1 上位机一并废弃，新固件不再实现。

## 5. 参考实现

- 帧常量与打包/解析（C）：`3.FIRMWARE/protocol.h`
- Python 解析：`4.Python_console/V2/comms/protocol_parser.py`
- ESP32 模拟发送（0x20）：`3.FIRMWARE/2.ESP32/ecg_wifi_bridge/main/ecg_bridge_main.c`
