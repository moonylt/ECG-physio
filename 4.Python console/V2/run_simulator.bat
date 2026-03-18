@echo off
chcp 65001 >nul
echo ========================================
echo    ECG 模拟器安装和运行
echo ========================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/3] 激活虚拟环境...
call venv\Scripts\activate.bat

echo [2/3] 检查 pyserial 安装...
pip show pyserial >nul 2>&1
if errorlevel 1 (
    echo 安装 pyserial...
    pip install pyserial
)

echo [3/3] 启动 ECG 模拟器...
echo.
echo ========================================
echo 使用说明:
echo ========================================
echo 1. 首先需要安装虚拟串口驱动:
echo    - com0com: http://com0com.sourceforge.net/
echo    - 或 VSPD: https://www.eltima.com/products/vspdxp-free/
echo.
echo 2. 创建虚拟串口对 (例如：COM3 <-> COM4)
echo.
echo 3. 运行此模拟器，选择 COM3
echo.
echo 4. 在 ECG Viewer 中选择 COM4
echo.
echo ========================================
echo.

python test_ecg_simulator.py

pause
