# -*- coding: utf-8 -*-
"""
Physio firmware command-line build script (zero dependencies, replaces
CubeIDE/make).

Usage:
    python build.py            # release build into build/
    python build.py clean      # clean build/
    python build.py SIM=0      # force real-acquisition mode

Toolchain: F:\\stm32-tools\\xpack-arm-none-eabi-gcc-* (override with the
ARM_GCC_BIN environment variable).
"""

import os
import subprocess
import sys
import glob
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, 'build')

TARGET = 'Physio'
MCU_FLAGS = ['-mcpu=cortex-m4', '-mfpu=fpv4-sp-d16', '-mfloat-abi=hard', '-mthumb']

C_FLAGS = ['-Os', '-std=gnu11', '-Wall',
           '-ffunction-sections', '-fdata-sections',
           '-g'] + MCU_FLAGS

LD_FLAGS = ['-T', 'STM32F429ZGTX_FLASH.ld',
            '--specs=nosys.specs', '--specs=nano.specs',
            '-static',
            '-Wl,-Map=build/Physio.map', '-Wl,--gc-sections',
            '-Wl,--start-group', '-lc', '-lm', '-Wl,--end-group',
            '-L' + os.path.join(HERE, 'Middlewares', 'ST', 'ARM', 'DSP', 'Lib')
            ] + MCU_FLAGS

INCLUDES = [
    'Core/Inc',
    'Drivers/STM32F4xx_HAL_Driver/Inc',
    'Drivers/STM32F4xx_HAL_Driver/Inc/Legacy',
    'Drivers/CMSIS/Device/ST/STM32F4xx/Include',
    'Drivers/CMSIS/Include',
    'Middlewares/ST/ARM/DSP/Inc',
    '../../',                       # 3.FIRMWARE/protocol.h
]

DEFINES = ['-DUSE_HAL_DRIVER', '-DSTM32F429xx']

# SIM=0/1 command-line override of the acquisition mode
for a in sys.argv[1:]:
    if a.startswith('SIM='):
        DEFINES.append(f'-DPHYSIO_SIM_MODE={a[4:]}')
        print('acquisition-mode override: PHYSIO_SIM_MODE =', a[4:])


def find_toolchain():
    env = os.environ.get('ARM_GCC_BIN')
    if env:
        return env
    for pat in (r'F:\stm32-tools\gcc\bin',
                r'F:\stm32-tools\xpack-arm-none-eabi-gcc-*\bin'):
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    return None


def collect_sources():
    srcs = []
    srcs += glob.glob(os.path.join(HERE, 'Core', 'Src', '*.c'))
    srcs += glob.glob(os.path.join(HERE, 'Drivers', 'STM32F4xx_HAL_Driver', 'Src', '*.c'))
    return srcs


def run(cmd, **kw):
    print(' '.join(os.path.basename(c) if i == 0 else c for i, c in enumerate(cmd)))
    return subprocess.run(cmd, **kw)


def main():
    if 'clean' in sys.argv:
        for f in glob.glob(os.path.join(BUILD, '*')):
            os.remove(f)
        print('cleaned', BUILD)
        return 0

    toolbin = find_toolchain()
    if not toolbin or not os.path.isdir(toolbin):
        print('ERROR: arm-none-eabi-gcc not found; install under F:\\stm32-tools or set ARM_GCC_BIN')
        return 1
    gcc = os.path.join(toolbin, 'arm-none-eabi-gcc.exe')
    objcopy = os.path.join(toolbin, 'arm-none-eabi-objcopy.exe')
    size = os.path.join(toolbin, 'arm-none-eabi-size.exe')
    print('toolchain:', toolbin)

    os.makedirs(BUILD, exist_ok=True)

    inc = [f'-I{os.path.join(HERE, p)}' for p in INCLUDES]
    cflags = C_FLAGS + DEFINES + inc
    srcs = collect_sources()
    print(f'compiling {len(srcs)} sources...')

    objs = []
    errors = []

    def compile_one(src):
        obj = os.path.join(BUILD, os.path.splitext(os.path.basename(src))[0] + '.o')
        r = subprocess.run([gcc] + cflags + ['-MMD', '-MP', '-c', src, '-o', obj],
                           capture_output=True, text=True,
                           cwd=HERE, encoding='utf-8', errors='replace')
        if r.returncode != 0:
            errors.append((src, r.stderr or r.stdout))
            return None
        warn = (r.stderr or '') + (r.stdout or '')
        for line in warn.splitlines():
            if 'warning' in line:
                print(f"[warn] {os.path.basename(src)}: {line}")
        return obj

    with ThreadPoolExecutor(max_workers=8) as ex:
        for obj in ex.map(compile_one, srcs):
            if obj:
                objs.append(obj)

    if errors:
        print(f'\n=== build FAILED: {len(errors)} files ===')
        for src, err in errors[:10]:
            print(f'\n--- {os.path.basename(src)} ---')
            print(err[-2000:])
        return 1

    # 启动文件
    startup = glob.glob(os.path.join(HERE, 'Core', 'Startup', '*.s'))[0]
    start_obj = os.path.join(BUILD, 'startup.o')
    r = subprocess.run([gcc] + MCU_FLAGS + ['-x', 'assembler-with-cpp', '-c', startup, '-o', start_obj],
                       capture_output=True, text=True, cwd=HERE)
    if r.returncode != 0:
        print('startup file compile failed:', r.stderr)
        return 1
    objs.append(start_obj)

    # 链接
    elf = os.path.join(BUILD, f'{TARGET}.elf')
    r = subprocess.run([gcc] + LD_FLAGS + objs + ['-o', elf],
                       capture_output=True, text=True, cwd=HERE)
    if r.returncode != 0:
        print('link FAILED:\n', r.stderr)
        return 1
    if r.stdout.strip():
        print(r.stdout)

    run([objcopy, '-O', 'binary', elf, os.path.join(BUILD, f'{TARGET}.bin')])
    run([objcopy, '-O', 'ihex', elf, os.path.join(BUILD, f'{TARGET}.hex')])
    run([size, elf])
    print(f'\noutput: build\\{TARGET}.elf / .bin / .hex')
    return 0


if __name__ == '__main__':
    sys.exit(main())
