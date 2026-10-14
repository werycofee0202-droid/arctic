from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.participant


class UserCreate(UserBase):
    password: Optional[str] = None
    birth_date: Optional[datetime] = None
    grade: Optional[str] = None
    school: Optional[str] = None
    region: Optional[str] = None
    parent_contact: Optional[str] = None
    organization: Optional[str] = None
    position: Optional[str] = None
    consent_personal_data: bool = False


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    grade: Optional[str] = None
    school: Optional[str] = None
    region: Optional[str] = None
    parent_contact: Optional[str] = None
    organization: Optional[str] = None
    position: Optional[str] = None
    mentor_id: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    grade: Optional[str] = None
    school: Optional[str] = None
    region: Optional[str] = None
    mentor_id: Optional[int] = None
    mentor_confirmed: bool = False
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse