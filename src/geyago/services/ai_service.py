"""
AI服务模块

负责与AI模型API交互，处理问题答案生成
支持多个AI服务提供商的统一管理
"""

from __future__ import annotations
from typing import Optional, Dict, Any
from ..config.settings import settings
from ..core.exceptions import AIServiceError, ValidationError
from .ai_service_manager import AIServiceManager


class AIService:
    """AI服务类（向后兼容的接口）"""

    def __init__(self):
        self.manager = AIServiceManager(settings)

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
            provider_id: 指定AI服务提供商（可选）
            model: 指定模型（可选）

        Returns:
            答案文本，如果失败返回None

        Raises:
            AIServiceError: AI服务相关错误
            ValidationError: 数据验证错误
        """
        return self.manager.query_answer(
            question=question,
            options=options,
            question_type=question_type,
            provider_id=provider_id,
            model=model
        )

    def health_check(self) -> bool:
        """检查默认AI服务健康状态"""
        try:
            test_response = self.manager.query_answer("1+1=?", "A.1 B.2 C.3", "single")
            return test_response is not None
        except Exception:
            return False

    def get_service_info(self) -> Dict[str, Any]:
        """获取AI服务信息"""
        return {
            "manager_stats": self.manager.get_service_stats(),
            "default_provider": self.manager.default_provider_id,
            "health_status": self.health_check()
        }

    def get_providers_info(self) -> Dict[str, Any]:
        """获取所有AI服务提供商信息"""
        return self.manager.get_providers_info()

    def get_provider_models(self, provider_id: str) -> list:
        """获取指定AI服务提供商的可用模型"""
        return self.manager.get_provider_models(provider_id)

    def set_default_provider(self, provider_id: str) -> bool:
        """设置默认AI服务提供商"""
        return self.manager.set_default_provider(provider_id)


# 全局AI服务实例
ai_service = AIService()