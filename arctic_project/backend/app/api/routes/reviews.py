from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.project import Project, ProjectStatus
from app.models.review import Review
from app.models.user import User, UserRole
from app.schemas.review import ReviewCreate, ReviewResponse

router = APIRouter(prefix="/reviews", tags=["Reviews"])

# Коэффициенты значимости критериев (настраиваются)
CRITERIA_WEIGHTS: dict[str, float] = {
    "актуальность": 0.2,
    "новизна": 0.2,
    "научность": 0.2,
    "практическая_значимость": 0.2,
    "оформление": 0.1,
    "презентация": 0.1,
}


def _weighted(criteria: dict[str, float]) -> float:
    total = 0.0
    for key, value in criteria.items():
        total += value * CRITERIA_WEIGHTS.get(key, 0.1)
    return round(total, 2)


@router.post("/", response_model=ReviewResponse)
def create_review(
    payload: ReviewCreate,
    expert: User = Depends(require_roles(UserRole.expert, UserRole.commission)),
    db: Session = Depends(get_db),
):
    project = db.query(Project).get(payload.project_id)
    if not project:
        raise HTTPException(404, "Проект не найден")

    exists = (
        db.query(Review)
        .filter(Review.project_id == project.id, Review.expert_id == expert.id)
        .first()
    )
    if exists:
        raise HTTPException(400, "Вы уже оценивали этот проект")

    review = Review(
        project_id=project.id,
        expert_id=expert.id,
        criteria_scores=payload.criteria_scores,
        weighted_score=_weighted(payload.criteria_scores),
        comment=payload.comment,
        recommendation=payload.recommendation,
    )
    db.add(review)
    db.flush()

    # Пересчёт среднего рейтинга проекта
    all_reviews = db.query(Review).filter(Review.project_id == project.id).all()
    project.score = round(
        sum(r.weighted_score or 0 for r in all_reviews) / len(all_reviews), 2
    )
    project.status = ProjectStatus.graded if all_reviews else ProjectStatus.on_review

    db.commit()
    db.refresh(review)
    return review


@router.get("/project/{project_id}", response_model=list[ReviewResponse])
def get_project_reviews(
    project_id: int,
    _: User = Depends(require_roles(UserRole.expert, UserRole.commission, UserRole.admin)),
    db: Session = Depends(get_db),
):
    return db.query(Review).filter(Review.project_id == project_id).all()