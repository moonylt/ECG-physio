import subprocess
import time
import win32gui
import win32process

def find_python_windows():
    """查找所有 Python 相关的窗口"""
    windows = []
    
    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            try:
                title = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                
                # 获取进程 ID
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                
                # 检查是否是 Python 进程
                if 'python' in title.lower() or 'ecg' in title.lower() or 'qt' in class_name.lower():
                    windows.append({
                        'hwnd': hwnd,
                        'title': title,
                        'class': class_name,
                        'pid': pid
                    })
            except:
                pass
        return True
    
    win32gui.EnumWindows(callback, None)
    return windows

# 启动前
print("=" * 60)
print("启动前的 Python/Qt 窗口:")
print("=" * 60)
before = find_python_windows()
for w in before:
    print(f"  PID:{w['pid']} HWND:{w['hwnd']} Title:'{w['title']}' Class:{w['class']}")

# 启动程序
print("\n启动 main.py...")
proc = subprocess.Popen(['python', 'main.py'])
print(f"进程 PID: {proc.pid}")

# 等待
print("等待 10 秒...")
for i in range(10, 0, -1):
    print(f"  {i}...")
    time.sleep(1)

# 启动后
print("\n" + "=" * 60)
print("启动后的 Python/Qt 窗口:")
print("=" * 60)
after = find_python_windows()
for w in after:
    print(f"  PID:{w['pid']} HWND:{w['hwnd']} Title:'{w['title']}' Class:{w['class']}")

# 新增窗口
new_windows = [w for w in after if w['hwnd'] not in [x['hwnd'] for x in before]]
print("\n" + "=" * 60)
print(f"新增窗口：{len(new_windows)} 个")
print("=" * 60)
for w in new_windows:
    print(f"  + PID:{w['pid']} HWND:{w['hwnd']} Title:'{w['title']}' Class:{w['class']}")

# 检查进程是否还在运行
if proc.poll() is None:
    print("\n进程仍在运行")
else:
    print(f"\n进程已退出，返回码：{proc.poll()}")

proc.terminate()
print("进程已终止")
