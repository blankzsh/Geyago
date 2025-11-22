"""
API端点测试

测试各个API路由的功能
"""

import pytest
import json
from unittest.mock import Mock, patch

from src.geyago.services.qa_service import qa_service
from src.geyago.models.question import QuestionRepository


class TestQueryAPI:
    """查询API测试类"""

    def test_query_request_validation(self):
        """测试查询请求验证"""
        # 这里稍后需要集成Flask客户端测试
        pass

    def test_successful_query_with_database_result(self, test_database, sample_questions):
        """测试成功的查询（数据库中有结果）"""
        # 准备测试数据
        question_data = sample_questions[0]

        # 添加到测试数据库
        question = qa_service.add_question(**question_data)

        # 测试查询
        result = qa_service.query_answer(
            question_text=question_data["question_text"],
            options=question_data["options"],
            question_type=question_data["question_type"]
        )

        # 验证结果
        assert result["code"] == 1
        assert result["data"] == question_data["answer"]
        assert result["source"] == "database"

    @patch('src.geyago.services.ai_service.ai_service.query_answer')
    def test_successful_query_with_ai_result(self, mock_ai_query, test_database, sample_questions):
        """测试成功的查询（AI生成结果）"""
        # 模拟AI服务返回
        mock_ai_query.return_value = "AI生成的答案"

        # 测试一个数据库中不存在的问题
        result = qa_service.query_answer(
            question_text="一个不存在的问题",
            options="A. 选项1 B. 选项2",
            question_type="single"
        )

        # 验证AI服务被调用
        mock_ai_query.assert_called_once()

        # 验证结果
        assert result["code"] == 1
        assert result["data"] == "AI生成的答案"
        assert result["source"] == "ai"

    def test_query_empty_question(self):
        """测试空问题查询"""
        with pytest.raises(Exception) as exc_info:
            qa_service.query_answer(question_text="", options="", question_type="")

        # 验证异常类型
        assert "验证" in str(exc_info.value) or "empty" in str(exc_info.value).lower()

    def test_query_whitespace_only_question(self):
        """测试只包含空白字符的问题"""
        with pytest.raises(Exception):
            qa_service.query_answer(question_text="   \n\t   ", options="", question_type="")

    def test_ai_service_error_handling(self, test_database):
        """测试AI服务错误处理"""
        # 测试一个不存在的问题，但AI服务可能会失败
        result = qa_service.query_answer(
            question_text="一个复杂的问题",
            options="A. 选项1 B. 选项2",
            question_type="single"
        )

        # 即使AI失败，也应该返回合理的响应
        assert "code" in result
        assert "msg" in result


class TestQuestionManagementAPI:
    """问题管理API测试类"""

    def test_add_question_success(self, test_database, sample_questions):
        """测试成功添加问题"""
        question_data = sample_questions[0]

        question = qa_service.add_question(**question_data)

        # 验证问题被正确保存
        assert question.question == question_data["question_text"]
        assert question.answer == question_data["answer"]
        assert question.options == question_data["options"]
        assert question.question_type == question_data["question_type"]
        assert question.id is not None

    def test_add_duplicate_question(self, test_database, sample_questions):
        """测试添加重复问题"""
        question_data = sample_questions[0]

        # 第一次添加应该成功
        qa_service.add_question(**question_data)

        # 第二次添加应该失败
        with pytest.raises(Exception) as exc_info:
            qa_service.add_question(**question_data)

        assert "已存在" in str(exc_info.value) or "duplicate" in str(exc_info.value).lower()

    def test_add_empty_question(self, test_database):
        """测试添加空问题"""
        with pytest.raises(Exception):
            qa_service.add_question(
                question_text="",
                answer="答案",
                options="",
                question_type=""
            )

    def test_add_empty_answer(self, test_database):
        """测试添加空答案"""
        with pytest.raises(Exception):
            qa_service.add_question(
                question_text="问题",
                answer="",
                options="",
                question_type=""
            )

    def test_search_questions(self, test_database, sample_questions):
        """测试搜索问题"""
        # 添加测试数据
        for q_data in sample_questions:
            qa_service.add_question(**q_data)

        # 搜索测试
        results = qa_service.search_questions("Python")

        # 验证搜索结果
        assert len(results) >= 1
        assert any("Python" in q.question for q in results)

    def test_get_recent_questions(self, test_database, sample_questions):
        """测试获取最近问题"""
        # 添加测试数据
        for q_data in sample_questions:
            qa_service.add_question(**q_data)

        # 获取最近问题
        recent_questions = qa_service.get_recent_questions(limit=2)

        # 验证结果
        assert len(recent_questions) <= 2
        assert all(q.id is not None for q in recent_questions)

    def test_get_statistics(self, test_database, sample_questions):
        """测试获取统计信息"""
        # 添加测试数据
        for q_data in sample_questions:
            qa_service.add_question(**q_data)

        # 获取统计信息
        stats = qa_service.get_question_statistics()

        # 验证统计信息
        assert "total_questions" in stats
        assert "service_status" in stats
        assert stats["total_questions"] >= len(sample_questions)


class TestHealthCheckAPI:
    """健康检查API测试类"""

    def test_health_check(self, test_database):
        """测试健康检查"""
        stats = qa_service.get_question_statistics()

        # 验证健康检查返回结构
        assert "total_questions" in stats
        assert "service_status" in stats
        assert "database" in stats["service_status"]
        assert "ai_service" in stats["service_status"]


class TestErrorHandling:
    """错误处理测试类"""

    def test_database_error_handling(self):
        """测试数据库错误处理"""
        # 这里可以模拟数据库连接错误
        pass

    def test_ai_service_timeout_handling(self):
        """测试AI服务超时处理"""
        # 这里可以模拟AI服务超时
        pass


# 集成测试类
class TestAPIIntegration:
    """API集成测试"""

    def test_complete_workflow(self, test_database):
        """测试完整的工作流程"""
        # 1. 添加问题
        question = qa_service.add_question(
            question_text="测试问题",
            answer="测试答案",
            options="A. 选项1 B. 选项2",
            question_type="single"
        )

        # 2. 查询问题
        result = qa_service.query_answer(
            question_text="测试问题",
            options="A. 选项1 B. 选项2",
            question_type="single"
        )

        # 3. 验证结果
        assert result["code"] == 1
        assert result["data"] == "测试答案"
        assert result["source"] == "database"

        # 4. 搜索问题
        search_results = qa_service.search_questions("测试")
        assert len(search_results) >= 1
        assert question.id in [q.id for q in search_results]