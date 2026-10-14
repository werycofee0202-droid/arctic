from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.project import Project, ProjectStatus
from app.models.user import User, UserRole

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
def summary(
    _: User = Depends(require_roles(UserRole.admin, UserRole.commission)),
    db: Session = Depends(get_db),
):
    participants = db.query(func.count(User.id)).filter(User.role == UserRole.participant).scalar()
    projects = db.query(func.count(Project.id)).scalar()
    regions = db.query(func.count(func.distinct(User.region))).filter(User.region.isnot(None)).scalar()
    schools = db.query(func.count(func.distinct(User.school))).filter(User.school.isnot(None)).scalar()
    return {
        "participants": participants,
        "projects": projects,
        "regions": regions,
        "schools": schools,
    }


@router.get("/by-region")
def by_region(
    _: User = Depends(require_roles(UserRole.admin, UserRole.commission)),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(User.region, func.count(User.id))
        .filter(User.role == UserRole.participant, User.region.isnot(None))
        .group_by(User.region)
        .all()
    )
    return [{"region": r, "count": c} for r, c in rows]


@router.get("/by-category")
def by_category(
    _: User = Depends(require_roles(UserRole.admin, UserRole.commission)),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Project.category, func.count(Project.id))
        .group_by(Project.category)
        .all()
    )
    return [{"category": c, "count": n} for c, n in rows]


@router.get("/by-status")
def by_status(
    _: User = Depends(require_roles(UserRole.admin, UserRole.commission)),
    db: Session = Depends(get_db),
):
    rows = db.query(Project.status, func.count(Project.id)).group_by(Project.status).all()
    return [{"status": s.value, "count": n} for s, n in rows]


@router.get("/public/counter")
def public_counter(db: Session = Depends(get_db)):
    """Счётчик участников для главной страницы (без авторизации)."""
    total = db.query(func.count(User.id)).filter(User.role == UserRole.participant).scalar()
    return {"participants": total}