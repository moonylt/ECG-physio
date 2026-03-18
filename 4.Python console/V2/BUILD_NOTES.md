# ECG Viewer 打包说明

## 问题修复记录

### 问题 1: numpy C 扩展未正确打包
**现象**: exe 启动时报错 `No module named 'numpy._core._exceptions'`

**原因**: PyInstaller 没有正确包含 numpy 的 C 扩展模块

**解决方案**: 
- 在打包命令中添加 `--collect-all numpy` 和 `--collect-all scipy`
- 添加必要的 hidden-imports

### 问题 2: signal 模块命名冲突
**现象**: exe 启动时报错 `No module named 'signal.heart_rate'; 'signal' is not a package`

**原因**: 项目中的 `signal` 文件夹与 Python 标准库的 `signal` 模块冲突

**解决方案**: 
- 将 `signal` 文件夹重命名为 `signal_processing`
- 更新 `ui/main_window.py` 中的导入语句

## 打包步骤

### 方法 1: 使用批处理脚本（推荐）
```bash
cd F:\FE\ecg_viewer
build_exe.bat
```

### 方法 2: 手动打包
```bash
cd F:\FE\ecg_viewer
call venv\Scripts\activate.bat
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
```

### 方法 3: 使用 spec 文件
```bash
cd F:\FE\ecg_viewer
call venv\Scripts\activate.bat
pyinstaller "ECG Viewer.spec"
```

## 输出位置
打包完成后可执行文件位于：`dist\ECG Viewer.exe`

## 依赖项
- Python 3.8+
- PyQt5 >= 5.15.0
- pyqtgraph >= 0.12.0
- pyserial >= 3.5
- numpy >= 1.20.0
- scipy >= 1.7.0
- pyinstaller >= 5.0.0

## 注意事项
1. 打包前请确保已安装所有依赖
2. 打包过程可能需要 1-2 分钟
3. 打包后的 exe 文件大小约为 150-200 MB
4. 某些杀毒软件可能会误报，请添加信任

## 修改历史
- 2026-03-03: 修复 numpy 打包问题和 signal 模块命名冲突
