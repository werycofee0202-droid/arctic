from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.project import ProjectStatus


class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=300)
    category: Optional[str] = None
    description: Optional[str] = None
    annotation: Optional[str] = None
    file_url: Optional[str] = None
    presentation_url: Optional[str] = None
    video_url: Optional[str] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    annotation: Optional[str] = None
    file_url: Optional[str] = None
    presentation_url: Optional[str] = None
    video_url: Optional[str] = None
    status: Optional[ProjectStatus] = None


class ProjectResponse(BaseModel):
    id: int
    title: str
    category: Optional[str] = None
    description: Optional[str] = None
    annotation: Optional[str] = None
    author_id: int
    mentor_id: Optional[int] = None
    file_url: Optional[str] = None
    presentation_url: Optional[str] = None
    video_url: Optional[str] = None
    status: ProjectStatus
    region: Optional[str] = None
    school: Optional[str] = None
    score: Optional[float] = None
    final_place: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True