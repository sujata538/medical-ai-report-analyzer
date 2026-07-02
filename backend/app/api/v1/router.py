"""Aggregates all v1 endpoint routers into a single APIRouter."""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, dashboard, reports, search, upload, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(upload.router)
api_router.include_router(reports.router)
api_router.include_router(dashboard.router)
api_router.include_router(search.router)
