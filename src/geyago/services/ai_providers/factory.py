"""
AI服务工厂

负责创建和管理不同AI服务提供商的实例
"""

from typing import Dict, Type, Optional
from ...config.settings import AIProviderConfig

from .base import BaseAIProvider
from .openai_compatible import OpenAICompatibleProvider
from .ali import AliProvider
from .gemini import GeminiProvider
from .ollama import OllamaProvider


class AIProviderFactory:
    """AI服务提供商工厂类"""

    # 注册的提供商类型
    _providers: Dict[str, Type[BaseAIProvider]] = {
        "openai_compatible": OpenAICompatibleProvider,
        "ali_custom": AliProvider,
        "gemini_custom": GeminiProvider,
        "ollama_custom": OllamaProvider,
    }

    @classmethod
    def register_provider(cls, request_format: str, provider_class: Type[BaseAIProvider]):
        """注册新的AI服务提供商"""
        cls._providers[request_format] = provider_class

    @classmethod
    def create_provider(
        cls,
        config: AIProviderConfig,
        api_config: Dict[str, any]
    ) -> Optional[BaseAIProvider]:
        """根据配置创建AI服务提供商实例"""
        request_format = config.request_format

        if request_format not in cls._providers:
            raise ValueError(f"不支持的AI服务提供商类型: {request_format}")

        provider_class = cls._providers[request_format]
        return provider_class(config, api_config)

    @classmethod
    def get_supported_formats(cls) -> list:
        """获取支持的请求格式列表"""
        return list(cls._providers.keys())

    @classmethod
    def get_provider_info(cls) -> Dict[str, str]:
        """获取提供商信息"""
        return {
            format_name: provider_class.__name__
            for format_name, provider_class in cls._providers.items()
        }