from fastapi import APIRouter
from typing import List
from app.schemas.project import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("/", response_model=List[ProjectResponse])
def get_projects():
    # Временная заглушка для списка проектов
    return []

@router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectCreate):
    # Временная заглушка для создания проекта
    return {
        "id": 1,
        "name": project.name,
        "description": project.description
    }