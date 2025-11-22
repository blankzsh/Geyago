"""
pytest配置文件

定义测试夹具和配置
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.geyago.config.settings import settings
from src.geyago.core.database import DatabaseManager


@pytest.fixture(scope="session")
def test_database():
    """测试数据库夹具"""
    # 创建临时数据库文件
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name

    # 更新settings使用测试数据库
    original_db_url = settings.database_url
    settings.database_url = f"sqlite:///{db_path}"

    # 初始化测试数据库
    test_db_manager = DatabaseManager()
    test_db_manager.init_database()

    yield test_db_manager

    # 清理
    os.unlink(db_path)
    settings.database_url = original_db_url


@pytest.fixture
def sample_questions():
    """示例问题数据夹具"""
    return [
        {
            "question_text": "Python是什么？",
            "answer": "一种高级编程语言",
            "options": "A. 编程语言 B. 一种咖啡 C. 游戏 D. 食物",
            "question_type": "single"
        },
        {
            "question_text": "1+1等于几？",
            "answer": "2",
            "options": "A.1 B.2 C.3 D.4",
            "question_type": "single"
        },
        {
            "question_text": "地球是圆的，对吗？",
            "answer": "对",
            "options": "",
            "question_type": "judgement"
        },
        {
            "question_text": "中国的首都是__",
            "answer": "北京",
            "options": "",
            "question_type": "fill"
        }
    ]


@pytest.fixture
def mock_api_key():
    """模拟API密钥夹具"""
    original_key = settings.api_key
    settings.api_key = "test_api_key_12345"
    yield settings.api_key
    settings.api_key = original_key


@pytest.fixture
def client(test_database):
    """Flask测试客户端夹具"""
    # 这里需要导入Flask应用，稍后在main模块重构后再完善
    pass