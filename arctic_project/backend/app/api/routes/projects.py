import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.config import settings
from app.core.database import get_db
from app.models.project import Project, ProjectStatus
from app.models.user import User, UserRole
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["Projects"])

ALLOWED_DOC = {".pdf", ".docx"}
ALLOWED_PRES = {".pdf", ".pptx"}


@router.get("/", response_model=list[ProjectResponse])
def get_projects(
    category: str | None = None,
    status: ProjectStatus | None = None,
    region: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Project)
    if category:
        q = q.filter(Project.category == category)
    if status:
        q = q.filter(Project.status == status)
    if region:
        q = q.filter(Project.region == region)
    return q.order_by(Project.created_at.desc()).all()


@router.get("/my", response_model=list[ProjectResponse])
def get_my_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Project).filter(Project.author_id == current_user.id).all()


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).get(project_id)
    if not project:
        raise HTTPException(404, "Проект не найден")
    return project


@router.post("/", response_model=ProjectResponse)
def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(require_roles(UserRole.participant, UserRole.mentor)),
    db: Session = Depends(get_db),
):
    project = Project(
        **payload.model_dump(),
        author_id=current_user.id,
        mentor_id=current_user.mentor_id,
        region=current_user.region,
        school=current_user.school,
        status=ProjectStatus.draft,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).get(project_id)
    if not project:
        raise HTTPException(404, "Проект не найден")
    if project.author_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(403, "Нет прав на изменение")

    data = payload.model_dump(exclude_unset=True)
    # Автор не может сам выставлять статус "оценена"/"допущена"
    if current_user.role != UserRole.admin and "status" in data:
        if data["status"] not in (ProjectStatus.draft, ProjectStatus.submitted):
            raise HTTPException(403, "Смена статуса недоступна")

    for field, value in data.items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


@router.post("/{project_id}/submit", response_model=ProjectResponse)
def submit_project(
    project_id: int,
    current_user: User = Depends(require_roles(UserRole.participant)),
    db: Session = Depends(get_db),
):
    project = db.query(Project).get(project_id)
    if not project or project.author_id != current_user.id:
        raise HTTPException(404, "Проект не найден")
    if not project.file_url:
        raise HTTPException(400, "Загрузите файл проекта")
    project.status = ProjectStatus.submitted
    db.commit()
    db.refresh(project)
    return project


@router.post("/{project_id}/upload/{kind}")
def upload_file(
    project_id: int,
    kind: str,                     # "doc" | "presentation" | "video"
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).get(project_id)
    if not project or project.author_id != current_user.id:
        raise HTTPException(404, "Проект не найден")

    ext = os.path.splitext(file.filename or "")[1].lower()
    if kind == "doc" and ext not in ALLOWED_DOC:
        raise HTTPException(400, "Допустимы только PDF/DOCX")
    if kind == "presentation" and ext not in ALLOWED_PRES:
        raise HTTPException(400, "Допустимы только PDF/PPTX")

    # Ограничение объёма (напр. 50 МБ)
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > 50 * 1024 * 1024:
        raise HTTPException(400, "Файл больше 50 МБ")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    fname = f"project_{project_id}_{kind}{ext}"
    path = os.path.join(settings.UPLOAD_DIR, fname)
    with open(path, "wb") as f:
        f.write(file.file.read())

    if kind == "doc":
        project.file_url = path
    elif kind == "presentation":
        project.presentation_url = path
    else:
        project.video_url = path
    db.commit()
    return {"ok": True, "path": path}
