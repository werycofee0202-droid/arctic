import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserRole(str, enum.Enum):
    participant = "participant"      # школьник
    mentor = "mentor"                # руководитель (педагог)
    expert = "expert"                # эксперт
    commission = "commission"        # член комиссии
    admin = "admin"                  # администратор
    partner = "partner"              # партнёр


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # может быть NULL если через VK ID
    vk_id = Column(String, unique=True, nullable=True, index=True)

    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.participant, nullable=False)

    # Участник
    birth_date = Column(DateTime, nullable=True)
    grade = Column(String, nullable=True)      # класс
    school = Column(String, nullable=True)
    region = Column(String, nullable=True, index=True)
    parent_contact = Column(String, nullable=True)  # контакт законного представителя

    # Педагог / эксперт
    organization = Column(String, nullable=True)
    position = Column(String, nullable=True)

    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    mentor_confirmed = Column(Boolean, default=False)
    mentor = relationship("User", remote_side=[id], backref="students")

    # Согласия 152-ФЗ
    consent_personal_data = Column(Boolean, default=False)
    consent_confirmed_at = Column(DateTime, nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    projects = relationship("Project", back_populates="author", foreign_keys="Project.author_id")
    certificates = relationship("Certificate", back_populates="user")