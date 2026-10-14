from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class TestQuestion(Base):
    __tablename__ = "test_questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)          # ["вариант 1", "вариант 2", ...]
    correct_index = Column(Integer, nullable=False)
    category = Column(String, index=True)
    difficulty = Column(Integer, default=1)         # 1..5
    is_active = Column(Boolean, default=True)


class TestAttempt(Base):
    __tablename__ = "test_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    questions_json = Column(JSON, nullable=False)   # какие вопросы выданы
    answers_json = Column(JSON, nullable=True)      # ответы пользователя
    score = Column(Integer, default=0)
    max_score = Column(Integer, default=0)
    passed = Column(Boolean, default=False)

    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)