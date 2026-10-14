import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.database import get_db
from app.models.test import TestQuestion, TestAttempt
from app.models.user import User, UserRole
from app.schemas.test import (
    TestQuestionResponse, TestStartResponse, TestSubmit, TestAttemptResponse,
)

router = APIRouter(prefix="/tests", tags=["Tests"])

QUESTIONS_PER_ATTEMPT = 20
DURATION_SECONDS = 30 * 60


@router.post("/start", response_model=TestStartResponse)
def start_test(
    current_user: User = Depends(require_roles(UserRole.participant)),
    db: Session = Depends(get_db),
):
    # Блокируем повторную попытку, если уже есть завершённая
    finished = (
        db.query(TestAttempt)
        .filter(TestAttempt.user_id == current_user.id, TestAttempt.finished_at.isnot(None))
        .first()
    )
    if finished:
        raise HTTPException(400, "Вы уже проходили тестирование")

    pool = db.query(TestQuestion).filter(TestQuestion.is_active == True).all()
    if len(pool) < QUESTIONS_PER_ATTEMPT:
        raise HTTPException(500, "Недостаточно вопросов в банке")

    selected = random.sample(pool, QUESTIONS_PER_ATTEMPT)
    attempt = TestAttempt(
        user_id=current_user.id,
        questions_json=[q.id for q in selected],
        max_score=len(selected),
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return TestStartResponse(
        attempt_id=attempt.id,
        questions=[TestQuestionResponse.model_validate(q) for q in selected],
        max_score=attempt.max_score,
        duration_seconds=DURATION_SECONDS,
    )


@router.post("/submit", response_model=TestAttemptResponse)
def submit_test(
    payload: TestSubmit,
    current_user: User = Depends(require_roles(UserRole.participant)),
    db: Session = Depends(get_db),
):
    attempt = db.query(TestAttempt).get(payload.attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise HTTPException(404, "Попытка не найдена")
    if attempt.finished_at:
        raise HTTPException(400, "Попытка уже завершена")

    question_ids: list[int] = attempt.questions_json
    questions = db.query(TestQuestion).filter(TestQuestion.id.in_(question_ids)).all()
    qmap = {q.id: q for q in questions}

    if len(payload.answers) != len(question_ids):
        raise HTTPException(400, "Неверное количество ответов")

    score = 0
    for qid, ans in zip(question_ids, payload.answers):
        q = qmap.get(qid)
        if q and q.correct_index == ans:
            score += 1

    attempt.answers_json = payload.answers
    attempt.score = score
    attempt.passed = score >= int(attempt.max_score * 0.6)  # порог 60%
    attempt.finished_at = datetime.utcnow()
    db.commit()