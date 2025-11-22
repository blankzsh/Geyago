"""
Geyago智能题库主应用入口

现代化的Flask应用架构，支持模块化和可扩展设计
"""

from __future__ import annotations
import logging
import json
from typing import NoReturn

from flask import Flask, request
from flask_cors import CORS

from .config.settings import settings
from .core.database import db_manager
from .api.routes.query import query_bp, main_bp
from .utils.helpers import setup_logging, get_client_ip, format_error_response
from .services.ai_service_manager import ai_service_manager


class GeyagoApp:
    """Geyago应用类"""

    def __init__(self):
        self.app = Flask(__name__)
        self._configure_app()
        self._register_blueprints()
        self._setup_cors()
        self._setup_error_handlers()
        self._setup_request_hooks()

    def _configure_app(self) -> None:
        """配置Flask应用"""
        # 基本配置
        self.app.config['DEBUG'] = settings.debug
        self.app.config['JSON_AS_ASCII'] = False  # 支持中文JSON
        self.app.config['JSON_SORT_KEYS'] = False

        # 自定义配置
        self.app.config.update({
            'PROPAGATE_EXCEPTIONS': not settings.debug,
            'TRAP_HTTP_EXCEPTIONS': settings.debug
        })

    def _register_blueprints(self) -> None:
        """注册蓝图"""
        self.app.register_blueprint(query_bp)
        self.app.register_blueprint(main_bp)

    def _setup_cors(self) -> None:
        """设置CORS（跨域资源共享）"""
        CORS(self.app, resources={
            r"/api/*": {
                "origins": "*",
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"]
            }
        })

    def _setup_error_handlers(self) -> None:
        """设置错误处理器"""
        @self.app.errorhandler(404)
        def not_found(error):
            return format_error_response(error, include_traceback=settings.debug), 404

        @self.app.errorhandler(405)
        def method_not_allowed(error):
            return format_error_response(error, include_traceback=settings.debug), 405

        @self.app.errorhandler(500)
        def internal_error(error):
            return format_error_response(error, include_traceback=settings.debug), 500

        @self.app.errorhandler(Exception)
        def unhandled_exception(error):
            logger = logging.getLogger(__name__)
            logger.error(f"未处理的异常: {str(error)}", exc_info=True)
            return format_error_response(error, include_traceback=settings.debug), 500

    def _setup_request_hooks(self) -> None:
        """设置请求钩子"""
        @self.app.before_request
        def before_request():
            """请求前处理"""
            logger = logging.getLogger(__name__)
            logger.info(f"收到请求: {request.method} {request.path} from {get_client_ip(request)}")

        @self.app.after_request
        def after_request(response):
            """请求后处理"""
            logger = logging.getLogger(__name__)
            logger.info(f"请求完成: {response.status_code}")
            return response

    def init_services(self) -> None:
        """初始化服务"""
        try:
            # 初始化数据库
            db_manager.init_database()
            logging.getLogger(__name__).info("数据库初始化完成")

            # 初始化AI服务管理器
            try:
                ai_service_manager.settings = settings
                ai_service_manager.initialize()
                logging.getLogger(__name__).info("AI服务管理器初始化完成")
            except Exception as init_error:
                logging.getLogger(__name__).error(f"AI服务管理器初始化失败: {str(init_error)}", exc_info=True)
                # 不抛出异常，让系统继续运行，只是AI功能不可用

        except Exception as e:
            logging.getLogger(__name__).error(f"服务初始化失败: {str(e)}")
            raise

    def print_startup_info(self) -> None:
        """打印启动信息"""
        # 服务器信息
        display_host = "127.0.0.1" if settings.host == "0.0.0.0" else settings.host
        print(f"\n🎭 {settings.app_name} v{settings.app_version}")
        print(f"🚀 服务器启动地址: http://{display_host}:{settings.port}")
        print(f"🔧 调试模式: {'开启' if settings.debug else '关闭'}")
        print(f"📊 数据库: {settings.database.url}")

        # API配置信息
        api_config = settings.get_api_config_dict()
        print(f"\n📋 API配置信息:")
        print(json.dumps(api_config, ensure_ascii=False, indent=2))

        # 可用端点
        print(f"\n🛠️  可用端点:")
        print(f"  GET  /api/query      - 查询问题答案")
        print(f"  GET  /api/config     - 获取API配置")
        print(f"  GET  /api/health     - 健康检查")
        print(f"  GET  /api/stats      - 题库统计")
        print(f"  GET  /api/search     - 搜索问题")
        print(f"  GET  /api/questions  - 问题列表（分页）")
        print(f"  GET  /api/recent     - 最近问题")

        print("\n" + "="*50)
        print("✨ 服务已就绪，可以开始使用！")
        print("="*50 + "\n")

    def create_app(self) -> Flask:
        """创建并配置应用"""
        self.init_services()
        self.print_startup_info()
        return self.app

    def run(self) -> NoReturn:
        """运行应用"""
        self.init_services()
        self.print_startup_info()
        self.app.run(
            host=settings.host,
            port=settings.port,
            debug=settings.debug
        )


def create_app() -> Flask:
    """应用工厂函数"""
    app_instance = GeyagoApp()
    return app_instance.create_app()


def main() -> NoReturn:
    """主函数"""
    # 设置日志
    setup_logging()

    # 创建并运行应用
    app_instance = GeyagoApp()
    app_instance.run()


if __name__ == '__main__':
    main()