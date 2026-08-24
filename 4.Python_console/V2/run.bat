@echo off
chcp 65001 >nul
echo ========================================
echo    ECG Viewer 测试运行
echo ========================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

:: 检查依赖是否已安装
echo 检查依赖...
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo [提示] 依赖未安装，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 安装依赖失败
        pause
        exit /b 1
    )
)

echo 启动 ECG Viewer...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo [错误] 程序运行出错
    pause
    exit /b 1
)
