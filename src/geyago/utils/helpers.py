"""
工具函数模块

提供通用的辅助函数
"""

from __future__ import annotations
import json
import logging
import re
from typing import Any, Dict, Optional, Union
from datetime import datetime

from ..config.settings import settings


def setup_logging() -> None:
    """设置日志配置"""
    log_level = getattr(logging, settings.logging.level.upper(), logging.INFO)

    # 创建日志格式
    if settings.logging.format.lower() == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # 清除现有处理器并添加新的
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)


class JsonFormatter(logging.Formatter):
    """JSON格式的日志格式化器"""

    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)


def sanitize_text(text: str) -> str:
    """
    清理和标准化文本

    Args:
        text: 原始文本

    Returns:
        清理后的文本
    """
    if not text:
        return ""

    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text.strip())

    # 移除特殊字符（保留基本标点）
    text = re.sub(r'[^\w\s\u4e00-\u9fff,.!?;:()（）。，！？；：]', '', text)

    return text


def validate_question_type(question_type: str) -> bool:
    """
    验证问题类型是否有效

    Args:
        question_type: 问题类型

    Returns:
        是否有效
    """
    valid_types = [
        'single',    # 单选题
        'multiple',  # 多选题
        'judgement', # 判断题
        'fill',      # 填空题
        'essay',     # 简答题
        'unknown'    # 未知类型
    ]

    return question_type.lower() in valid_types


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    从文本中提取JSON对象

    Args:
        text: 包含JSON的文本

    Returns:
        提取的JSON字典，失败时返回None
    """
    if not text:
        return None

    try:
        # 查找JSON对象
        json_pattern = r'\{[^{}]*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)

        for match in matches:
            try:
                # 清理JSON字符串
                cleaned_json = match.replace("'", '"')  # 替换单引号
                cleaned_json = re.sub(r'(\w+):', r'"\1":', cleaned_json)  # 添加键名引号
                cleaned_json = re.sub(r'\s+', ' ', cleaned_json).strip()  # 清理空白

                return json.loads(cleaned_json)
            except json.JSONDecodeError:
                continue

        return None
    except Exception:
        return None


def format_error_response(error: Exception, include_traceback: bool = False) -> Dict[str, Any]:
    """
    格式化错误响应

    Args:
        error: 异常对象
        include_traceback: 是否包含堆栈信息

    Returns:
        格式化的错误响应
    """
    response = {
        "success": False,
        "error": str(error),
        "error_type": type(error).__name__,
        "timestamp": datetime.now().isoformat()
    }

    if include_traceback:
        import traceback
        response["traceback"] = traceback.format_exc()

    return response


def safe_json_dumps(obj: Any, default: str = "") -> str:
    """
    安全的JSON序列化

    Args:
        obj: 要序列化的对象
        default: 序列化失败时的默认值

    Returns:
        JSON字符串或默认值
    """
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return default


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本到指定长度

    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后的后缀

    Returns:
        截断后的文本
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def normalize_question_text(text: str) -> str:
    """
    标准化问题文本以便匹配

    Args:
        text: 原始问题文本

    Returns:
        标准化后的文本
    """
    if not text:
        return ""

    # 转换为小写
    text = text.lower()

    # 移除标点符号
    text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)

    # 标准化空白字符
    text = re.sub(r'\s+', ' ', text.strip())

    return text


def calculate_similarity(text1: str, text2: str) -> float:
    """
    计算两个文本的相似度（简单的字符重叠率）

    Args:
        text1: 文本1
        text2: 文本2

    Returns:
        相似度分数（0-1之间）
    """
    if not text1 or not text2:
        return 0.0

    # 转换为字符集合
    set1 = set(text1.lower())
    set2 = set(text2.lower())

    # 计算交集和并集
    intersection = set1.intersection(set2)
    union = set1.union(set2)

    # 计算相似度
    similarity = len(intersection) / len(union) if union else 0.0

    return similarity


def mask_api_key(api_key: str) -> str:
    """
    遮蔽API密钥用于日志显示

    Args:
        api_key: 原始API密钥

    Returns:
        遮蔽后的API密钥
    """
    if not api_key or len(api_key) < 8:
        return "***"

    return api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]


def parse_options_string(options: str) -> list[str]:
    """
    解析选项字符串

    Args:
        options: 选项字符串，如 "A.选项1 B.选项2 C.选项3"

    Returns:
        选项列表
    """
    if not options:
        return []

    # 按字母标识分割选项
    pattern = r'([A-Z]\.\s*[^A-Z]+)'
    matches = re.findall(pattern, options)

    if not matches:
        # 如果没有找到字母标识，尝试其他分割方式
        return [option.strip() for option in options.split(';,，') if option.strip()]

    # 清理选项文本
    parsed_options = []
    for match in matches:
        # 移除字母标识并清理
        clean_option = re.sub(r'^[A-Z]\.\s*', '', match).strip()
        if clean_option:
            parsed_options.append(clean_option)

    return parsed_options


def is_empty_input(text: str) -> bool:
    """
    检查输入是否为空或只包含空白字符

    Args:
        text: 输入文本

    Returns:
        是否为空
    """
    return not text or not text.strip()


def get_client_ip(request) -> str:
    """
    获取客户端IP地址

    Args:
        request: Flask请求对象

    Returns:
        客户端IP地址
    """
    # 尝试从各种头部获取真实IP
    ip_headers = [
        'X-Forwarded-For',
        'X-Real-IP',
        'X-Client-IP',
        'CF-Connecting-IP',  # Cloudflare
        'True-Client-IP'     # Akamai
    ]

    for header in ip_headers:
        ip = request.headers.get(header)
        if ip:
            # X-Forwarded-For可能包含多个IP，取第一个
            return ip.split(',')[0].strip()

    # 回退到远程地址
    return request.remote_addr or 'unknown'