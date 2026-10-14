import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProjectStatus(str, enum.Enum):
    draft = "черновик"
    submitted = "на проверке"
    admitted = "допущена"
    on_review = "на экспертизе"
    graded = "оценена"
    rejected = "отклонена"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    category = Column(String, index=True)           # номинация
    description = Column(Text)
    annotation = Column(Text)

    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Файлы
    file_url = Column(String, nullable=True)        # PDF/DOCX
    presentation_url = Column(String, nullable=True)  # PDF/PPTX
    video_url = Column(String, nullable=True)       # ссылка или файл

    status = Column(Enum(ProjectStatus), default=ProjectStatus.draft, index=True)
    region = Column(String, index=True)             # денормализация для аналитики
    school = Column(String, index=True)

    score = Column(Float, nullable=True)            # итоговый рейтинг
    final_place = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = relationship("User", foreign_keys=[author_id], back_populates="projects")
    mentor = relationship("User", foreign_keys=[mentor_id])
    reviews = relationship("Review", back_populates="project", cascade="all, delete-orphan")