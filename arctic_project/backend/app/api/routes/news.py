from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.news import News
from app.models.user import User, UserRole
from app.schemas.news import NewsCreate, NewsResponse

router = APIRouter(prefix="/news", tags=["News"])


@router.get("/", response_model=list[NewsResponse])
def list_news(limit: int = 10, db: Session = Depends(get_db)):
    return (
        db.query(News)
        .filter(News.is_published == True)
        .order_by(News.created_at.desc())
        .limit(limit)
        .all()
    )


@router.post("/", response_model=NewsResponse)
def create_news(
    payload: NewsCreate,
    _: User = Depends(require_roles(UserRole.admin)),
    db: Session = Depends(get_db),
):
    news = News(**payload.model_dump())
    db.add(news)
    db.commit()
    db.refresh(news)
    return news


@router.delete("/{news_id}")
def delete_news(
    news_id: int,
    _: User = Depends(require_roles(UserRole.admin)),
    db: Session = Depends(get_db),
):
    news = db.query(News).get(news_id)
    if not news:
        raise HTTPException(404, "Новость не найдена")
    db.delete(news)
    db.commit()
    return {"ok": True}
