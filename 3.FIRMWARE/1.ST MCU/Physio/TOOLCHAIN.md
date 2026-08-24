# STM32 命令行工具链（无需 CubeIDE）

本目录的固件可以用纯命令行工具链编译、烧录、调试，
适合脚本化和 AI 辅助开发（ZCode 可自主完成 编译→修错→烧录→调试 闭环）。

## 工具组成（安装位置 F:\stm32-tools）

| 工具 | 用途 | 来源 |
|------|------|------|
| xpack arm-none-eabi-gcc 15.x | 编译/链接/objcopy（含 GDB） | github.com/xpack-dev-tools/arm-none-eabi-gcc-xpack |
| SEGGER J-Link V6.30j（已装） | 烧录 + GDB Server（首选，SWD） | C:\Program Files (x86)\SEGGER |
| xpack OpenOCD 0.12 | 备用烧录/GDB Server（ST-Link） | github.com/xpack-dev-tools/openocd-xpack |

## 日常命令

```bash
cd "3.FIRMWARE/1.ST MCU/Physio"

python build.py            # 编译 → build/Physio.elf/.bin/.hex（零依赖，不需要 make）
python build.py clean      # 清理
python flash.py            # 烧录 build/Physio.hex（自动选 J-Link，烧完复位运行）
python flash.py openocd    # 强制 ST-Link/OpenOCD 烧录 .elf
python flash.py erase      # 全片擦除
python flash.py gdb        # GDB Server: J-Link tcp:2331（无 J-Link 时 OpenOCD tcp:3333）
```

编译宏开关在 `Core/Inc/physio_app.h`：`PHYSIO_SIM_MODE` 1=模拟数据 / 0=真实采集。

## GDB 调试（命令行，J-Link）

```bash
# 终端1: GDB Server
python flash.py gdb

# 终端2: arm-none-eabi-gdb 在 F:\stm32-tools\xpack-arm-none-eabi-gcc-*\bin
arm-none-eabi-gdb build/Physio.elf
  (gdb) target remote :2331
  (gdb) monitor reset halt
  (gdb) break physio_app_poll
  (gdb) continue
  (gdb) bt          # 查看调用栈
  (gdb) p phy_tx_seq
```

AI/脚本一次性批处理（最常用，烧写+断点+回栈一气呵成）：

```bash
arm-none-eabi-gdb -ex "target remote :2331" -ex "monitor reset" -ex "load" \
    -ex "monitor reset halt" -ex "break HardFault_Handler" -ex "continue" \
    -ex "bt" -batch build/Physio.elf
```

## 与 CubeIDE 的关系

本目录仍是完整的 CubeIDE 工程（.cproject/.ioc 未动），CubeIDE 打开照常可用；
`build.py`/`flash.py` 是并行的命令行入口，两边共用 `Core/` 源码。
注意：CubeMX 重新生成代码不会影响这两个脚本。
