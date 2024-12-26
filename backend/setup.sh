#!/bin/bash

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 创建数据库
mysql -u root -proot << EOF
CREATE DATABASE IF NOT EXISTS ks_db;
EOF

# 初始化数据库表
python init_db.py

# 运行Flask应用
export FLASK_APP=app
export FLASK_ENV=development
flask run --port=6565 