"""
阿里百炼平台AI服务

支持阿里百炼平台（通义千问）系列模型的AI服务
"""

from __future__ import annotations
import json
import time
import traceback
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    import requests
else:
    import requests

from .base import BaseAIProvider
from ...core.exceptions import AIServiceError, TimeoutError, RateLimitError


class AliProvider(BaseAIProvider):
    """阿里百炼平台AI服务提供商"""

    def _build_prompt(self, question: str, options: str = "", question_type: str = "") -> str:
        """构建AI提示词"""
        prompt = (
            '你是一个题库接口函数，请根据问题和选项提供答案。'
            '如果是选择题，直接返回对应选项的内容，注意是内容，不是对应字母；'
            '如果题目是多选题，将内容用"###"连接；'
            '如果选项内容是"对","错"，且只有两项，或者question_type是judgement，你直接返回"对"或"错"的文字，不要返回字母；'
            '如果是填空题，直接返回填空内容，多个空使用###连接。'
            '回答格式为：{"answer":"your_answer_string"}，严格使用此格式回答。'
            '不要回答嗯、好的、我知道了之类的话，你的回答只能是json。'
        )

        # 添加问题信息
        prompt += f'\n问题: {question}'
        if options:
            prompt += f'\n选项: {options}'
        if question_type:
            prompt += f'\n类型: {question_type}'

        return prompt

    def _build_payload(self, prompt: str, model: str) -> Dict[str, Any]:
        """构建API请求载荷"""
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        # 合并提供商特定的参数
        payload.update(self.config.parameters)

        return payload

    def _build_headers(self) -> Dict[str, str]:
        """构建API请求头"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }

        # 如果有额外的头部配置
        if self.config.headers:
            headers.update(self.config.headers)

        return headers

    def _parse_ai_response(self, response_text: str) -> Optional[str]:
        """解析AI响应，提取答案"""
        return self._parse_standard_json_response(response_text)

    def _make_request(self, payload: Dict[str, Any], headers: Dict[str, str], model: str) -> str:
        """发起API请求（包含重试逻辑）"""
        last_exception = None
        url = self.config.base_url

        for attempt in range(self.max_retries):
            try:
                print(f"尝试 {attempt+1}/{self.max_retries} - 准备发送请求到 {url}")
                print(f"请求体: {json.dumps(payload, ensure_ascii=False)}")

                # 发送请求
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    verify=False,
                    timeout=self.timeout
                )

                print(f"API响应状态码: {response.status_code}")
                print(f"API响应内容: {response.text[:200]}...")  # 只打印前200个字符

                # 检查HTTP状态码
                if response.status_code == 429:
                    raise RateLimitError("API调用频率超限，请稍后重试")

                if response.status_code >= 500:
                    if attempt < self.max_retries - 1:
                        print(f"服务器错误，将在 {self.retry_delay} 秒后重试...")
                        time.sleep(self.retry_delay)
                        self.retry_delay *= 2  # 指数退避
                        continue
                    else:
                        raise AIServiceError(f"服务器错误: {response.status_code}")

                # 检查特定的错误码
                if response.status_code == 401:
                    raise AIServiceError("API密钥无效或已过期")
                elif response.status_code == 403:
                    raise AIServiceError("API访问被拒绝，请检查权限")

                response.raise_for_status()  # 检查请求是否成功

                # 解析响应
                result = response.json()

                # 阿里百炼平台的响应格式
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    raise AIServiceError(f"API响应格式异常: {json.dumps(result, ensure_ascii=False)}")

            except requests.exceptions.Timeout as e:
                last_exception = TimeoutError(f"API请求超时: {str(e)}")
                if attempt < self.max_retries - 1:
                    print(f"将在 {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                    self.retry_delay *= 2
                    continue

            except requests.exceptions.RequestException as e:
                last_exception = AIServiceError(f"API请求异常: {str(e)}")
                if attempt < self.max_retries - 1:
                    print(f"将在 {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                    self.retry_delay *= 2
                    continue

            except json.JSONDecodeError as e:
                raise AIServiceError(f"API响应解析失败: {str(e)}")

            except Exception as e:
                error_trace = traceback.format_exc()
                print(f"调用AI模型异常: {str(e)}")
                print(f"详细错误信息: {error_trace}")
                last_exception = AIServiceError(f"AI模型调用失败: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    self.retry_delay *= 2
                    continue

        # 如果所有重试都失败了
        if last_exception:
            raise last_exception
        else:
            raise AIServiceError("多次尝试后仍无法获取答案")