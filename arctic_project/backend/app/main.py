from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import api_router
from app.core.config import settings
from app.core.database import Base, engine

# Для Alembic таблицы лучше создавать через миграции,
# но для быстрого старта можно раскомментировать:
# from app import models  # noqa
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

# Раздача загруженных файлов
import os
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CERTIFICATE_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.mount("/certificates", StaticFiles(directory=settings.CERTIFICATE_DIR), name="certificates")


@app.get("/")
def root():
    return {"name": settings.PROJECT_NAME, "status": "ok"}