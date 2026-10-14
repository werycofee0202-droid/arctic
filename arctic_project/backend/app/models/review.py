from datetime import datetime

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    expert_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Оценки по критериям: {"критерий_1": 8, "критерий_2": 9}
    criteria_scores = Column(JSON, nullable=False, default=dict)
    weighted_score = Column(Float, nullable=True)   # итоговый с коэффициентами
    comment = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="reviews")