"""
问题模型模块

定义问题相关的数据模型和数据库操作
"""

from __future__ import annotations
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass

from ..core.database import db_manager
from ..core.exceptions import DatabaseError, QuestionNotFoundError


@dataclass
class Question:
    """问题数据模型"""
    id: Optional[int] = None
    question: str = ""
    answer: str = ""
    options: Optional[str] = None
    question_type: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_db_row(cls, row) -> Question:
        """从数据库行创建Question实例"""
        if row is None:
            return None

        return cls(
            id=row['id'],
            question=row['question'],
            answer=row['answer'],
            options=row['options'],
            question_type=row['type'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'options': self.options,
            'type': self.question_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class QuestionRepository:
    """问题数据访问层"""

    @staticmethod
    def find_by_question(question_text: str) -> Optional[Question]:
        """根据问题文本查找问题"""
        try:
            row = db_manager.execute_query(
                "SELECT * FROM question_answer WHERE question = ?",
                (question_text,),
                fetch_one=True
            )
            return Question.from_db_row(row)
        except Exception as e:
            raise DatabaseError(f"查询问题失败: {str(e)}")

    @staticmethod
    def find_similar_questions(question_text: str, limit: int = 5) -> List[Question]:
        """查找相似问题（简单实现，基于模糊匹配）"""
        try:
            rows = db_manager.execute_query(
                """
                SELECT *,
                       (LENGTH(question) - LENGTH(REPLACE(LOWER(question), LOWER(?), ''))) as similarity_score
                FROM question_answer
                WHERE LOWER(question) LIKE LOWER(?)
                ORDER BY similarity_score DESC, length(question) ASC
                LIMIT ?
                """,
                (question_text, f"%{question_text}%", limit),
                fetch_all=True
            )
            return [Question.from_db_row(row) for row in rows] if rows else []
        except Exception as e:
            raise DatabaseError(f"查找相似问题失败: {str(e)}")

    @staticmethod
    def save(question: Question) -> Question:
        """保存问题到数据库"""
        try:
            if question.id is None:
                # 新增问题
                question.id = db_manager.execute_query(
                    """
                    INSERT INTO question_answer
                    (question, answer, options, type)
                    VALUES (?, ?, ?, ?)
                    """,
                    (question.question, question.answer, question.options,
                     question.question_type)
                )
            else:
                # 更新问题
                db_manager.execute_query(
                    """
                    UPDATE question_answer
                    SET question=?, answer=?, options=?, type=?
                    WHERE id=?
                    """,
                    (question.question, question.answer, question.options,
                     question.question_type, question.id)
                )

            # 重新获取更新后的数据
            return QuestionRepository.find_by_question(question.question)
        except Exception as e:
            raise DatabaseError(f"保存问题失败: {str(e)}")

    @staticmethod
    def create_question(
        question_text: str,
        answer: str,
        options: Optional[str] = None,
        question_type: Optional[str] = None
    ) -> Question:
        """创建新问题"""
        question = Question(
            question=question_text,
            answer=answer,
            options=options,
            question_type=question_type
        )
        return QuestionRepository.save(question)

    @staticmethod
    def get_all_questions(limit: int = 100, offset: int = 0) -> List[Question]:
        """获取所有问题列表"""
        try:
            rows = db_manager.execute_query(
                "SELECT * FROM question_answer ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
                fetch_all=True
            )
            if rows:
                return [Question.from_db_row(dict(row)) for row in rows]
            else:
                return []
        except Exception as e:
            raise DatabaseError(f"获取问题列表失败: {str(e)}")

    @staticmethod
    def count_questions() -> int:
        """统计问题总数"""
        try:
            row = db_manager.execute_query(
                "SELECT COUNT(*) as count FROM question_answer",
                fetch_one=True
            )
            return row['count'] if row else 0
        except Exception as e:
            raise DatabaseError(f"统计问题数量失败: {str(e)}")

    @staticmethod
    def delete_question(question_id: int) -> bool:
        """删除问题"""
        try:
            db_manager.execute_query(
                "DELETE FROM question_answer WHERE id = ?",
                (question_id,)
            )
            return True
        except Exception as e:
            raise DatabaseError(f"删除问题失败: {str(e)}")

    @staticmethod
    def get_questions_by_type(question_type: str) -> List[Question]:
        """根据类型获取问题"""
        try:
            rows = db_manager.execute_query(
                "SELECT * FROM question_answer WHERE type = ? ORDER BY created_at DESC",
                (question_type,),
                fetch_all=True
            )
            return [Question.from_db_row(row) for row in rows] if rows else []
        except Exception as e:
            raise DatabaseError(f"根据类型获取问题失败: {str(e)}")

    @staticmethod
    def search_questions(keyword: str) -> List[Question]:
        """搜索问题"""
        try:
            rows = db_manager.execute_query(
                """
                SELECT * FROM question_answer
                WHERE question LIKE ? OR answer LIKE ? OR options LIKE ?
                ORDER BY created_at DESC
                """,
                (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"),
                fetch_all=True
            )
            return [Question.from_db_row(row) for row in rows] if rows else []
        except Exception as e:
            raise DatabaseError(f"搜索问题失败: {str(e)}")