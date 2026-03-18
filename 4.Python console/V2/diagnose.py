# ECG Viewer 诊断脚本
import sys
import os

print("诊断信息:")
print("=" * 50)

# 检查 Python 版本
print("Python 版本:", sys.version)

# 检查屏幕信息
try:
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # 获取主屏幕信息
    screen = app.primaryScreen()
    geometry = screen.geometry()
    available_geometry = screen.availableGeometry()
    
    print("主屏幕分辨率:", geometry.width(), "x", geometry.height())
    print("可用工作区:", available_geometry.width(), "x", available_geometry.height())
    
    # 检查多显示器
    screens = app.screens()
    print("显示器数量:", len(screens))
    for i, s in enumerate(screens):
        geom = s.geometry()
        print(f"  显示器 {i+1}: {geom.width()}x{geom.height()} @ ({geom.x()}, {geom.y()})")
    
    print("")
    print("建议:")
    print("如果窗口不可见，可能是因为窗口位置超出了屏幕范围。")
    print("可以尝试修改 main_window.py 中的窗口位置设置。")
    
except Exception as e:
    print("诊断错误:", e)

print("=" * 50)
