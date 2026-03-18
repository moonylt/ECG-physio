@echo off
chcp 65001 >nul
echo ========================================
echo    ECG Viewer 打包脚本
echo ========================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/5] 创建虚拟环境...
python -m venv venv
if errorlevel 1 (
    echo [错误] 创建虚拟环境失败
    pause
    exit /b 1
)

echo [2/5] 激活虚拟环境...
call venv\Scripts\activate.bat

echo [3/5] 安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 安装依赖失败
    pause
    exit /b 1
)

echo [4/5] 清理旧的构建文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo [5/5] 使用 PyInstaller 打包...
REM 注意：signal 文件夹已重命名为 signal_processing，避免与 Python 标准库冲突
pyinstaller --onefile --windowed ^
    --name "ECG Viewer" ^
    --icon="resources/icons/ecg.ico" ^
    --add-data "resources;resources" ^
    --hidden-import=pyqtgraph ^
    --hidden-import=scipy ^
    --hidden-import=numpy ^
    --hidden-import=numpy._core ^
    --hidden-import=numpy._core._exceptions ^
    --hidden-import=numpy._core._multiarray_umath ^
    --hidden-import=numpy._core.numeric ^
    --hidden-import=numpy._core.umath ^
    --hidden-import=numpy.lib ^
    --hidden-import=numpy.lib.npyio ^
    --hidden-import=serial ^
    --collect-all numpy ^
    --collect-all scipy ^
    main.py

if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo    打包完成!
echo ========================================
echo.
echo 可执行文件位置：dist\ECG Viewer.exe
echo.

:: 询问是否打开 dist 文件夹
set /p open_dist="是否打开 dist 文件夹？(Y/N): "
if /i "%open_dist%"=="Y" (
    explorer dist
)

pause
