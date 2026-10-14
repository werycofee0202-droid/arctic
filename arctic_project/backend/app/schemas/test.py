from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TestQuestionResponse(BaseModel):
    id: int
    text: str
    options: list[str]
    category: Optional[str] = None
    difficulty: int

    class Config:
        from_attributes = True


class TestStartResponse(BaseModel):
    attempt_id: int
    questions: list[TestQuestionResponse]
    max_score: int
    duration_seconds: int


class TestSubmit(BaseModel):
    attempt_id: int
    answers: list[int]   # индексы выбранных вариантов в порядке вопросов


class TestAttemptResponse(BaseModel):
    id: int
    user_id: int
    score: int
    max_score: int
    passed: bool
    started_at: datetime
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True