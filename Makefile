# Geyago智能题库 Makefile

.PHONY: help install dev-install run test lint format clean build deploy init-db

# 默认目标
help:
	@echo "🎭 Geyago智能题库 - 可用命令:"
	@echo ""
	@echo "📦 安装管理:"
	@echo "  install       安装项目依赖"
	@echo "  dev-install   安装开发依赖"
	@echo "  clean         清理临时文件"
	@echo ""
	@echo "🚀 运行管理:"
	@echo "  run           运行应用"
	@echo "  init-db       初始化数据库"
	@echo ""
	@echo "🧪 测试管理:"
	@echo "  test          运行测试"
	@echo "  test-cov      运行测试并生成覆盖率报告"
	@echo "  test-watch    监视模式运行测试"
	@echo ""
	@echo "🔧 代码质量:"
	@echo "  lint          代码检查"
	@echo "  format        代码格式化"
	@echo "  format-check  检查代码格式"
	@echo ""
	@echo "🏗️  构建管理:"
	@echo "  build         构建项目"
	@echo "  deploy        部署项目"

# 安装管理
install:
	@echo "📦 安装项目依赖..."
	uv sync --frozen

dev-install:
	@echo "📦 安装开发依赖..."
	uv sync --frozen --dev

clean:
	@echo "🧹 清理临时文件..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

# 运行管理
run:
	@echo "🚀 启动Geyago智能题库..."
	uv run python -m geyago

init-db:
	@echo "🗄️ 初始化数据库..."
	uv run python scripts/init_db.py

# 测试管理
test:
	@echo "🧪 运行测试..."
	uv run pytest -v

test-cov:
	@echo "🧪 运行测试并生成覆盖率报告..."
	uv run pytest --cov=src/geyago --cov-report=html --cov-report=term

test-watch:
	@echo "👀 监视模式运行测试..."
	uv run pytest-watch

# 代码质量
lint:
	@echo "🔍 运行代码检查..."
	uv run flake8 src tests
	uv run mypy src
	uv run black --check src tests
	uv run isort --check-only src tests

format:
	@echo "✨ 格式化代码..."
	uv run black src tests
	uv run isort src tests

format-check:
	@echo "🔍 检查代码格式..."
	uv run black --check src tests
	uv run isort --check-only src tests

# 开发工具
pre-commit-install:
	@echo "🔧 安装pre-commit钩子..."
	uv run pre-commit install

pre-commit-run:
	@echo "🔧 运行pre-commit检查..."
	uv run pre-commit run --all-files

# 构建管理
build:
	@echo "🏗️ 构建项目..."
	uv build

# 部署相关
docker-build:
	@echo "🐳 构建Docker镜像..."
	docker build -t geyago:latest .

docker-run:
	@echo "🐳 运行Docker容器..."
	docker run -p 5000:5000 --env-file .env geyago:latest

# 开发环境启动
dev: dev-install init-db pre-commit-install
	@echo "🎉 开发环境设置完成！"
	@echo "💡 运行 'make run' 启动应用"

# 生产环境部署
deploy-staging:
	@echo "🚀 部署到预发布环境..."
	# 这里可以添加部署脚本

deploy-prod:
	@echo "🚀 部署到生产环境..."
	# 这里可以添加部署脚本

# 数据库管理
backup-db:
	@echo "💾 备份数据库..."
	@mkdir -p backups
	cp question_bank.db backups/backup_$(shell date +%Y%m%d_%H%M%S).db

restore-db:
	@echo "🔄 恢复数据库..."
	@echo "请指定备份文件: make restore-db BACKUP_FILE=backups/backup_20231201_120000.db"
	@if [ -n "$(BACKUP_FILE)" ] && [ -f "$(BACKUP_FILE)" ]; then \
		cp $(BACKUP_FILE) question_bank.db; \
		echo "✅ 数据库恢复成功"; \
	else \
		echo "❌ 备份文件不存在"; \
	fi

# 监控和日志
logs:
	@echo "📋 查看应用日志..."
	tail -f logs/app.log 2>/dev/null || echo "日志文件不存在"

monitor:
	@echo "📊 系统监控..."
	@echo "CPU使用率: $$(top -l 1 | grep "CPU usage" | awk '{print $$3}' | cut -d'%' -f1)"
	@echo "内存使用: $$(free -h 2>/dev/null | grep Mem | awk '{print $$3"/"$$2}' || echo 'N/A')"

# 版本管理
version:
	@echo "📋 当前版本: $$(uv run python -c 'import tomllib; f=open("pyproject.toml", "rb"); data=tomllib.load(f); print(data["project"]["version"])')"

bump-patch:
	@echo "🔢 升级补丁版本..."
	uv run bump-my-version bump patch

bump-minor:
	@echo "🔢 升级次版本..."
	uv run bump-my-version bump minor

bump-major:
	@echo "🔢 升级主版本..."
	uv run bump-my-version bump major

# 文档生成
docs:
	@echo "📚 生成API文档..."
	@mkdir -p docs
	@uv run python -c "from src.geyago.main import create_app; app = create_app(); \
		with open('docs/api_endpoints.md', 'w', encoding='utf-8') as f: \
			f.write('# API端点文档\n\n'); \
			[ \
				f.write(f'## {rule.endpoint}\n- **路径**: {rule.rule}\n- **方法**: {rule.methods}\n\n') \
				for rule in app.url_map.iter_rules() \
				if 'GET' in rule.methods or 'POST' in rule.methods \
			]; \
		print('✅ API文档生成完成: docs/api_endpoints.md')"

# 性能测试
benchmark:
	@echo "⚡ 运行性能测试..."
	uv run python scripts/benchmark.py

# 安全检查
security-scan:
	@echo "🔒 运行安全扫描..."
	uv run bandit -r src/
	uv run safety check

# 依赖更新
update-deps:
	@echo "⬆️ 更新依赖..."
	uv pip compile pyproject.toml --upgrade

# 本地开发环境检查
check-dev:
	@echo "🔍 检查开发环境..."
	@echo "Python版本: $$(python --version)"
	@echo "UV版本: $$(uv --version)"
	@echo "当前目录: $$(pwd)"
	@echo "虚拟环境: $$VIRTUAL_ENV"
	@if [ ! -f .env ]; then echo "⚠️  .env文件不存在，请复制.env.example"; fi