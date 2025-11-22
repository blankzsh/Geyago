"""
查询API的请求和响应模式定义

使用Pydantic提供数据验证和序列化
"""

from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator


class QueryRequest(BaseModel):
    """查询请求模式"""
    title: str = Field(..., min_length=1, description="问题标题")
    options: Optional[str] = Field("", description="问题选项")
    type: Optional[str] = Field("", description="问题类型")

    @validator('title')
    def validate_title(cls, v):
        """验证问题标题"""
        if not v or not v.strip():
            raise ValueError('问题标题不能为空')
        return v.strip()

    class Config:
        """Pydantic配置"""
        str_strip_whitespace = True
        extra = "forbid"


class QueryResponse(BaseModel):
    """查询响应模式"""
    success: bool = Field(..., description="请求是否成功")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    error: Optional[str] = Field(None, description="错误信息")

    @classmethod
    def success_response(cls, code: int, data: Any, message: str) -> "QueryResponse":
        """创建成功响应"""
        return cls(
            success=True,
            data={
                "code": code,
                "data": data,
                "msg": message
            }
        )

    @classmethod
    def error_response(cls, error_message: str) -> "QueryResponse":
        """创建错误响应"""
        return cls(
            success=False,
            error=error_message
        )


class AnswerData(BaseModel):
    """答案数据模式"""
    code: int = Field(..., description="状态码，1表示有答案，0表示无答案")
    data: Optional[str] = Field(None, description="答案内容")
    msg: str = Field(..., description="消息说明")
    source: Optional[str] = Field(None, description="答案来源")


class APIConfigInfo(BaseModel):
    """API配置信息模式"""
    name: str = Field(..., description="API名称")
    homepage: str = Field(..., description="主页")
    url: str = Field(..., description="API地址")
    method: str = Field(..., description="请求方法")
    type: str = Field(..., description="请求类型")
    contentType: str = Field(..., description="内容类型")
    data: Dict[str, str] = Field(..., description="请求参数模板")
    handler: str = Field(..., description="响应处理函数")


class ErrorResponse(BaseModel):
    """详细错误响应模式"""
    success: bool = Field(False, description="总是False")
    error: str = Field(..., description="错误消息")
    error_code: Optional[str] = Field(None, description="错误代码")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")

    @classmethod
    def validation_error(cls, details: Dict[str, Any]) -> "ErrorResponse":
        """创建验证错误响应"""
        return cls(
            error="数据验证失败",
            error_code="VALIDATION_ERROR",
            details=details
        )

    @classmethod
    def database_error(cls, details: Dict[str, Any] = None) -> "ErrorResponse":
        """创建数据库错误响应"""
        return cls(
            error="数据库操作失败",
            error_code="DATABASE_ERROR",
            details=details
        )

    @classmethod
    def ai_service_error(cls, details: Dict[str, Any] = None) -> "ErrorResponse":
        """创建AI服务错误响应"""
        return cls(
            error="AI服务调用失败",
            error_code="AI_SERVICE_ERROR",
            details=details
        )

    @classmethod
    def configuration_error(cls, details: Dict[str, Any] = None) -> "ErrorResponse":
        """创建配置错误响应"""
        return cls(
            error="服务配置错误",
            error_code="CONFIGURATION_ERROR",
            details=details
        )