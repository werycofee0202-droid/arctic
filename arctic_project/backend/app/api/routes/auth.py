from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=Token)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(400, "Email уже зарегистрирован")

    if not payload.consent_personal_data:
        raise HTTPException(400, "Необходимо согласие на обработку персональных данных (152-ФЗ)")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role,
        hashed_password=hash_password(payload.password) if payload.password else None,
        birth_date=payload.birth_date,
        grade=payload.grade,
        school=payload.school,
        region=payload.region,
        parent_contact=payload.parent_contact,
        organization=payload.organization,
        position=payload.position,
        consent_personal_data=payload.consent_personal_data,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.role.value)
    return Token(access_token=token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(401, "Неверный email или пароль")
    if not user.is_active:
        raise HTTPException(403, "Аккаунт заблокирован")

    token = create_access_token(user.id, user.role.value)
    return Token(access_token=token, user=UserResponse.model_validate(user))


@router.post("/vk", response_model=Token)
def login_vk(vk_id: str, full_name: str, email: str, db: Session = Depends(get_db)):
    """
    Упрощённая регистрация/вход через VK ID.
    В реальности vk_id и данные приходят после верификации токена VK.
    """
    user = db.query(User).filter(User.vk_id == vk_id).first()
    if not user:
        user = User(
            vk_id=vk_id,
            email=email,
            full_name=full_name,
            role=UserRole.participant,
            consent_personal_data=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(user.id, user.role.value)
    return Token(access_token=token, user=UserResponse.model_validate(user))