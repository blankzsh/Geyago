"""
配置管理模块

使用 JSON 配置文件提供类型安全的配置管理
支持多AI接口配置和动态切换
"""

from __future__ import annotations
import json
import os
from typing import Dict, Any, Optional, List
from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerConfig(BaseModel):
    """服务器配置"""
    host: str = Field(default="0.0.0.0", description="服务器监听地址")
    port: int = Field(default=5000, description="服务器端口")
    debug: bool = Field(default=False, description="调试模式")


class DatabaseConfig(BaseModel):
    """数据库配置"""
    url: str = Field(default="sqlite:///question_bank.db", description="数据库连接URL")


class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = Field(default="INFO", description="日志级别")
    format: str = Field(default="text", description="日志格式")


class AppConfig(BaseModel):
    """应用配置"""
    name: str = Field(default="Geyago智能题库", description="应用名称")
    version: str = Field(default="1.0.0", description="应用版本")
    default_ai: str = Field(default="siliconflow", description="默认AI服务")
    homepage: str = Field(default="https://toni.wang/", description="主页地址")


class APIConfig(BaseModel):
    """API配置"""
    timeout: int = Field(default=30, description="API请求超时时间（秒）")
    max_retries: int = Field(default=3, description="最大重试次数")
    retry_delay: int = Field(default=2, description="重试延迟时间（秒）")


class AIProviderConfig(BaseModel):
    """AI服务提供商配置"""
    name: str = Field(description="服务名称")
    enabled: bool = Field(default=False, description="是否启用")
    api_key: str = Field(default="", description="API密钥")
    base_url: str = Field(description="API基础URL")
    models: Dict[str, Any] = Field(description="模型配置")
    request_format: str = Field(description="请求格式")
    headers: Optional[Dict[str, str]] = Field(default=None, description="请求头")
    parameters: Dict[str, Any] = Field(description="请求参数")
    auth_type: Optional[str] = Field(default=None, description="认证类型")
    secret_key: Optional[str] = Field(default=None, description="密钥（如百度需要的secret_key）")


class Settings(BaseSettings):
    """应用配置类"""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore"
    )

    # 子配置
    server: ServerConfig = Field(default_factory=ServerConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    app: AppConfig = Field(default_factory=AppConfig)
    api_config: APIConfig = Field(default_factory=APIConfig)
    ai_providers: Dict[str, AIProviderConfig] = Field(default_factory=dict)

    def __init__(self, **data):
        super().__init__(**data)
        self._load_from_json()

    def _load_from_json(self):
        """从JSON文件加载配置"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "..", "config.json")

        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

                # 更新配置
                if 'server' in config_data:
                    self.server = ServerConfig(**config_data['server'])
                if 'database' in config_data:
                    self.database = DatabaseConfig(**config_data['database'])
                if 'logging' in config_data:
                    self.logging = LoggingConfig(**config_data['logging'])
                if 'app' in config_data:
                    self.app = AppConfig(**config_data['app'])
                if 'api_config' in config_data:
                    self.api_config = APIConfig(**config_data['api_config'])
                if 'ai_providers' in config_data:
                    self.ai_providers = {
                        provider_id: AIProviderConfig(**provider_config)
                        for provider_id, provider_config in config_data['ai_providers'].items()
                    }

            except Exception as e:
                print(f"加载JSON配置失败: {str(e)}")
                print("使用默认配置")

    def save_to_json(self):
        """保存配置到JSON文件"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "..", "config.json")

        config_data = {
            "server": self.server.model_dump(),
            "database": self.database.model_dump(),
            "logging": self.logging.model_dump(),
            "app": self.app.model_dump(),
            "api_config": self.api_config.model_dump(),
            "ai_providers": {
                provider_id: provider.model_dump()
                for provider_id, provider in self.ai_providers.items()
            }
        }

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            print("配置已保存到JSON文件")
        except Exception as e:
            print(f"保存配置失败: {str(e)}")

    @property
    def database_path(self) -> str:
        """获取数据库文件路径"""
        if self.database.url.startswith("sqlite:///"):
            return self.database.url.replace("sqlite:///", "")
        return self.database.url

    @property
    def host(self) -> str:
        """获取主机地址"""
        return self.server.host

    @property
    def port(self) -> int:
        """获取端口"""
        return self.server.port

    @property
    def debug(self) -> bool:
        """获取调试模式"""
        return self.server.debug

    @property
    def app_name(self) -> str:
        """获取应用名称"""
        return self.app.name

    @property
    def app_version(self) -> str:
        """获取应用版本"""
        return self.app.version

    @property
    def api_timeout(self) -> int:
        """获取API超时时间"""
        return self.api_config.timeout

    @property
    def max_retries(self) -> int:
        """获取最大重试次数"""
        return self.api_config.max_retries

    @property
    def retry_delay(self) -> int:
        """获取重试延迟"""
        return self.api_config.retry_delay

    def get_default_ai_provider(self) -> Optional[AIProviderConfig]:
        """获取默认AI提供商"""
        if self.app.default_ai in self.ai_providers:
            return self.ai_providers[self.app.default_ai]

        # 如果默认的不可用，尝试找一个启用的
        for provider in self.ai_providers.values():
            if provider.enabled:
                return provider

        return None

    def get_enabled_providers(self) -> Dict[str, AIProviderConfig]:
        """获取所有启用的AI提供商"""
        return {
            provider_id: provider
            for provider_id, provider in self.ai_providers.items()
            if provider.enabled
        }

    def get_provider_by_id(self, provider_id: str) -> Optional[AIProviderConfig]:
        """根据ID获取AI提供商"""
        return self.ai_providers.get(provider_id)

    def get_api_config_dict(self) -> dict:
        """获取API配置信息用于输出"""
        display_host = "127.0.0.1" if self.server.host == "0.0.0.0" else self.server.host
        return {
            "app": {
                "name": self.app.name,
                "version": self.app.version,
                "homepage": self.app.homepage,
                "default_ai": self.app.default_ai
            },
            "server": {
                "host": self.server.host,
                "port": self.server.port,
                "debug": self.server.debug
            },
            "database": {
                "url": self.database.url
            },
            "api": {
                "name": f"{self.app.name}",
                "homepage": self.app.homepage,
                "url": f"http://{display_host}:{self.server.port}/api/query",
                "method": "get",
                "type": "GM_xmlhttpRequest",
                "contentType": "json",
                "data": {
                    "title": "${title}",
                    "options": "${options}",
                    "type": "${type}"
                },
                "handler": "return (res)=>res.code === 0 ? [undefined, undefined] : [undefined,res.data.data]"
            },
            "query_config": {
                "url": f"http://{display_host}:{self.server.port}/api/query",
                "method": "get",
                "type": "GM_xmlhttpRequest",
                "contentType": "json",
                "data": {
                    "title": "${title}",
                    "options": "${options}",
                    "type": "${type}"
                },
                "handler": "return (res)=>res.code === 0 ? [undefined, undefined] : [undefined,res.data.data]"
            },
            "endpoints": {
                "query": f"http://{display_host}:{self.server.port}/api/query",
                "config": f"http://{display_host}:{self.server.port}/api/config",
                "providers": f"http://{display_host}:{self.server.port}/api/ai/providers",
                "health": f"http://{display_host}:{self.server.port}/api/health",
                "stats": f"http://{display_host}:{self.server.port}/api/stats"
            }
        }

    def get_providers_info(self) -> Dict[str, Any]:
        """获取所有AI提供商信息"""
        return {
            provider_id: {
                "name": provider.name,
                "enabled": provider.enabled,
                "models": provider.models,
                "base_url": provider.base_url,
                "has_api_key": bool(provider.api_key.strip())
            }
            for provider_id, provider in self.ai_providers.items()
        }


# 全局配置实例
settings = Settings()