"""
数据库连接和初始化模块

提供数据库连接管理和表结构初始化功能
"""

from __future__ import annotations
import sqlite3
from typing import Optional, Any, List, Dict
from contextlib import contextmanager
from pathlib import Path

from ..config.settings import settings


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, database_url: str = None):
        self.database_url = database_url or settings.database.url
        self.db_path = Path(settings.database_path)
        self._ensure_database_directory()

    def _ensure_database_directory(self) -> None:
        """确保数据库目录存在"""
        if self.db_path.parent != Path('.'):
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        try:
            conn = sqlite3.connect(
                self.database_url.replace("sqlite:///", ""),
                check_same_thread=False
            )
            conn.row_factory = sqlite3.Row
            # 启用外键约束
            conn.execute("PRAGMA foreign_keys = ON")
            # 设置WAL模式提高并发性能
            conn.execute("PRAGMA journal_mode = WAL")
            return conn
        except Exception as e:
            raise ConnectionError(f"数据库连接失败: {str(e)}")

    @contextmanager
    def get_cursor(self) -> sqlite3.Cursor:
        """获取数据库游标的上下文管理器"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_database(self) -> None:
        """初始化数据库表结构"""
        with self.get_cursor() as cursor:
            # 创建问题答案表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS question_answer (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    options TEXT,
                    type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 创建索引提高查询性能
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_question_answer_question
                ON question_answer(question)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_question_answer_type
                ON question_answer(type)
            ''')

    def execute_query(
        self,
        query: str,
        params: tuple = (),
        fetch_one: bool = False,
        fetch_all: bool = False
    ) -> Optional[Any]:
        """执行查询语句"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)

            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()

            return cursor.lastrowid

    def execute_many(self, query: str, params_list: List[tuple]) -> None:
        """批量执行语句"""
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)

    def table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        with self.get_cursor() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            return cursor.fetchone() is not None

    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """获取表结构信息"""
        with self.get_cursor() as cursor:
            cursor.execute(f"PRAGMA table_info({table_name})")
            return [dict(row) for row in cursor.fetchall()]

    def backup_database(self, backup_path: str) -> None:
        """备份数据库"""
        source = sqlite3.connect(self.database_url.replace("sqlite:///", ""))
        backup = sqlite3.connect(backup_path)
        try:
            source.backup(backup)
        finally:
            source.close()
            backup.close()

    def close_all_connections(self) -> None:
        """关闭所有数据库连接（SQLite特性）"""
        # SQLite会自动管理连接，这里可以实现连接池管理
        pass


# 全局数据库管理器实例
db_manager = DatabaseManager()