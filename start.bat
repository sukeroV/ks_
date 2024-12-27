@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion

:: 设置标题
title 口算练习系统启动器

:: 设置颜色
color 0A

echo ====================================
echo        口算练习系统启动器
echo ====================================
echo.

:: 先清理可能存在的残留进程
echo [信息] 清理残留进程...
taskkill /F /IM "python.exe" > nul 2>&1
taskkill /F /IM "node.exe" > nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find ":6565" ^| find "LISTENING"') do taskkill /F /PID %%a > nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5173" ^| find "LISTENING"') do taskkill /F /PID %%a > nul 2>&1

:: 检查Python是否安装
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python
    pause
    exit /b
)

:: 检查Node.js是否安装
node --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Node.js，请先安装Node.js
    pause
    exit /b
)

:: 进入后端目录
cd backend

:: 检查虚拟环境
if not exist venv (
    echo.
    echo [询问] 未检测到虚拟环境，是否创建？
    echo 直接回车确认，输入 no 取消：
    set /p create_venv=
    if /i "!create_venv!"=="no" (
        echo [信息] 取消操作
        exit /b
    ) else (
        echo [信息] 创建虚拟环境...
        python -m venv venv
    )
)

:: 激活虚拟环境
call venv\Scripts\activate

:: 检查Flask是否已安装
python -c "import flask" > nul 2>&1
if errorlevel 1 (
    echo.
    echo [询问] 未检测到必要依赖，是否安装？
    echo 直接回车确认，输入 no 取消：
    set /p install_deps=
    if /i "!install_deps!"=="no" (
        echo [信息] 取消操作
        exit /b
    ) else (
        :: 逐行读取requirements.txt并安装依赖
        for /f "usebackq tokens=1,2 delims==" %%a in ("requirements.txt") do (
            echo [安装] %%a
            :: 尝试不同的源安装
            set "success="
            pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn %%a==%%b > nul 2>&1 && set success=1
            if not defined success pip install -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com %%a==%%b > nul 2>&1 && set success=1
            if not defined success pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ --trusted-host pypi.mirrors.ustc.edu.cn %%a==%%b > nul 2>&1 && set success=1
            if not defined success pip install %%a==%%b > nul 2>&1 && set success=1
            
            if not defined success (
                echo [错误] %%a 安装失败
                echo 按任意键退出...
                pause > nul
                exit /b 1
            ) else (
                echo [成功] %%a 安装完成
            )
        )
        echo [信息] 所有依赖安装完成
    )
)

:: 询问是否初始化数据库
echo.
echo [询问] 是否需要初始化数据库？
echo 直接回车跳过，输入 yes 初始化：
set /p init_db=
if /i "!init_db!"=="yes" (
    echo [信息] 初始化数据库...
    python init_db.py
    if errorlevel 1 (
        echo [错误] 数据库初始化失败
        pause
        exit /b
    )
) else (
    echo [信息] 跳过数据库初始化
)

:: 启动后端服务
echo [信息] 启动后端服务...
start "Backend Service" /min cmd /k "mode con: cols=120 lines=30 & chcp 65001 > nul & title Backend Service & call venv\Scripts\activate & python run.py"

:: 返回根目录
cd ..

:: 进入前端目录
cd frontend

:: 检查前端依赖
if not exist node_modules (
    echo.
    echo [询问] 未检测到前端依赖，是否安装？
    echo 直接回车确认，输入 no 取消：
    set /p install_frontend=
    if /i "!install_frontend!"=="no" (
        echo [信息] 取消操作
        exit /b
    ) else (
        echo [信息] 开始安装前端依赖...
        :: 保存当前错误级别
        set "npm_error="
        
        :: 尝试安装依赖
        echo [进行] 正在安装，请稍候...
        call npm install --no-audit --no-fund > npm_install.log 2>&1 || set npm_error=1
        
        :: 检查安装结果
        if defined npm_error (
            echo [错误] 前端依赖安装失败
            echo 详细错误信息请查看 npm_install.log
            echo 按任意键退出...
            pause > nul
            exit /b 1
        ) else (
            echo [成功] 前端依赖安装完成
            if exist npm_install.log del npm_install.log
        )
    )
)

:: 启动前端服务
echo [信息] 启动前端服务...
start "Frontend Service" /min cmd /k "mode con: cols=120 lines=30 & chcp 65001 > nul & title Frontend Service & npm run dev"

:: 返回根目录
cd ..

cls
echo ====================================
echo        口算练习系统启动器
echo ====================================
echo.
echo [成功] 服务启动完成！
echo.
echo 后端地址: http://localhost:6565
echo 前端地址: http://localhost:5173
echo.
echo 提示：按任意键2次关闭所有服务
pause > nul
pause > nul
echo ====================================

:: 清理进程
cls
echo ====================================
echo        口算练习系统启动器
echo ====================================
echo.
echo [信息] 正在关闭服务...

:: 关闭所有Python和Node进程
wmic process where "name='python.exe'" call terminate > nul 2>&1
wmic process where "name='node.exe'" call terminate > nul 2>&1

:: 关闭占用特定端口的进程
for /f "tokens=5" %%a in ('netstat -aon ^| find ":6565" ^| find "LISTENING"') do (
    taskkill /F /PID %%a > nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5173" ^| find "LISTENING"') do (
    taskkill /F /PID %%a > nul 2>&1
)

:: 使用 taskkill 最后的清理
taskkill /F /FI "WINDOWTITLE eq Backend Service*" > nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Frontend Service*" > nul 2>&1
taskkill /F /IM "python.exe" > nul 2>&1
taskkill /F /IM "node.exe" > nul 2>&1

echo [信息] 服务已关闭
timeout /t 1 > nul

exit 