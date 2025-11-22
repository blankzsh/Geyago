# 🎭 Geyago智能题库

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![UV](https://img.shields.io/badge/UV-Modern%20Package%20Manager-green.svg)](https://github.com/astral-sh/uv)
[![Flask](https://img.shields.io/badge/Flask-3.0+-red.svg)](https://flask.palletsprojects.com)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.4+-green.svg)](https://vuejs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3+-blue.svg)](https://www.typescriptlang.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

现代化、全栈的智能题库系统，支持多AI提供商的问题解答和本地缓存。后端采用Python 3.13 + Flask + UV工具链，前端使用Vue 3 + TypeScript + Element Plus，具备完整的测试覆盖和类型注解。

## ✨ 特性

### 🤖 多AI服务提供商支持
- **阿里云百炼平台** - 阿里云AI服务 (默认)
- **智谱AI** - GLM系列大模型
- **硅基流动** - 高性能AI服务
- **OpenAI** - OpenAI GPT系列模型
- **Google Gemini** - Google最新AI模型
- **Ollama** - 本地AI模型部署支持

### 💾 智能缓存与管理
- **本地缓存**: 自动缓存AI生成的答案，提高响应速度
- **答案历史**: 完整的查询历史记录管理
- **智能去重**: 相同问题避免重复调用AI API

### 🏗️ 全栈架构
- **后端服务**: Python 3.13 + Flask + SQLite
- **前端应用**: Vue 3 + TypeScript + Element Plus
- **模块化设计**: 分层架构，易于维护和扩展
- **API优先**: RESTful API设计，支持第三方集成

### 🎨 现代化前端
- **响应式设计**: 适配桌面和移动设备
- **丰富组件**: Element Plus UI组件库
- **数据可视化**: ECharts图表展示
- **路由管理**: Vue Router单页应用
- **状态管理**: Pinia状态管理

### 🧪 开发体验
- **完整测试**: 单元测试和集成测试覆盖
- **类型安全**: Python类型注解 + TypeScript
- **代码质量**: Black格式化、ESLint、Prettier
- **现代工具链**: UV包管理、Vite构建
- **开发工具**: pre-commit钩子、自动化检查

## 🚀 快速开始

### 环境要求

**后端环境:**
- Python 3.13+
- UV包管理器 ([安装指南](https://github.com/astral-sh/uv))

**前端环境:**
- Node.js 18+
- npm 或 yarn 包管理器

### 安装和运行

```bash
# 1. 克隆项目
git clone https://github.com/blankzsh/Geyago.git
cd Geyago

# 2. 后端设置
uv sync --dev

# 3. 前端设置
cd frontend
npm install

# 4. 环境配置
# 复制并编辑配置文件
cp config.example.json config.json
# 编辑 config.json 文件，设置你的API密钥

# 5. 启动服务
# 后端服务 (终端1)
make run
# 或者
uv run python -m geyago.main

# 前端服务 (终端2)
cd frontend
npm run dev
```

### 🌐 访问应用

- **前端界面**: http://localhost:5173
- **后端API**: http://localhost:5000
- **API文档**: http://localhost:5000/api/config

### 配置

在 `config.json` 文件中设置以下配置：

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false
  },
  "database": {
    "url": "sqlite:///question_bank.db"
  },
  "app": {
    "name": "Geyago智能题库",
    "default_ai": "ali"
  },
  "ai_providers": {
    "ali": {
      "name": "阿里百炼平台",
      "enabled": true,
      "api_key": "your-ali-dashscope-api-key-here"
    }
  }
}
```

详细的配置选项请参考 `config.example.json` 文件。

### 🔑 获取API密钥

**支持的AI服务提供商:**

1. **阿里云百炼平台** (默认)
   - [官网](https://dashscope.aliyun.com/)
   - 支持通义千问系列模型

2. **智谱AI**
   - [官网](https://open.bigmodel.cn/)
   - 支持GLM-4系列模型

3. **硅基流动**
   - [注册链接](https://cloud.siliconflow.cn/)

4. **OpenAI**
   - [官网](https://platform.openai.com/)
   - 支持GPT-3.5、GPT-4等模型

5. **Google Gemini**
   - [官网](https://ai.google.dev/)
   - 支持Gemini Pro等模型

6. **Ollama (本地)**
   - [官网](https://ollama.ai/)
   - 本地部署，无需API密钥

## 📋 API接口

### 查询问题答案

```http
GET /api/query?title=问题文本&options=选项&type=类型
```

### 获取API配置信息

```http
GET /api/config
```

### 健康检查

```http
GET /api/health
```

### 题库统计

```http
GET /api/stats
```

### 搜索问题

```http
GET /api/search?q=关键词&limit=10
```

### 最近问题

```http
GET /api/recent?limit=10
```

## 🛠️ 开发指南

### 项目结构

```
geyago/
├── 📁 src/geyago/           # 后端源代码
│   ├── 📁 api/             # API路由和数据模式
│   │   ├── 📁 routes/      # API路由定义
│   │   └── 📁 schemas/     # 数据验证模式
│   ├── 📁 config/          # 配置管理
│   ├── 📁 core/            # 核心功能（数据库、异常）
│   ├── 📁 models/          # 数据模型
│   ├── 📁 services/        # 业务逻辑服务
│   │   └── 📁 ai_providers/ # AI服务提供商
│   └── 📁 utils/           # 工具函数
├── 📁 frontend/            # 前端应用
│   ├── 📁 src/             # Vue源代码
│   │   ├── 📁 components/  # Vue组件
│   │   ├── 📁 views/       # 页面视图
│   │   ├── 📁 stores/      # Pinia状态管理
│   │   └── 📁 utils/       # 前端工具
│   ├── 📄 package.json     # 前端依赖配置
│   └── 📄 vite.config.ts   # Vite构建配置
├── 📁 tests/               # 测试代码
├── 📄 pyproject.toml       # Python项目配置
├── 📄 Makefile           # 开发命令快捷方式
├── 📄 config.example.json # 配置文件模板
└── 📄 README.md          # 项目文档
```

### 开发命令

#### 后端开发 (Python)

```bash
# 安装开发环境
make dev

# 运行后端服务
make run

# 后端测试
make test
make test-cov

# 代码质量检查
make lint

# 代码格式化
make format

# 数据库管理
make init-db
make backup-db

# 构建后端项目
make build
```

#### 前端开发 (Vue.js)

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查和格式化
npm run lint
npm run format
```

#### 全栈开发

```bash
# 并发启动前后端 (需要两个终端)
# 终端1: 启动后端
make run

# 终端2: 启动前端
cd frontend && npm run dev
```

### 测试

#### 后端测试

```bash
# 运行所有后端测试
uv run pytest

# 运行特定测试文件
uv run pytest tests/test_api.py

# 生成覆盖率报告
uv run pytest --cov=src/geyago --cov-report=html

# 运行带标记的测试
uv run pytest -m unit      # 单元测试
uv run pytest -m integration # 集成测试
```

#### 前端测试

```bash
cd frontend

# 运行单元测试 (如果配置了)
npm run test

# 运行端到端测试 (如果配置了)
npm run test:e2e
```

#### 测试覆盖率

- **后端覆盖率报告**: `htmlcov/index.html`
- **前端覆盖率报告**: `coverage/lcov-report/index.html` (如果配置)

## 🏗️ 架构设计

### 后端架构 (Python + Flask)

本项目采用分层架构：

```
┌─────────────────┐
│   API 路由层     │ ← HTTP请求处理、参数验证
├─────────────────┤
│   业务服务层     │ ← AI服务、业务逻辑
├─────────────────┤
│   数据访问层     │ ← 数据库操作、模型映射
├─────────────────┤
│   核心基础层     │ ← 配置管理、异常处理
└─────────────────┘
```

- **API路由层**: 处理HTTP请求和响应，数据验证
- **业务服务层**: AI服务集成、业务逻辑处理
- **数据访问层**: 数据模型定义、数据库操作
- **核心基础层**: 配置管理、异常处理、工具函数

### 前端架构 (Vue 3 + TypeScript)

```
┌─────────────────┐
│   视图层 (Views) │ ← 页面组件、路由管理
├─────────────────┤
│   组件层 (Comps) │ ← 可复用UI组件
├─────────────────┤
│  状态管理 (Store)│ ← Pinia状态管理
├─────────────────┤
│   服务层 (API)   │ ← HTTP请求、数据获取
└─────────────────┘
```

- **视图层**: 页面组件，使用Vue Router管理路由
- **组件层**: 可复用的UI组件，基于Element Plus
- **状态管理**: 使用Pinia进行全局状态管理
- **服务层**: API请求封装，与后端通信

### AI服务架构

```
┌─────────────────┐
│  AI服务管理器    │ ← 统一接口、提供商切换
├─────────────────┤
│  提供商工厂      │ ← 动态创建AI服务实例
├─────────────────┤
│  AI提供商实现    │ ← 各种AI服务适配器
│  - SiliconFlow   │
│  - OpenAI        │
│  - Gemini        │
│  - 百度文心      │
│  - 阿里通义      │
│  - Ollama        │
└─────────────────┘
```

## 🔧 技术栈

### 后端技术栈
- **Web框架**: Flask 3.0+
- **包管理器**: UV (现代Python包管理)
- **数据库**: SQLite (可扩展到PostgreSQL/MySQL)
- **ORM**: SQLAlchemy (通过Flask扩展)
- **数据验证**: Pydantic + Pydantic Settings
- **类型检查**: mypy
- **测试框架**: pytest + pytest-cov
- **代码格式化**: Black + isort
- **代码质量**: flake8 + pre-commit hooks
- **HTTP客户端**: requests
- **CORS支持**: Flask-CORS
- **依赖管理**: pyproject.toml

### 前端技术栈
- **框架**: Vue 3.4+ (Composition API)
- **语言**: TypeScript 5.3+
- **构建工具**: Vite 5.0+
- **UI组件库**: Element Plus 2.4+
- **路由管理**: Vue Router 4.2+
- **状态管理**: Pinia 2.1+
- **HTTP客户端**: Axios 1.6+
- **图表库**: ECharts 5.4+ + vue-echarts 6.6+
- **图标库**: @element-plus/icons-vue
- **代码规范**: ESLint + Prettier
- **包管理**: npm

### AI服务集成
- **阿里云百炼平台** (默认) - 阿里云AI服务
- **智谱AI** - GLM系列大模型
- **硅基流动** - 高性能AI服务
- **OpenAI** - OpenAI GPT系列模型
- **Google Gemini** - Google最新AI模型
- **Ollama** - 本地AI模型部署

### 开发工具
- **版本控制**: Git + pre-commit hooks
- **容器化**: Docker (可选)
- **文档**: Markdown + 自动化文档生成

## 📦 部署

### Docker部署

```bash
# 构建后端镜像
make docker-build

# 运行后端容器
make docker-run

# 或者使用docker-compose (推荐)
docker-compose up -d
```

### 全栈部署

#### 后端部署

```bash
# 安装生产依赖
uv sync --frozen

# 设置生产环境变量
export DEBUG=false
export HOST=0.0.0.0
export PORT=5000
export AI_PROVIDER=siliconflow
export API_KEY=your_production_api_key

# 启动后端服务
uv run python -m geyago
# 或使用生产WSGI服务器 (如gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "geyago:create_app()"
```

#### 前端部署

```bash
cd frontend

# 构建生产版本
npm run build

# 部署到Web服务器 (如nginx)
# 将 dist/ 目录内容复制到Web服务器根目录
```

#### 生产环境配置

**Nginx配置示例:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 云平台部署

- **后端**: 可部署到Heroku、Railway、Render等支持Python的平台
- **前端**: 可部署到Vercel、Netlify、GitHub Pages等静态托管平台
- **数据库**: SQLite适合小规模，生产环境建议使用PostgreSQL或MySQL

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [UV](https://github.com/astral-sh/uv) - 现代Python包管理器
- [Flask](https://flask.palletsprojects.com) - Web框架

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [Issue](https://github.com/blankzsh/geyago/issues)
- 发送邮件到 shell7@petalmail.com

---

<div align="center">
  <p>用 💖 和 ☕ 制作</p>
  <p>© 2024 Geyago Project</p>
</div>



