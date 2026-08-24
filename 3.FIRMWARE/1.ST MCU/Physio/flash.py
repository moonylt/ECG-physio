# -*- coding: utf-8 -*-
"""
Physio firmware flashing script (command line, no CubeIDE needed).

用法:
    python flash.py            # 烧录 build/Physio.hex 并复位运行（自动选择 J-Link/OpenOCD）
    python flash.py jlink      # 强制 J-Link
    python flash.py openocd    # 强制 OpenOCD（ST-Link）
    python flash.py erase      # 全片擦除
    python flash.py gdb        # 启动 GDB Server: J-Link tcp:2331 / OpenOCD tcp:3333

Probe order: JLink.exe (SEGGER install dir) -> OpenOCD (F:\\stm32-tools)
"""

import os
import subprocess
import sys
import glob
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ELF = os.path.join(HERE, 'build', 'Physio.elf')
HEX = os.path.join(HERE, 'build', 'Physio.hex')
DEVICE = 'STM32F429ZG'


def find_jlink():
    env = os.environ.get('JLINK_EXE')
    if env:
        return env
    hits = sorted(glob.glob(r'C:\Program Files (x86)\SEGGER\JLink*\JLink.exe')) + \
           sorted(glob.glob(r'C:\Program Files\SEGGER\JLink*\JLink.exe'))
    return hits[-1] if hits else None


def find_jlink_gdbserver():
    env = os.environ.get('JLINK_GDBSERVER')
    if env:
        return env
    hits = sorted(glob.glob(r'C:\Program Files (x86)\SEGGER\JLink*\JLinkGDBServerCL.exe')) + \
           sorted(glob.glob(r'C:\Program Files\SEGGER\JLink*\JLinkGDBServerCL.exe'))
    return hits[-1] if hits else None


def find_openocd():
    env = os.environ.get('OPENOCD_BIN')
    if env:
        return env
    hits = glob.glob(r'F:\stm32-tools\openocd*\bin\openocd.exe')
    return hits[0] if hits else None


# ---------------------------------------------------------------- J-Link
def jlink_run(cmd_lines, tool=None):
    jlink = tool or find_jlink()
    if not jlink:
        return None
    script = os.path.join(tempfile.gettempdir(), 'physio_flash.jlink')
    with open(script, 'w') as f:
        f.write('\n'.join(cmd_lines) + '\n')
    cmd = [jlink, '-device', DEVICE, '-if', 'SWD', '-speed', '4000',
           '-autoconnect', '1', '-CommanderScript', script]
    print(' '.join(cmd))
    return subprocess.call(cmd)


def jlink_flash():
    if not os.path.exists(HEX):
        print('ERROR: build/Physio.hex missing; run python build.py first')
        return 1
    return jlink_run(['loadfile "%s"' % HEX, 'r', 'g', 'qc']) or 0


def jlink_erase():
    return jlink_run(['erase', 'qc']) or 0


# ---------------------------------------------------------------- OpenOCD
OPENOCD_CFG = ['-f', 'interface/stlink.cfg', '-f', 'target/stm32f4x.cfg']


def openocd_flash():
    if not os.path.exists(ELF):
        print('ERROR: build/Physio.elf missing; run python build.py first')
        return 1
    cmd = [find_openocd()] + OPENOCD_CFG + ['-c', f'program "{ELF}" verify reset exit']
    print(' '.join(cmd))
    return subprocess.call(cmd)


def main():
    args = sys.argv[1:]
    mode = args[0] if args else None

    if mode == 'gdb':
        gs = find_jlink_gdbserver()
        if gs:
            print('starting J-Link GDB server: tcp:2331')
            cmd = [gs, '-device', DEVICE, '-if', 'SWD', '-speed', '4000', '-port', '2331']
        else:
            print('starting OpenOCD GDB server: tcp:3333')
            cmd = [find_openocd()] + OPENOCD_CFG
        print(' '.join(cmd))
        return subprocess.call(cmd)

    if mode == 'erase':
        return jlink_erase() if find_jlink() else \
            subprocess.call([find_openocd()] + OPENOCD_CFG +
                            ['-c', 'init; reset halt; stm32f4x mass_erase 0; exit'])

    if mode == 'openocd':
        return openocd_flash()
    if mode == 'jlink':
        return jlink_flash()

    # auto: prefer J-Link
    if find_jlink():
        return jlink_flash()
    if find_openocd():
        return openocd_flash()
    print('ERROR: neither JLink.exe nor OpenOCD found')
    return 1


if __name__ == '__main__':
    sys.exit(main())
