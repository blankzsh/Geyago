"""
AI服务基础类

定义所有AI服务的通用接口和行为
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import json
import re
import time

from ...config.settings import AIProviderConfig
from ...core.exceptions import AIServiceError, TimeoutError, RateLimitError


class BaseAIProvider(ABC):
    """AI服务提供商基础类"""

    def __init__(self, config: AIProviderConfig, api_config: Dict[str, Any]):
        self.config = config
        self.api_config = api_config
        self.timeout = api_config.get("timeout", 30)
        self.max_retries = api_config.get("max_retries", 3)
        self.retry_delay = api_config.get("retry_delay", 2)

    @abstractmethod
    def _build_prompt(self, question: str, options: str = "", question_type: str = "") -> str:
        """构建AI提示词"""
        pass

    @abstractmethod
    def _build_payload(self, prompt: str, model: str) -> Dict[str, Any]:
        """构建API请求载荷"""
        pass

    @abstractmethod
    def _build_headers(self) -> Dict[str, str]:
        """构建API请求头"""
        pass

    @abstractmethod
    def _parse_ai_response(self, response_text: str) -> Optional[str]:
        """解析AI响应，提取答案"""
        pass

    @abstractmethod
    def _make_request(self, payload: Dict[str, Any], headers: Dict[str, str], model: str) -> str:
        """发起API请求（包含重试逻辑）"""
        pass

    def _parse_standard_json_response(self, response_text: str) -> Optional[str]:
        """标准JSON响应解析（大多数AI服务通用）"""
        if not response_text:
            return None

        try:
            # 尝试解析JSON格式的答案
            if "{" in response_text and "}" in response_text:
                # 提取JSON部分 - 从第一个{到最后一个}
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1
                json_str = response_text[start_idx:end_idx]

                # 清理和格式化JSON字符串
                # 1. 替换单引号为双引号
                json_str = json_str.replace("'", '"')

                # 2. 处理没有引号的键名 {answer: -> {"answer":
                json_str = re.sub(r'{(\s*)(\w+)(\s*):', r'{\1"\2"\3:', json_str)
                json_str = re.sub(r',(\s*)(\w+)(\s*):', r',\1"\2"\3:', json_str)

                # 3. 移除所有换行符和多余空格，使JSON更紧凑
                json_str = re.sub(r'\s+', ' ', json_str).strip()

                print(f"处理后的JSON字符串: {json_str}")

                # 尝试解析JSON
                answer_dict = json.loads(json_str)

                # 提取answer字段
                if "answer" in answer_dict:
                    return answer_dict["answer"]
                elif "anwser" in answer_dict:  # 处理可能的拼写错误
                    return answer_dict["anwser"]

        except json.JSONDecodeError as e:
            print(f"解析AI回答JSON失败: {str(e)}")
            print(f"原始JSON字符串: {json_str if 'json_str' in locals() else '未提取'}")

            # 尝试直接提取引号中的内容作为答案
            if '"answer"' in response_text or '"anwser"' in response_text:
                try:
                    # 使用正则表达式提取引号中的内容
                    answer_match = re.search(r'"answer"\s*:\s*"([^"]+)"', response_text)
                    if answer_match:
                        return answer_match.group(1)
                    else:
                        answer_match = re.search(r'"anwser"\s*:\s*"([^"]+)"', response_text)
                        if answer_match:
                            return answer_match.group(1)
                except Exception as regex_error:
                    print(f"正则提取答案失败: {str(regex_error)}")

        return None

    def query_answer(
        self,
        question: str,
        options: str = "",
        question_type: str = "",
        model: Optional[str] = None
    ) -> Optional[str]:
        """
        查询问题答案

        Args:
            question: 问题文本
            options: 选项文本
            question_type: 问题类型
            model: 指定模型，如果为None则使用默认模型

        Returns:
            答案文本，如果失败返回None

        Raises:
            AIServiceError: AI服务相关错误
            TimeoutError: 请求超时错误
            RateLimitError: 频率限制错误
        """
        if not model:
            model = self.config.models.get("default", "")

        if not self._validate_config():
            raise AIServiceError(f"AI服务配置无效: {self.config.name}")

        # 构建提示词和请求
        prompt = self._build_prompt(question, options, question_type)
        payload = self._build_payload(prompt, model)
        headers = self._build_headers()

        # 发起请求并解析响应
        response_text = self._make_request(payload, headers, model)
        answer = self._parse_ai_response(response_text)

        return answer

    def _validate_config(self) -> bool:
        """验证配置是否有效"""
        if not self.config.enabled:
            return False

        # 检查必要的配置项
        if not self.config.base_url:
            return False

        # 某些服务可能不需要API密钥（如本地Ollama）
        if self.config.request_format != "ollama_custom" and not self.config.api_key:
            return False

        return True

    def health_check(self) -> bool:
        """检查AI服务健康状态"""
        try:
            # 使用简单的问题进行测试
            test_response = self.query_answer("1+1=?", "A.1 B.2 C.3", "single")
            return test_response is not None
        except Exception:
            return False

    def get_service_info(self) -> Dict[str, Any]:
        """获取服务信息"""
        return {
            "provider_id": self.config.name.lower().replace(" ", "_"),
            "name": self.config.name,
            "enabled": self.config.enabled,
            "base_url": self.config.base_url,
            "models": self.config.models,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "health_status": self.health_check(),
            "has_api_key": bool(self.config.api_key.strip()) if self.config.api_key else True
        }