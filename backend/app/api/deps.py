"""
Shared FastAPI dependencies: DB session injection, current-user resolution
from the Authorization header, and role-based guards.
"""
from __future__ import annotations

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException
from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=True)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_current_user(
    token: str = Depends(oauth2_scheme), auth_service: AuthService = Depends(get_auth_service)
) -> User:
    return auth_service.get_current_user(token)


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.role or user.role.name != "admin":
        raise ForbiddenException("Administrator privileges are required for this action.")
    return user
