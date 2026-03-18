@echo off
chcp 65001 >nul
echo ========================================
echo    ECG 数据模拟器 - 快速测试
echo ========================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/2] 激活虚拟环境...
call venv\Scripts\activate.bat

echo [2/2] 启动 ECG 模拟器...
echo.

python test_ecg_loopback.py

pause
