# 口算练习系统
## 快速开始
1. 确保已安装必要的环境
2. 双击运行 `start.bat`
3. 按提示进行操作：
    - 创建虚拟环境（直接回车确认）
    - 安装后端依赖（直接回车确认）
    - 初始化数据库（输入 yes 初始化，回车跳过）
    - 安装前端依赖（直接回车确认）
4. 等待服务启动完成
5. 访问服务：
    - 后端API: http://localhost:6565
    - 前端页面: http://localhost:5173

## 项目结构
```
├── start.bat                # 项目启动脚本，用于自动化部署和服务管理
├── 环境说明.md              # 环境配置和使用说明文档
├── 系统架构图.puml          # PlantUML系统架构图
├── backend/                # 后端目录
│   ├── app/               # Flask应用目录
│   │   ├── __init__.py   # Flask应用初始化
│   │   ├── models.py     # 数据库模型定义
│   │   ├── routes.py     # API路由定义
│   │   └── utils.py      # 工具函数
│   ├── venv/             # Python虚拟环境(自动创建)
│   ├── instance/         # 数据库文件目录
│   │   └── math.db      # SQLite数据库文件
│   ├── init_db.py        # 数据库初始化脚本
│   ├── requirements.txt  # Python依赖列表
│   ├── run.py           # 后端服务启动脚本
│   └── setup.bat        # 后端环境配置脚本
└── frontend/             # 前端目录
    ├── src/             # 源代码目录
    │   ├── assets/      # 静态资源
    │   ├── components/  # Vue组件
    │   ├── router/      # 路由配置
    │   ├── store/       # 状态管理
    │   ├── views/       # 页面视图
    │   ├── App.vue      # 根组件
    │   └── main.ts      # 入口文件
    ├── public/          # 公共资源
    ├── node_modules/    # Node.js依赖(自动创建)
    ├── package.json     # 项目配置文件
    └── vite.config.ts   # Vite构建配置
```

[查看完整系统架构图](系统架构图.puml)

## 文件说明

### 根目录文件
#### start.bat
- 项目主启动脚本
- 功能：
  - 环境检查（Python、Node.js）
  - 虚拟环境创建和管理
  - 依赖自动安装
  - 数据库初始化
  - 服务启动和关闭
  - 错误处理和状态提示

#### 环境说明.md
- 详细的环境配置和使用说明文档
- 内容：
  - 环境要求说明
  - 安装步骤指南
  - 常见问题解答
  - 注意事项说明

### 后端文件 (backend/)
#### run.py
- 后端服务启动入口
- 配置：
  - Flask应用初始化
  - 服务端口：6565
  - 开发模式配置
  - 跨域设置

#### init_db.py
- 数据库初始化脚本
- 功能：
  - 创建数据表结构
  - 初始化基础数据
  - 设置数据库配置

#### requirements.txt
- Python依赖清单
- 核心依赖：
  - Flask==3.0.0
  - Flask-Cors==4.0.0
  - Flask-SQLAlchemy==3.1.1
  - PyMySQL==1.1.0
  - python-docx==1.1.2
  - python-dotenv==1.0.0
  - pytz==2024.2

### 前端文件 (frontend/)
#### vite.config.ts
- Vite构建工具配置
- 设置：
  - 开发服务器端口：5173
  - API代理配置
  - 构建优化选项

#### package.json
- 前端项目配置文件
- 包含：
  - 项目基本信息
  - 依赖包列表
  - 开发脚本命令
  - 构建配置

## 开发环境要求
- Python 3.8+
- Node.js 14+
- MySQL 5.7+

## 注意事项
1. 首次运行
   - 需要完整执行环境配置
   - 确保网络连接正常
   - 注意查看错误提示

2. 数据库
   - 初始化仅需执行一次
   - 可以根据需要重新初始化
   - 注意数据备份

3. 服务管理
   - 使用启动器提供的方式关闭服务（按两次任意键）
   - 避免直接关闭命令行窗口
   - 确保服务完全关闭

4. 开发建议
   - 保持依赖版本一致性
   - 定期更新依赖包
   - 遵循代码规范
