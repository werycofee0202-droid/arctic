from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NewsCreate(BaseModel):
    title: str
    body: str
    cover_url: Optional[str] = None
    is_published: bool = True


class NewsResponse(BaseModel):
    id: int
    title: str
    body: str
    cover_url: Optional[str] = None
    is_published: bool
    created_at: datetime

    class Config:
        from_attributes = True