@echo off
chcp 65001 >nul
echo ========================================
echo PDF标准文档识别系统
echo ========================================
echo.

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

echo 检查依赖包...
python -c "import pdfplumber, sklearn, numpy, joblib, tqdm" >nul 2>&1
if errorlevel 1 (
    echo 安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误: 依赖包安装失败
        pause
        exit /b 1
    )
)

echo.
echo 选择运行模式:
echo 1. 完整流程 (推荐)
echo 2. 仅提取特征
echo 3. 仅训练模型
echo 4. 仅预测复制
echo 5. 系统测试
echo 6. 系统演示
echo.

set /p choice=请输入选择 (1-6): 

if "%choice%"=="1" (
    echo.
    echo 运行完整流程...
    python main.py
) else if "%choice%"=="2" (
    echo.
    echo 提取特征...
    python main.py --step 1
) else if "%choice%"=="3" (
    echo.
    echo 训练模型...
    python main.py --step 2
) else if "%choice%"=="4" (
    echo.
    echo 预测复制...
    python main.py --step 3
) else if "%choice%"=="5" (
    echo.
    echo 运行系统测试...
    python test_system.py
) else if "%choice%"=="6" (
    echo.
    echo 运行系统演示...
    python demo.py
) else (
    echo 无效选择
    pause
    exit /b 1
)

echo.
echo 处理完成!
pause 