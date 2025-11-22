"""
自定义异常模块

定义应用中使用的所有自定义异常类
"""


class GeyagoException(Exception):
    """Geyago应用基础异常类"""

    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseError(GeyagoException):
    """数据库相关异常"""
    pass


class ConfigurationError(GeyagoException):
    """配置相关异常"""
    pass


class AIServiceError(GeyagoException):
    """AI服务相关异常"""
    pass


class ValidationError(GeyagoException):
    """数据验证异常"""
    pass


class QuestionNotFoundError(GeyagoException):
    """问题未找到异常"""
    pass


class APIError(GeyagoException):
    """API调用异常"""
    pass


class AuthenticationError(GeyagoException):
    """认证异常"""
    pass


class RateLimitError(GeyagoException):
    """频率限制异常"""
    pass


class TimeoutError(GeyagoException):
    """超时异常"""
    pass