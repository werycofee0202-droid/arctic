from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.certificate import CertificateType


class CertificateResponse(BaseModel):
    id: int
    user_id: int
    number: str
    type: CertificateType
    title: str
    qr_payload: str
    file_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True