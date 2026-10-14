from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.database import get_db
from app.models.certificate import Certificate, CertificateType
from app.models.test import TestAttempt
from app.models.user import User, UserRole
from app.schemas.certificate import CertificateResponse
from app.services.certificate import generate_certificate_pdf, make_number

router = APIRouter(prefix="/certificates", tags=["Certificates"])


@router.get("/my", response_model=list[CertificateResponse])
def my_certificates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Certificate).filter(Certificate.user_id == current_user.id).all()


@router.post("/participant/auto", response_model=CertificateResponse)
def auto_issue_participant(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Автогенерация сертификата участника после успешного теста."""
    attempt = (
        db.query(TestAttempt)
        .filter(TestAttempt.user_id == current_user.id, TestAttempt.passed == True)
        .first()
    )
    if not attempt:
        raise HTTPException(400, "Тест не сдан — сертификат недоступен")

    existing = (
        db.query(Certificate)
        .filter(Certificate.user_id == current_user.id, Certificate.type == CertificateType.participant)
        .first()
    )
    if existing:
        return existing

    number = make_number("ARC-P")
    qr_payload = f"{settings_frontend_check(number)}"
    title = "Сертификат участника I этапа"
    file_path = generate_certificate_pdf(current_user.full_name, title, number, qr_payload)

    cert = Certificate(
        user_id=current_user.id,
        number=number,
        type=CertificateType.participant,
        title=title,
        qr_payload=qr_payload,
        file_path=file_path,
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert


def settings_frontend_check(number: str) -> str:
    from app.core.config import settings
    return f"{settings.FRONTEND_URL}/verify/{number}"


@router.get("/{certificate_id}/download")
def download(
    certificate_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cert = db.query(Certificate).get(certificate_id)
    if not cert:
        raise HTTPException(404, "Сертификат не найден")
    if cert.user_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(403, "Нет доступа")
    return FileResponse(cert.file_path, filename=f"{cert.number}.pdf", media_type="application/pdf")


@router.post("/issue", response_model=CertificateResponse)
def issue_manual(
    user_id: int,
    title: str,
    type: CertificateType,
    _: User = Depends(require_roles(UserRole.admin)),
    db: Session = Depends(get_db),
):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    number = make_number("ARC")
    qr_payload = settings_frontend_check(number)
    file_path = generate_certificate_pdf(user.full_name, title, number, qr_payload)
    cert = Certificate(
        user_id=user.id, number=number, type=type, title=title,
        qr_payload=qr_payload, file_path=file_path,
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert