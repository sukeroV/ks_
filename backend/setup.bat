@echo off

:: 创建虚拟环境
python -m venv venv

:: 激活虚拟环境
call venv\Scripts\activate

:: 安装依赖
pip install -r requirements.txt

:: 创建数据库
mysql -u root -proot -e "CREATE DATABASE IF NOT EXISTS ks_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

:: 初始化数据库表
:: REM python init_db.py

:: 运行Flask应用
python run.py 