import subprocess
import time
import ctypes
from ctypes import wintypes

# Windows API 函数
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowTextLengthW = ctypes.windll.user32.GetWindowTextLengthW
GetWindowTextW = ctypes.windll.user32.GetWindowTextW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
GetClassNameW = ctypes.windll.user32.GetClassNameW

def enum_windows_callback(hwnd, results):
    if IsWindowVisible(hwnd):
        length = GetWindowTextLengthW(hwnd)
        if length > 0:
            buffer = ctypes.create_unicode_buffer(length + 1)
            GetWindowTextW(hwnd, buffer, length + 1)
            title = buffer.value
            
            # 获取类名
            class_buffer = ctypes.create_unicode_buffer(256)
            GetClassNameW(hwnd, class_buffer, 256)
            class_name = class_buffer.value
            
            if 'ECG' in title.upper() or 'QT' in class_name.upper() or 'PYTHON' in title.upper():
                results.append((hwnd, title, class_name))
    return True

def find_windows():
    results = []
    EnumWindows(EnumWindowsProc(enum_windows_callback), results)
    return results

# 启动程序前枚举
print("启动前窗口:")
before = find_windows()
for hwnd, title, class_name in before:
    print(f"  [{hwnd}] {title} ({class_name})")

# 启动程序
print("\n启动 ECG Viewer main.py...")
proc = subprocess.Popen(['python', 'main.py'])
time.sleep(10)  # 等待 10 秒

# 启动后枚举
print("\n启动后窗口:")
after = find_windows()
for hwnd, title, class_name in after:
    print(f"  [{hwnd}] {title} ({class_name})")

# 查找新增窗口
new_windows = [w for w in after if w not in before]
print(f"\n新增窗口数量：{len(new_windows)}")
for hwnd, title, class_name in new_windows:
    print(f"  + [{hwnd}] {title} ({class_name})")

proc.terminate()
