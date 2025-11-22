"""
问答服务模块

整合数据库和AI服务，提供统一的问答业务逻辑
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
import logging

from ..models.question import QuestionRepository, Question
from ..services.ai_service import ai_service, AIServiceError
from ..services.ai_service_manager import ai_service_manager
from ..core.exceptions import DatabaseError, ValidationError, QuestionNotFoundError

# 配置日志
logger = logging.getLogger(__name__)


class QAService:
    """问答服务类"""

    def __init__(self):
        self.question_repo = QuestionRepository()
        self.ai_service_manager = ai_service_manager

    def query_answer(
        self,
        question_text: str,
        options: Optional[str] = None,
        question_type: Optional[str] = None,
        provider_id: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """查询答案（支持多AI接口）"""
        try:
            logger.info(f"查询问题: {question_text[:50]}...")

            # 第一步：在本地数据库中搜索
            question = self._search_local_database(question_text)
            if question:
                logger.info("在本地数据库中找到答案: %s...", question.answer[:50] if question.answer else "None")
                return {
                    "code": 0,
                    "data": question.answer,
                    "msg": "数据库匹配",
                    "source": "database"
                }

            # 第二步：使用AI生成答案
            logger.info("本地数据库中未找到答案，尝试AI生成...")
            ai_answer = self._generate_ai_answer(question_text, options or "", question_type or "", provider_id, model)

            if ai_answer:
                # 保存AI生成的答案到数据库
                try:
                    self._save_ai_answer(question_text, ai_answer, options or "", question_type or "")
                    logger.info("AI答案已保存到数据库")
                except DatabaseError as e:
                    # 保存失败不应该影响返回结果，记录日志即可
                    logger.error(f"保存AI答案到数据库失败: {str(e)}")

                return {
                    "code": 1,
                    "data": ai_answer,
                    "msg": "AI生成答案",
                    "source": "ai"
                }

            # 第三步：都未找到答案
            logger.info("AI服务也未生成有效答案")
            return {
                "code": 0,
                "data": None,
                "msg": "未找到答案",
                "source": None
            }

        except (DatabaseError, AIServiceError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"查询答案时发生未知错误: {str(e)}")
            raise DatabaseError(f"查询失败: {str(e)}")

    def _search_local_database(self, question_text: str) -> Optional[Question]:
        """在本地数据库中搜索问题"""
        try:
            # 精确匹配
            question = self.question_repo.find_by_question(question_text)

            if question:
                logger.debug(f"精确匹配找到问题: {question.id}")
                return question

            return None

        except Exception as e:
            logger.error(f"搜索本地数据库失败: {str(e)}")
            raise DatabaseError(f"数据库搜索失败: {str(e)}")

    def _generate_ai_answer(
        self,
        question_text: str,
        options: str,
        question_type: str,
        provider_id: Optional[str] = None,
        model: Optional[str] = None
    ) -> Optional[str]:
        """使用AI生成答案（支持多接口）"""
        try:
            logger.debug(f"开始AI生成答案，参数: question={question_text}, options={options}, type={question_type}, provider={provider_id}, model={model}")

            # 确保AI服务管理器已初始化
            if not self.ai_service_manager.providers:
                logger.info("AI服务管理器未初始化，正在初始化...")
                self.ai_service_manager.settings = __import__('geyago.config.settings', fromlist=['settings']).settings
                self.ai_service_manager.initialize()

            answer = self.ai_service_manager.query_answer(question_text, options, question_type, provider_id, model)

            if answer:
                logger.info(f"AI生成答案成功: {answer[:50]}...")
                return answer
            else:
                logger.warning("AI未能生成有效答案")
                return None

        except AIServiceError as e:
            logger.error(f"AI服务错误: {str(e)}")
            # AI服务错误不应该中断整个流程，返回None让业务逻辑继续
            return None
        except Exception as e:
            logger.error(f"AI生成答案时发生未知错误: {str(e)}")
            return None

    def _save_ai_answer(
        self,
        question_text: str,
        answer: str,
        options: str,
        question_type: str
    ) -> Question:
        """保存AI生成的答案到数据库"""
        try:
            return self.question_repo.create_question(
                question_text=question_text,
                answer=answer,
                options=options,
                question_type=question_type
            )
        except Exception as e:
            logger.error(f"保存AI答案失败: {str(e)}")
            raise DatabaseError(f"保存答案失败: {str(e)}")

    def add_question(
        self,
        question_text: str,
        answer: str,
        options: Optional[str] = None,
        question_type: Optional[str] = None
    ) -> Question:
        """手动添加问题和答案"""
        # 验证输入
        if not question_text or not question_text.strip():
            raise ValidationError("问题文本不能为空")

        if not answer or not answer.strip():
            raise ValidationError("答案不能为空")

        # 检查问题是否已存在
        existing = self.question_repo.find_by_question(question_text.strip())
        if existing:
            raise ValidationError("问题已存在")

        return self.question_repo.create_question(
            question_text=question_text.strip(),
            answer=answer.strip(),
            options=options.strip() if options else None,
            question_type=question_type.strip() if question_type else None
        )

    def get_question_statistics(self) -> Dict[str, Any]:
        """获取题库统计信息"""
        try:
            total_count = self.question_repo.count_questions()

            # 检查AI服务健康状态
            ai_healthy = True
            try:
                health_status = self.ai_service_manager.health_check()
                ai_healthy = any(
                    provider.get("status") == "healthy"
                    for provider in health_status.values()
                )
            except Exception as e:
                logger.warning(f"AI服务健康检查失败: {str(e)}")
                ai_healthy = False

            return {
                "total_questions": total_count,
                "service_status": {
                    "database": "healthy",
                    "ai_service": "healthy" if ai_healthy else "unhealthy"
                }
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            raise DatabaseError(f"获取统计信息失败: {str(e)}")

    def search_questions(self, keyword: str, limit: int = 10) -> List[Question]:
        """搜索问题"""
        if not keyword or not keyword.strip():
            raise ValidationError("搜索关键词不能为空")

        try:
            return self.question_repo.search_questions(keyword.strip())
        except Exception as e:
            logger.error(f"搜索问题失败: {str(e)}")
            raise DatabaseError(f"搜索问题失败: {str(e)}")

    def get_recent_questions(self, limit: int = 10) -> List[Question]:
        """获取最近添加的问题"""
        try:
            return self.question_repo.get_all_questions(limit=limit)
        except Exception as e:
            logger.error(f"获取最近问题失败: {str(e)}")
            raise DatabaseError(f"获取最近问题失败: {str(e)}")

    def delete_question(self, question_id: int) -> bool:
        """删除问题"""
        if question_id <= 0:
            raise ValidationError("无效的问题ID")

        try:
            return self.question_repo.delete_question(question_id)
        except Exception as e:
            logger.error(f"删除问题失败: {str(e)}")
            raise DatabaseError(f"删除问题失败: {str(e)}")

    def get_providers_info(self) -> Dict[str, Any]:
        """获取AI服务提供商信息"""
        try:
            return ai_service_manager.get_providers_info()
        except Exception as e:
            logger.error(f"获取AI服务提供商信息失败: {str(e)}")
            raise DatabaseError(f"获取提供商信息失败: {str(e)}")

    def get_provider_models(self, provider_id: str) -> List:
        """获取指定AI服务提供商的可用模型列表"""
        try:
            return ai_service_manager.get_provider_models(provider_id)
        except Exception as e:
            logger.error(f"获取AI模型列表失败: {str(e)}")
            raise DatabaseError(f"获取模型列表失败: {str(e)}")

    def set_default_provider(self, provider_id: str) -> bool:
        """设置默认AI服务提供商"""
        try:
            return ai_service_manager.set_default_provider(provider_id)
        except Exception as e:
            logger.error(f"设置默认AI服务提供商失败: {str(e)}")
            raise DatabaseError(f"设置默认提供商失败: {str(e)}")

    def add_model_to_provider(self, provider_id: str, model_name: str) -> bool:
        """向指定AI服务提供商添加模型"""
        try:
            return ai_service_manager.add_model_to_provider(provider_id, model_name)
        except Exception as e:
            logger.error(f"添加模型失败: {str(e)}")
            raise DatabaseError(f"添加模型失败: {str(e)}")

    def remove_model_from_provider(self, provider_id: str, model_name: str) -> bool:
        """从指定AI服务提供商删除模型"""
        try:
            return ai_service_manager.remove_model_from_provider(provider_id, model_name)
        except Exception as e:
            logger.error(f"删除模型失败: {str(e)}")
            raise DatabaseError(f"删除模型失败: {str(e)}")


# 全局问答服务实例
qa_service = QAService()