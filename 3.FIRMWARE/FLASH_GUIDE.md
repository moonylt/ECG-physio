# PHYSIO 烧录与联调教程

完整链路三件套：**STM32（主控）→ ESP32（WiFi 桥）→ 上位机（PC）**。
全部烧好后：PC 连 WiFi 热点 `ECG-Physio` → 打开上位机 → 看到 4 通道模拟波形 + SpO2/温度。

---

## 0. 前提条件

| 项目 | 说明 |
|------|------|
| J-Link | 已装 SEGGER 驱动（本机 V6.30j，`C:\Program Files (x86)\SEGGER\JLink_V630j`），SWD 线接主板调试口 |
| 主板供电 | DC 座上电（只插 J-Link 不会给整板供电，VTref 应为 3.3V） |
| ESP32 烧录 | 一根 USB 转串口线（板上有 H1 排针：TXD/RXD），或你惯用的烧录器 |
| Python | 上位机用 `4.Python console/V2/venv`（已建好） |

## 1. STM32 编译与烧录（本机即可完成）

```bash
cd "F:\ECG-physio\3.FIRMWARE\1.ST MCU\Physio"

python build.py            # 编译（默认模拟数据模式）
python build.py SIM=0      # 编译真实采集模式（联调通过后再切）
python build.py clean      # 清理
```

输出在 `build/` 下：`Physio.bin`（裸二进制）、`Physio.hex`（带地址，烧录用它）、`Physio.elf`（调试符号）。

烧录（自动选 J-Link）：

```bash
python flash.py            # 烧录 + 校验 + 复位运行
python flash.py erase      # 全片擦除（需要时）
python flash.py openocd    # 备用：ST-Link/OpenOCD 路径
```

**成功的标志**：J-Link 输出 `Flash download: ... O.K.`，随后自动复位。
**验证运行**（可选）：设备应每秒发出约 150 帧数据，可用 J-Link 读计数器：

```bash
printf 'mem32 0x200007A0 1\nmem8 0x2000028A 1\nSleep 1000\nmem32 0x200007A0 1\nmem8 0x2000028A 1\nqc\n' | "C:\Program Files (x86)\SEGGER\JLink_V630j\JLink.exe" -device STM32F429ZG -if SWD -speed 4000 -autoconnect 1
```

两个 `uwTick`（0x200007A0）读数差约 1000，`phy_tx_seq`（0x2000028A）差约 150 即正常。

> 注意：这两个 RAM 地址是符号地址，**每次重编译都可能漂移**。地址失配时用
> `F:/stm32-tools/gcc/bin/arm-none-eabi-nm build/Physio.elf | grep -E "uwTick|phy_tx_seq"`
> 重新定位后再读。

> 注意：编译脚本零依赖（不需要 make/CubeIDE），工具链在 `F:\stm32-tools`。
> 如果以后改了代码，直接重跑 `python build.py && python flash.py` 即可。

## 2. ESP32 重烧（波特率默认值已改，必须全量重建）

本轮把 UART 波特率从 921600 改为 **819200**（STM32 侧 32.768MHz APB 时钟下零误差分频），
该默认值在 `sdkconfig.defaults` 里，**只有删掉旧 sdkconfig 才会生效**：

```bash
cd "F:\ECG-physio\3.FIRMWARE\2.ESP32\ecg_wifi_bridge"

idf.py fullclean           # 或者手动删除 sdkconfig 文件
idf.py set-target esp32    # 若之前没设过 target
idf.py build
idf.py -p COM5 flash       # 端口号按设备管理器实际显示（COMx）
idf.py -p COM5 monitor     # 看启动日志，Ctrl+] 退出
```

烧录前核对两处配置（`idf.py menuconfig` → Example Configuration）：

| 配置 | 正确值 | 说明 |
|------|--------|------|
| Data Mode | **1** | 真实数据模式：转发 STM32 的 UART 数据（0=ESP32 自产模拟波） |
| UART Baud Rate | **819200** | 必须与 STM32 一致 |

### 进下载模式（板上 ESP32 无自动下载电路，需手动）

esptool 报 `Wrong boot mode detected (0x13)` 时，说明芯片没进下载模式。板上按键：
**SW2 = BOOT（接 IO0），SW1 = RST（接 EN）**。操作：

1. 运行 `idf.py -p COMx flash`，等它打印 `Connecting...`
2. **按住 SW2 不松 → 短按一下 SW1 → 松开 SW2**
3. 立即开始烧写

没有按键时：把 H1 排针第 4 脚（IO0）短接 GND，复位一次，烧完拆线。

烧录串口接线（H1）：适配器 TX→H1.3，RX→H1.2，共地。

正常启动日志应显示：`Running in UART DATA mode`、SoftAP `ECG-Physio`、`TCP Server listening on port 12345`。

> ESP32-WROVER 模组（板上 U16）如烧录失败，检查 Flash 型号设置（WROVER-IE 8MB）。

## 3. 上位机连接

1. PC 连接 WiFi 热点 **ECG-Physio**（开放网络，无密码）
2. 启动上位机：

```bash
cd "F:\ECG-physio\4.Python console\V2"
venv\Scripts\python.exe main.py
```

3. 在界面 WiFi 面板连接 `192.168.4.1:12345`
4. **预期看到**：4 通道波形滚动（CH1 呼吸正弦、CH2~CH4 为 450bpm 的 PQRST 心电）、
   状态栏 SpO2 98%、温度 皮37.5/肛38.2/板40.0、Rx 计数增长

## 4. 切换到真实采集

上位机跑通后：

```bash
cd "F:\ECG-physio\3.FIRMWARE\1.ST MCU\Physio"
python build.py SIM=0 && python flash.py
```

真实模式会启用 ADS1298R（ECG 中断）、AFE4490（血氧）、TMP117/MAX31856（温度）。
探头没接的通道波形为平线属于正常。

## 5. 常见问题排查

| 现象 | 原因与处理 |
| ESP32 烧录报 `Wrong boot mode (0x13)` | 芯片没进下载模式：按住 SW2(BOOT) → 点按 SW1(RST) → 松开 SW2（详见第 2 节） |
|------|-----------|
| J-Link 报 `VTref = 0.000V` | 主板没上电，或 SWD 排线没接 VTref（1 脚） |
| `Cannot connect to target` | SWD 线序错/松动；把速度降到 `-speed 1000` 重试 |
| ESP32 日志乱码 | 串口监视器波特率与日志口不符（115200/74880 常见），与数据口无关 |
| 上位机无波形 | ① TCP 没连上（ping 192.168.4.1）② ESP32 仍是旧固件（没 fullclean，波特率不匹配 → 重新走第 2 步）③ STM32 没在发（回第 1 步验证帧率） |
| 波形有但 CRC 错误计数增长 | 数据链路误码，检查 UART 接线/波特率一致性 |
| STM32 编译报找不到 gcc | 工具链被移动，设置环境变量 `ARM_GCC_BIN` 指向新的 bin 目录 |

## 6. GDB 调试（可选，进阶）

```bash
python flash.py gdb                                    # 终端1: J-Link GDB Server :2331
F:\stm32-tools\gcc\bin\arm-none-eabi-gdb.exe build\Physio.elf   # 终端2
  (gdb) target remote :2331
  (gdb) monitor reset halt
  (gdb) break physio_app_poll
  (gdb) continue
```

详细用法见 `TOOLCHAIN.md`。
