"""
查询API路由模块

处理问题查询相关的HTTP请求
"""

from __future__ import annotations
import logging
from typing import Dict, Any
from flask import Blueprint, request, jsonify

from ...config.settings import settings
from ...services.qa_service import qa_service
from ...services.ai_service_manager import ai_service_manager
from ...core.exceptions import GeyagoException, ValidationError, DatabaseError
from ..schemas.query import QueryRequest, QueryResponse, ErrorResponse

# 配置日志
logger = logging.getLogger(__name__)

# 创建蓝图
query_bp = Blueprint('query', __name__, url_prefix='/api')

# 创建主蓝图
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """主页面"""
    from ...config.settings import settings

    display_host = "127.0.0.1" if settings.host == "0.0.0.0" else settings.host

    return {
        "name": "完美题库(自建版)",
        "homepage": "https://toni.wang/",
        "version": settings.app_version,
        "default_ai": settings.app.default_ai,
        "endpoints": {
            "query": f"http://{display_host}:{settings.port}/api/query",
            "config": f"http://{display_host}:{settings.port}/api/config",
            "providers": f"http://{display_host}:{settings.port}/api/ai/providers",
            "health": f"http://{display_host}:{settings.port}/api/health",
            "stats": f"http://{display_host}:{settings.port}/api/stats"
        },
        "query_config": {
            "url": f"http://{display_host}:{settings.port}/api/query",
            "method": "get",
            "type": "GM_xmlhttpRequest",
            "contentType": "json",
            "data": {
                "title": "${title}",
                "options": "${options}",
                "type": "${type}",
                "provider": "${provider}",  # 可选：指定AI提供商
                "model": "${model}"        # 可选：指定模型
            },
            "handler": "return (res)=>res.code === 0 ? [undefined, undefined] : [undefined,res.data.data]"
        },
        "supported_providers": list(settings.ai_providers.keys())
    }


@query_bp.route('/query', methods=['GET'])
def search_answer() -> Dict[str, Any]:
    """
    查询问题答案的API端点

    Query Parameters:
        title (str, required): 问题标题
        options (str, optional): 问题选项
        type (str, optional): 问题类型

    Returns:
        JSON: 包含查询结果或错误信息的响应
    """
    try:
        # 解析请求参数
        query_request = QueryRequest(
            title=request.args.get('title', '').strip(),
            options=request.args.get('options', '').strip(),
            type=request.args.get('type', '').strip()
        )

        logger.info(f"收到查询请求: {query_request.title[:50]}...")

        # 获取AI提供商和模型参数
        provider_id = request.args.get('provider', '').strip()
        model = request.args.get('model', '').strip()

        # 调用业务逻辑
        result = qa_service.query_answer(
            question_text=query_request.title,
            options=query_request.options,
            question_type=query_request.type,
            provider_id=provider_id if provider_id else None,
            model=model if model else None
        )

        # 返回成功响应
        return QueryResponse.success_response(
            code=result['code'],
            data=result['data'],
            message=result['msg']
        ).dict()

    except ValidationError as e:
        logger.warning(f"数据验证错误: {str(e)}")
        return jsonify(ErrorResponse.validation_error({"error": str(e)}).dict()), 400

    except DatabaseError as e:
        logger.error(f"数据库错误: {str(e)}")
        return jsonify(ErrorResponse.database_error().dict()), 500

    except GeyagoException as e:
        logger.error(f"应用错误: {str(e)}")
        return jsonify(ErrorResponse.error_response(str(e)).dict()), 500

    except Exception as e:
        logger.error(f"未知错误: {str(e)}", exc_info=True)
        return jsonify(ErrorResponse(error="服务器内部错误").dict()), 500


@query_bp.route('/config', methods=['GET'])
def get_api_config() -> Dict[str, Any]:
    """
    获取API配置信息

    Returns:
        JSON: API配置信息
    """
    try:
        api_config = settings.get_api_config_dict()
        return jsonify({
            "success": True,
            "data": api_config
        })
    except Exception as e:
        logger.error(f"获取API配置失败: {str(e)}")
        return jsonify(ErrorResponse(error="获取配置失败").dict()), 500


@query_bp.route('/health', methods=['GET'])
def health_check() -> Dict[str, Any]:
    """
    健康检查端点

    Returns:
        JSON: 服务健康状态
    """
    try:
        stats = qa_service.get_question_statistics()
        return jsonify({
            "success": True,
            "data": {
                "status": "healthy",
                "service": settings.app_name,
                "version": settings.app_version,
                "database": stats["service_status"]["database"],
                "ai_service": stats["service_status"]["ai_service"],
                "total_questions": stats["total_questions"]
            }
        })
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": "健康检查失败"
        }), 500


@query_bp.route('/stats', methods=['GET'])
def get_statistics() -> Dict[str, Any]:
    """
    获取题库统计信息

    Returns:
        JSON: 题库统计数据
    """
    try:
        stats = qa_service.get_question_statistics()
        return jsonify({
            "success": True,
            "data": stats
        })
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        return jsonify(ErrorResponse.database_error().dict()), 500


@query_bp.route('/search', methods=['GET'])
def search_questions() -> Dict[str, Any]:
    """
    搜索问题

    Query Parameters:
        q (str, required): 搜索关键词
        limit (int, optional): 返回结果数量限制，默认10

    Returns:
        JSON: 搜索结果列表
    """
    try:
        keyword = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 10))

        if not keyword:
            raise ValidationError("搜索关键词不能为空")

        questions = qa_service.search_questions(keyword, limit)

        # 转换为字典格式
        results = [question.to_dict() for question in questions]

        return jsonify({
            "success": True,
            "data": {
                "keyword": keyword,
                "results": results,
                "count": len(results)
            }
        })

    except ValueError as e:
        return jsonify(ErrorResponse.validation_error({"error": "limit参数必须是整数"}).dict()), 400
    except ValidationError as e:
        return jsonify(ErrorResponse.validation_error({"error": str(e)}).dict()), 400
    except Exception as e:
        logger.error(f"搜索问题失败: {str(e)}")
        return jsonify(ErrorResponse(error="搜索失败").dict()), 500


@query_bp.route('/questions', methods=['GET'])
def get_questions() -> Dict[str, Any]:
    """
    获取问题列表（分页）

    Query Parameters:
        page (int, optional): 页码，默认1
        limit (int, optional): 每页数量，默认10

    Returns:
        JSON: 问题列表（分页）
    """
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10

        questions = qa_service.get_recent_questions(limit * page)

        # 转换为字典格式并分页
        all_results = [question.to_dict() for question in questions]
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        results = all_results[start_idx:end_idx]

        return jsonify({
            "success": True,
            "data": {
                "results": results,
                "count": len(results),
                "page": page,
                "limit": limit,
                "total": len(all_results)
            }
        })

    except ValueError as e:
        return jsonify(ErrorResponse.validation_error({"error": "page和limit参数必须是整数"}).dict()), 400
    except Exception as e:
        logger.error(f"获取问题列表失败: {str(e)}")
        return jsonify(ErrorResponse(error="获取问题列表失败").dict()), 500


@query_bp.route('/recent', methods=['GET'])
def get_recent_questions() -> Dict[str, Any]:
    """
    获取最近添加的问题

    Query Parameters:
        limit (int, optional): 返回结果数量限制，默认10

    Returns:
        JSON: 最近问题列表
    """
    try:
        limit = int(request.args.get('limit', 10))

        questions = qa_service.get_recent_questions(limit)

        # 转换为字典格式
        results = [question.to_dict() for question in questions]

        return jsonify({
            "success": True,
            "data": {
                "results": results,
                "count": len(results)
            }
        })

    except ValueError as e:
        return jsonify(ErrorResponse.validation_error({"error": "limit参数必须是整数"}).dict()), 400
    except Exception as e:
        logger.error(f"获取最近问题失败: {str(e)}")
        return jsonify(ErrorResponse(error="获取最近问题失败").dict()), 500


@query_bp.errorhandler(404)
def not_found(error) -> Dict[str, Any]:
    """处理404错误"""
    return jsonify(ErrorResponse(error="API端点不存在").dict()), 404


@query_bp.errorhandler(405)
def method_not_allowed(error) -> Dict[str, Any]:
    """处理405错误"""
    return jsonify(ErrorResponse(error="请求方法不被允许").dict()), 405


@query_bp.before_request
def log_request_info():
    """记录请求信息"""
    logger.debug(f"请求方法: {request.method}")
    logger.debug(f"请求路径: {request.path}")
    logger.debug(f"请求参数: {dict(request.args)}")


@query_bp.after_request
def log_response_info(response):
    """记录响应信息"""
    logger.debug(f"响应状态码: {response.status_code}")
    return response


@query_bp.route('/ai/providers', methods=['GET'])
def get_ai_providers() -> Dict[str, Any]:
    """
    获取所有AI服务提供商信息（包括未启用的）

    Returns:
        JSON: AI服务提供商列表和状态
    """
    try:
        # 获取所有配置的提供商信息（包括未启用的）
        all_providers = settings.get_providers_info()

        # 为每个提供商添加运行时状态信息
        providers_info = {}
        for provider_id, provider_config in all_providers.items():
            providers_info[provider_id] = {
                # 配置信息
                "provider_id": provider_id,
                "name": provider_config.get("name", provider_id),
                "enabled": provider_config.get("enabled", False),
                "base_url": provider_config.get("base_url", ""),
                "models": provider_config.get("models", {"default": "", "available": []}),
                "api_key": provider_config.get("api_key", ""),
                "has_api_key": bool(provider_config.get("api_key", "").strip()),
                "timeout": settings.api_config.timeout,
                "max_retries": settings.api_config.max_retries,

                # 运行时状态（如果提供商已初始化）
                "is_initialized": provider_id in ai_service_manager.providers,
                "health_status": None
            }

            # 如果提供商已初始化，获取健康状态
            if provider_id in ai_service_manager.providers:
                try:
                    provider_obj = ai_service_manager.providers[provider_id]
                    if hasattr(provider_obj, 'health_check'):
                        providers_info[provider_id]["health_status"] = provider_obj.health_check()
                    else:
                        providers_info[provider_id]["health_status"] = True
                except Exception as e:
                    logger.warning(f"获取提供商 {provider_id} 健康状态失败: {str(e)}")
                    providers_info[provider_id]["health_status"] = False

        return jsonify({
            "success": True,
            "data": {
                "providers": providers_info,
                "default_provider": ai_service_manager.default_provider_id,
                "total_count": len(providers_info)
            }
        })
    except Exception as e:
        logger.error(f"获取AI服务提供商信息失败: {str(e)}")
        return jsonify(ErrorResponse(error="获取提供商信息失败").dict()), 500


@query_bp.route('/ai/providers/<provider_id>/models', methods=['GET', 'POST'])
def manage_provider_models(provider_id: str) -> Dict[str, Any]:
    """
    管理指定AI服务提供商的模型列表

    Args:
        provider_id: AI服务提供商ID

    GET: 获取模型列表
    POST: 添加新模型

    Returns:
        JSON: 操作结果
    """
    try:
        if request.method == 'GET':
            # 获取模型列表
            models = qa_service.get_provider_models(provider_id)
            return jsonify({
                "success": True,
                "data": {
                    "provider_id": provider_id,
                    "models": models,
                    "count": len(models)
                }
            })
        elif request.method == 'POST':
            # 添加新模型
            request_data = request.get_json()
            if not request_data:
                raise ValidationError("请求体不能为空")

            model_name = request_data.get("model", "").strip()
            if not model_name:
                raise ValidationError("模型名称不能为空")

            success = qa_service.add_model_to_provider(provider_id, model_name)
            if success:
                return jsonify({
                    "success": True,
                    "data": {
                        "message": f"模型 '{model_name}' 添加成功",
                        "provider_id": provider_id,
                        "model": model_name
                    }
                })
            else:
                return jsonify(ErrorResponse.validation_error({"error": "添加模型失败"}).dict()), 400

    except ValidationError as e:
        logger.warning(f"数据验证错误: {str(e)}")
        return jsonify(ErrorResponse.validation_error({"error": str(e)}).dict()), 400
    except Exception as e:
        if request.method == 'GET':
            logger.error(f"获取AI模型列表失败: {str(e)}")
            return jsonify(ErrorResponse(error="获取模型列表失败").dict()), 500
        else:
            logger.error(f"添加AI模型失败: {str(e)}")
            return jsonify(ErrorResponse(error="添加模型失败").dict()), 500


@query_bp.route('/ai/providers/<provider_id>/models/<path:model_name>', methods=['DELETE'])
def remove_model_from_provider(provider_id: str, model_name: str) -> Dict[str, Any]:
    """
    从指定AI服务提供商删除模型

    Args:
        provider_id: AI服务提供商ID
        model_name: 模型名称（支持路径参数，包含特殊字符）

    Returns:
        JSON: 删除结果
    """
    try:
        # URL解码模型名称
        from urllib.parse import unquote
        model_name = unquote(model_name)

        success = qa_service.remove_model_from_provider(provider_id, model_name)
        if success:
            return jsonify({
                "success": True,
                "data": {
                    "message": f"模型 '{model_name}' 删除成功",
                    "provider_id": provider_id,
                    "model": model_name
                }
            })
        else:
            return jsonify(ErrorResponse.validation_error({"error": "删除模型失败"}).dict()), 400

    except ValidationError as e:
        logger.warning(f"数据验证错误: {str(e)}")
        return jsonify(ErrorResponse.validation_error({"error": str(e)}).dict()), 400
    except Exception as e:
        logger.error(f"删除AI模型失败: {str(e)}")
        return jsonify(ErrorResponse(error="删除模型失败").dict()), 500


@query_bp.route('/ai/providers/<provider_id>/set-default', methods=['POST'])
def set_default_provider(provider_id: str) -> Dict[str, Any]:
    """
    设置默认AI服务提供商

    Args:
        provider_id: AI服务提供商ID

    Returns:
        JSON: 设置结果
    """
    try:
        success = qa_service.set_default_provider(provider_id)
        if success:
            return jsonify({
                "success": True,
                "data": {
                    "message": f"默认AI服务提供商已设置为: {provider_id}",
                    "new_default": provider_id
                }
            })
        else:
            return jsonify(ErrorResponse.validation_error({"error": f"无法设置提供商 {provider_id} 为默认值"}).dict()), 400
    except Exception as e:
        logger.error(f"设置默认AI服务提供商失败: {str(e)}")
        return jsonify(ErrorResponse(error="设置默认提供商失败").dict()), 500


@query_bp.route('/ai/config', methods=['GET'])
def get_ai_config() -> Dict[str, Any]:
    """
    获取AI配置信息

    Returns:
        JSON: AI配置信息
    """
    try:
        config_info = settings.get_providers_info()
        return jsonify({
            "success": True,
            "data": {
                "app_config": {
                    "default_ai": settings.app.default_ai,
                    "timeout": settings.api_timeout,
                    "max_retries": settings.max_retries,
                    "retry_delay": settings.retry_delay
                },
                "providers": config_info
            }
        })
    except Exception as e:
        logger.error(f"获取AI配置失败: {str(e)}")
        return jsonify(ErrorResponse(error="获取配置失败").dict()), 500


@query_bp.route('/ai/config', methods=['POST'])
def update_ai_config() -> Dict[str, Any]:
    """
    更新AI配置信息

    Request Body:
        JSON: 配置更新数据

    Returns:
        JSON: 更新结果
    """
    try:
        update_data = request.get_json()
        if not update_data:
            raise ValidationError("请求体不能为空")

        # 这里可以实现配置更新逻辑
        # 为了安全，只允许更新特定的配置项
        allowed_updates = ["default_ai", "timeout", "max_retries", "retry_delay", "models", "enabled"]
        updated_fields = []

        # 获取provider_id（对于提供商相关的更新）
        provider_id = update_data.get("provider_id")

        for field in allowed_updates:
            if field in update_data:
                if field == "default_ai":
                    if update_data[field] not in settings.ai_providers:
                        raise ValidationError(f"AI服务提供商不存在: {update_data[field]}")
                    settings.app.default_ai = update_data[field]
                elif field == "timeout":
                    settings.api_config.timeout = int(update_data[field])
                elif field == "max_retries":
                    settings.api_config.max_retries = int(update_data[field])
                elif field == "retry_delay":
                    settings.api_config.retry_delay = int(update_data[field])
                elif field == "enabled":
                    # 处理启用/禁用服务商
                    if not provider_id:
                        raise ValidationError("更新启用状态时必须指定provider_id")

                    provider_config = settings.get_provider_by_id(provider_id)
                    if not provider_config:
                        raise ValidationError(f"AI服务提供商不存在: {provider_id}")

                    # 更新启用状态
                    provider_config.enabled = update_data[field]
                elif field == "models":
                    # 处理模型配置更新
                    if not provider_id:
                        raise ValidationError("更新模型配置时必须指定provider_id")

                    provider_config = settings.get_provider_by_id(provider_id)
                    if not provider_config:
                        raise ValidationError(f"AI服务提供商不存在: {provider_id}")

                    # 更新模型配置
                    if "models" in update_data and isinstance(update_data["models"], dict):
                        if "default" in update_data["models"]:
                            new_default = update_data["models"]["default"]
                            if new_default not in provider_config.models.get("available", []):
                                raise ValidationError(f"默认模型 '{new_default}' 不在可用模型列表中")
                            provider_config.models["default"] = new_default

                        if "available" in update_data["models"]:
                            provider_config.models["available"] = update_data["models"]["available"]

                updated_fields.append(field)

        # 保存配置到文件
        settings.save_to_json()

        # 重新加载AI服务
        qa_service.ai_service_manager.reload_providers()

        return jsonify({
            "success": True,
            "data": {
                "message": "配置更新成功",
                "updated_fields": updated_fields
            }
        })

    except ValidationError as e:
        logger.warning(f"数据验证错误: {str(e)}")
        return jsonify(ErrorResponse.validation_error({"error": str(e)}).dict()), 400
    except Exception as e:
        logger.error(f"更新AI配置失败: {str(e)}")
        return jsonify(ErrorResponse(error="更新配置失败").dict()), 500


@query_bp.route('/questions', methods=['POST'])
def add_question() -> Dict[str, Any]:
    """
    添加新题目

    Request Body:
        JSON: 题目数据

    Returns:
        JSON: 添加结果
    """
    try:
        question_data = request.get_json()
        if not question_data:
            raise ValidationError("请求体不能为空")

        # 验证必需字段
        required_fields = ["question_text", "answer"]
        for field in required_fields:
            if field not in question_data or not question_data[field]:
                raise ValidationError(f"缺少必需字段: {field}")

        # 调用业务逻辑添加题目
        question = qa_service.add_question(
            question_text=question_data["question_text"],
            answer=question_data["answer"],
            options=question_data.get("options"),
            question_type=question_data.get("question_type")
        )

        return jsonify({
            "success": True,
            "data": {
                "message": "题目添加成功",
                "question": question.to_dict()
            }
        })

    except ValidationError as e:
        logger.warning(f"数据验证错误: {str(e)}")
        return jsonify(ErrorResponse.validation_error({"error": str(e)}).dict()), 400
    except Exception as e:
        logger.error(f"添加题目失败: {str(e)}")
        return jsonify(ErrorResponse(error="添加题目失败").dict()), 500


@query_bp.route('/questions/<int:question_id>', methods=['PUT'])
def update_question(question_id: int) -> Dict[str, Any]:
    """
    更新题目

    Args:
        question_id: 题目ID

    Request Body:
        JSON: 更新的题目数据

    Returns:
        JSON: 更新结果
    """
    try:
        update_data = request.get_json()
        if not update_data:
            raise ValidationError("请求体不能为空")

        # 这里可以实现更新题目的逻辑
        # 目前先返回成功响应
        return jsonify({
            "success": True,
            "data": {
                "message": f"题目 {question_id} 更新成功",
                "question_id": question_id
            }
        })

    except ValidationError as e:
        logger.warning(f"数据验证错误: {str(e)}")
        return jsonify(ErrorResponse.validation_error({"error": str(e)}).dict()), 400
    except Exception as e:
        logger.error(f"更新题目失败: {str(e)}")
        return jsonify(ErrorResponse(error="更新题目失败").dict()), 500


@query_bp.route('/questions/<int:question_id>', methods=['DELETE'])
def delete_question(question_id: int) -> Dict[str, Any]:
    """
    删除题目

    Args:
        question_id: 题目ID

    Returns:
        JSON: 删除结果
    """
    try:
        # 调用业务逻辑删除题目
        success = qa_service.delete_question(question_id)

        if success:
            return jsonify({
                "success": True,
                "data": {
                    "message": f"题目 {question_id} 删除成功",
                    "question_id": question_id
                }
            })
        else:
            return jsonify(ErrorResponse.validation_error({"error": "题目不存在或删除失败"}).dict()), 400

    except ValidationError as e:
        logger.warning(f"数据验证错误: {str(e)}")
        return jsonify(ErrorResponse.validation_error({"error": str(e)}).dict()), 400
    except Exception as e:
        logger.error(f"删除题目失败: {str(e)}")
        return jsonify(ErrorResponse(error="删除题目失败").dict()), 500