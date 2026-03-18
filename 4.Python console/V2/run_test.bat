@echo off
chcp 65001 >nul
echo ========================================
echo    ECG Viewer - 测试模式
echo ========================================
echo.
echo 此模式会自动生成模拟 ECG 数据
echo 无需串口，直接显示波形
echo.
echo ========================================
echo.

call venv\Scripts\activate.bat
python main.py --test

pause
