import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.core.database import Base


class CertificateType(str, enum.Enum):
    participant = "participant"   # участник I этапа
    mentor = "mentor"             # руководитель
    winner = "winner"             # победитель
    expert = "expert"             # эксперт


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    number = Column(String, unique=True, index=True, nullable=False)  # уникальный номер
    type = Column(Enum(CertificateType), default=CertificateType.participant)
    title = Column(String, nullable=False)
    qr_payload = Column(String, nullable=False)   # ссылка / данные для QR
    file_path = Column(String, nullable=True)     # путь к PDF

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="certificates")