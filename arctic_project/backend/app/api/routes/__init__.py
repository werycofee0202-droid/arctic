from fastapi import APIRouter

from app.api.routes import (
    auth, users, projects, tests, news, reviews, certificates, analytics,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(projects.router)
api_router.include_router(tests.router)
api_router.include_router(news.router)
api_router.include_router(reviews.router)
api_router.include_router(certificates.router)
api_router.include_router(analytics.router)