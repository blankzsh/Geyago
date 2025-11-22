"""
AI服务管理器

统一管理多个AI服务提供商，支持动态切换和负载均衡
"""

from __future__ import annotations
import logging
from typing import Dict, Any, Optional, List
from ..config.settings import Settings
from ..core.exceptions import AIServiceError, ValidationError
from .ai_providers.factory import AIProviderFactory


logger = logging.getLogger(__name__)


class AIServiceManager:
    """AI服务管理器"""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings
        self.providers: Dict[str, Any] = {}
        self.default_provider_id: Optional[str] = None

    def initialize(self):
        """初始化所有可用的AI服务提供商"""
        # 如果已经初始化过，就不再重复初始化
        if self.providers:
            return

        if not self.settings:
            logger.error("Settings对象为None，无法初始化AI服务提供商")
            return

        logger.info(f"开始初始化AI服务提供商，默认AI: {self.settings.app.default_ai}")

        enabled_providers = self.settings.get_enabled_providers()
        logger.info(f"找到 {len(enabled_providers)} 个启用的AI服务提供商: {list(enabled_providers.keys())}")

        api_config = {
            "timeout": self.settings.api_config.timeout,
            "max_retries": self.settings.api_config.max_retries,
            "retry_delay": self.settings.api_config.retry_delay
        }

        for provider_id, config in enabled_providers.items():
            try:
                logger.info(f"正在初始化AI服务提供商 {provider_id} (格式: {config.request_format})")
                provider = AIProviderFactory.create_provider(config, api_config)
                if provider:
                    self.providers[provider_id] = provider
                    logger.info(f"成功初始化AI服务提供商: {config.name}")
                else:
                    logger.warning(f"AI服务提供商 {provider_id} 创建失败，返回None")

            except Exception as e:
                logger.error(f"初始化AI服务提供商失败 {provider_id}: {str(e)}", exc_info=True)

        # 设置默认提供商
        default_provider = self.settings.get_provider_by_id(self.settings.app.default_ai)
        if default_provider:
            self.default_provider_id = self.settings.app.default_ai
            logger.info(f"设置默认AI服务提供商: {default_provider.name}")
        elif self.providers:
            # 如果配置的默认提供商不可用，使用第一个可用的
            self.default_provider_id = list(self.providers.keys())[0]
            logger.warning(f"配置的默认AI服务不可用，使用: {self.default_provider_id}")

        if not self.providers:
            logger.warning("没有可用的AI服务提供商")
        else:
            logger.info(f"AI服务管理器初始化完成，共 {len(self.providers)} 个提供商")

    def _initialize_providers(self):
        """初始化所有可用的AI服务提供商"""
        enabled_providers = self.settings.get_enabled_providers()
        api_config = {
            "timeout": self.settings.api_timeout,
            "max_retries": self.settings.max_retries,
            "retry_delay": self.settings.retry_delay
        }

        for provider_id, config in enabled_providers.items():
            try:
                provider = AIProviderFactory.create_provider(config, api_config)
                if provider:
                    self.providers[provider_id] = provider
                    logger.info(f"成功初始化AI服务提供商: {config.name}")

            except Exception as e:
                logger.error(f"初始化AI服务提供商失败 {provider_id}: {str(e)}")
                continue

        # 设置默认提供商
        default_provider = self.settings.get_default_ai_provider()
        if default_provider:
            self.default_provider_id = self.settings.app.default_ai
            logger.info(f"设置默认AI服务提供商: {default_provider.name}")
        elif self.providers:
            # 如果配置的默认提供商不可用，使用第一个可用的
            self.default_provider_id = list(self.providers.keys())[0]
            logger.warning(f"配置的默认AI服务不可用，使用: {self.default_provider_id}")

        if not self.providers:
            logger.warning("没有可用的AI服务提供商")

    def query_answer(
        self,
        question: str,
        options: str = "",
        question_type: str = "",
        provider_id: Optional[str] = None,
        model: Optional[str] = None
    ) -> Optional[str]:
        """
        查询问题答案

        Args:
            question: 问题文本
            options: 选项文本
            question_type: 问题类型
            provider_id: 指定AI服务提供商，如果为None则使用默认提供商
            model: 指定模型，如果为None则使用提供商默认模型

        Returns:
            答案文本，如果失败返回None

        Raises:
            AIServiceError: AI服务相关错误
            ValidationError: 数据验证错误
        """
        if not question.strip():
            raise ValidationError("问题不能为空")

        # 选择提供商
        if provider_id:
            if provider_id not in self.providers:
                raise ValidationError(f"AI服务提供商不存在: {provider_id}")
            provider = self.providers[provider_id]
        else:
            if not self.default_provider_id:
                raise AIServiceError("没有可用的AI服务提供商")
            provider = self.providers[self.default_provider_id]
            provider_id = self.default_provider_id

        try:
            logger.info(f"使用AI服务提供商 {provider_id} 查询问题: {question[:50]}...")
            answer = provider.query_answer(question, options, question_type, model)
            logger.info(f"AI服务 {provider_id} 返回答案: {answer}")
            return answer

        except Exception as e:
            logger.error(f"AI服务 {provider_id} 查询失败: {str(e)}")
            # 尝试使用备用提供商
            if provider_id == self.default_provider_id:
                return self._try_fallback_providers(question, options, question_type, model)
            else:
                raise AIServiceError(f"AI服务查询失败: {str(e)}")

    def _try_fallback_providers(
        self,
        question: str,
        options: str = "",
        question_type: str = "",
        model: Optional[str] = None
    ) -> Optional[str]:
        """尝试使用备用提供商"""
        for fallback_id, fallback_provider in self.providers.items():
            if fallback_id == self.default_provider_id:
                continue  # 跳过已经失败的默认提供商

            try:
                logger.info(f"尝试使用备用AI服务提供商 {fallback_id}")
                answer = fallback_provider.query_answer(question, options, question_type, model)
                logger.info(f"备用AI服务 {fallback_id} 返回答案: {answer}")
                return answer

            except Exception as e:
                logger.warning(f"备用AI服务 {fallback_id} 也失败了: {str(e)}")
                continue

        return None

    def health_check(self) -> Dict[str, Any]:
        """检查所有AI服务的健康状态"""
        health_status = {}

        for provider_id, provider in self.providers.items():
            try:
                is_healthy = provider.health_check()
                health_status[provider_id] = {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "last_check": "now"
                }
            except Exception as e:
                health_status[provider_id] = {
                    "status": "error",
                    "error": str(e),
                    "last_check": "now"
                }

        return health_status

    def get_providers_info(self) -> Dict[str, Any]:
        """获取所有AI服务提供商的详细信息"""
        providers_info = {}

        for provider_id, provider in self.providers.items():
            try:
                providers_info[provider_id] = provider.get_service_info()
            except Exception as e:
                providers_info[provider_id] = {
                    "provider_id": provider_id,
                    "error": str(e),
                    "status": "error"
                }

        return providers_info

    def get_provider_models(self, provider_id: str) -> List[str]:
        """获取指定AI服务提供商的可用模型列表"""
        if provider_id not in self.providers:
            raise ValidationError(f"AI服务提供商不存在: {provider_id}")

        provider = self.providers[provider_id]
        try:
            # 从配置中获取模型列表
            config = self.settings.get_provider_by_id(provider_id)
            if config and hasattr(config, 'models') and config.models:
                return config.models.get("available", [])
            return []

        except Exception as e:
            logger.error(f"获取AI服务提供商 {provider_id} 模型列表失败: {str(e)}")
            return []

    def get_service_stats(self) -> Dict[str, Any]:
        """获取AI服务统计信息"""
        return {
            "total_providers": len(self.providers),
            "default_provider": self.default_provider_id,
            "health_status": self.health_check(),
            "available_providers": list(self.providers.keys()),
            "providers_info": self.get_providers_info()
        }

    def reload_providers(self):
        """重新加载AI服务提供商（用于配置更新后）"""
        logger.info("重新加载AI服务提供商")
        self.providers.clear()
        self._initialize_providers()

    def set_default_provider(self, provider_id: str) -> bool:
        """设置默认AI服务提供商"""
        if provider_id not in self.providers:
            logger.error(f"无法设置默认提供商，{provider_id} 不存在")
            return False

        old_default = self.default_provider_id
        self.default_provider_id = provider_id

        # 更新配置
        self.settings.app.default_ai = provider_id
        self.settings.save_to_json()

        logger.info(f"默认AI服务提供商已从 {old_default} 更改为 {provider_id}")
        return True

    def add_model_to_provider(self, provider_id: str, model_name: str) -> bool:
        """向指定AI服务提供商添加模型"""
        try:
            if provider_id not in self.providers:
                logger.error(f"提供商 {provider_id} 不存在")
                return False

            if not model_name or not model_name.strip():
                logger.error("模型名称不能为空")
                return False

            model_name = model_name.strip()

            # 获取提供商的当前模型列表
            provider_info = self.settings.get_provider_by_id(provider_id)
            if not provider_info:
                logger.error(f"无法找到提供商 {provider_id} 的配置")
                return False

            # 检查模型是否已存在
            current_models = provider_info.models.get("available", [])
            if model_name in current_models:
                logger.warning(f"模型 {model_name} 已存在于提供商 {provider_id}")
                return True

            # 添加模型到配置
            current_models.append(model_name)
            provider_info.models["available"] = current_models

            # 更新默认模型（如果还没有默认模型）
            if not provider_info.models.get("default"):
                provider_info.models["default"] = model_name

            # 保存配置
            self.settings.save_to_json()

            # 重新初始化提供商以更新内存中的配置
            self.reload_providers()

            logger.info(f"模型 {model_name} 已添加到提供商 {provider_id}")
            return True

        except Exception as e:
            logger.error(f"添加模型失败: {str(e)}")
            return False

    def remove_model_from_provider(self, provider_id: str, model_name: str) -> bool:
        """从指定AI服务提供商删除模型"""
        try:
            if provider_id not in self.providers:
                logger.error(f"提供商 {provider_id} 不存在")
                return False

            if not model_name or not model_name.strip():
                logger.error("模型名称不能为空")
                return False

            model_name = model_name.strip()

            # 获取提供商的当前模型列表
            provider_info = self.settings.get_provider_by_id(provider_id)
            if not provider_info:
                logger.error(f"无法找到提供商 {provider_id} 的配置")
                return False

            current_models = provider_info.models.get("available", [])
            if model_name not in current_models:
                logger.warning(f"模型 {model_name} 不存在于提供商 {provider_id}")
                return True

            # 从模型列表中移除
            current_models.remove(model_name)
            provider_info.models["available"] = current_models

            # 如果删除的是默认模型，需要重新设置默认模型
            if provider_info.models.get("default") == model_name:
                if current_models:
                    provider_info.models["default"] = current_models[0]
                else:
                    provider_info.models["default"] = ""

            # 保存配置
            self.settings.save_to_json()

            # 重新初始化提供商以更新内存中的配置
            self.reload_providers()

            logger.info(f"模型 {model_name} 已从提供商 {provider_id} 删除")
            return True

        except Exception as e:
            logger.error(f"删除模型失败: {str(e)}")
            return False


# 全局AI服务管理器实例
ai_service_manager = AIServiceManager()