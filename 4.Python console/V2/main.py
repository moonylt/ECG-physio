# -*- coding: utf-8 -*-
"""
ECG Viewer - ADS1294R 调试工具
主程序入口

使用方法:
1. 正常模式：python main.py
2. 测试模式：python main.py --test
"""

import sys
import os
import io
import traceback
import time

# 设置标准输出编码（仅在控制台模式有效）
if sys.stdout:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 50)
print("ECG Viewer Starting...")
print("=" * 50)

# 检查是否启用测试模式
TEST_MODE = '--test' in sys.argv

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont

    print("[1/4] PyQt5 imported")

    from ui.main_window import MainWindow
    print("[2/4] MainWindow imported")

    # Enable High DPI
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("ECG Viewer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("ECG Viewer Team")

    print("[3/4] QApplication created")

    # Set font
    font = QFont("Microsoft YaHei UI", 9)
    app.setFont(font)

    # Create main window
    window = MainWindow()

    # 获取主屏幕几何信息
    screen = app.primaryScreen().availableGeometry()
    
    # 计算居中位置
    window_width = 1400
    window_height = 900
    x = (screen.width() - window_width) // 2
    y = (screen.height() - window_height) // 2
    
    # 确保窗口在可见区域内
    x = max(0, min(x, screen.width() - window_width))
    y = max(0, min(y, screen.height() - window_height))
    
    window.setGeometry(x, y, window_width, window_height)
    window.show()
    window.raise_()
    window.activateWindow()
    window.setFocus()

    print("[4/4] MainWindow created and shown")
    print("=" * 50)
    print("ECG Viewer Started!")
    print("Window Title:", window.windowTitle())
    print("Window Position:", window.pos().x(), ",", window.pos().y())
    print("Window Size:", window.width(), "x", window.height())
    print("Screen Size:", screen.width(), "x", screen.height())
    print("=" * 50)
    
    # 如果是测试模式，启动内部测试
    if TEST_MODE:
        print("\n测试模式：启动内部 ECG 数据注入...")
        print("观察波形显示，按 Ctrl+C 停止测试\n")
        from test_ecg_direct import start_test
        start_test(window)

    # Run application
    sys.exit(app.exec_())
    
except Exception as e:
    print("")
    print("ERROR:")
    print("=" * 50)
    print("Type:", type(e).__name__)
    print("Detail:", str(e))
    print("")
    print("Stack trace:")
    traceback.print_exc()
    print("=" * 50)
    if sys.stdout:
        input("Press Enter to exit...")
    sys.exit(1)
