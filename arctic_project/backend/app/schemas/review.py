from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReviewCreate(BaseModel):
    project_id: int
    criteria_scores: dict[str, float]
    comment: Optional[str] = None
    recommendation: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    project_id: int
    expert_id: int
    criteria_scores: dict[str, float]
    weighted_score: Optional[float] = None
    comment: Optional[str] = None
    recommendation: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True