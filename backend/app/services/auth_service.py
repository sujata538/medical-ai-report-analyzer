"""
Authentication service.

Encapsulates all business logic for registration, login, token refresh and
logout. Depends only on the UserRepository (repository pattern) and the
security utilities, so it has no knowledge of HTTP/FastAPI concerns.
"""
from datetime import datetime, timedelta, timezone
import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.models.user_session import UserSession
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def register(self, payload: UserCreate) -> User:
        if self.users.email_exists(payload.email):
            raise ConflictException("An account with this email already exists.")

        user = User(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
        )
        self.users.create(user)
        logger.info("New user registered: %s", user.email)
        return user

    def authenticate(self, email: str, password: str) -> User:
        user = self.users.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Incorrect email or password.")
        if not user.is_active:
            raise UnauthorizedException("This account has been deactivated.")
        return user

    def issue_tokens(self, user: User, user_agent: str | None = None, ip: str | None = None) -> Token:
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        session = UserSession(
            user_id=user.id,
            refresh_token=refresh_token,
            user_agent=user_agent,
            ip_address=ip,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.db.add(session)
        self.db.commit()

        return Token(access_token=access_token, refresh_token=refresh_token)

    def refresh_access_token(self, refresh_token: str) -> Token:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid or expired refresh token.")

        session = (
            self.db.query(UserSession)
            .filter(UserSession.refresh_token == refresh_token, UserSession.is_revoked.is_(False))
            .first()
        )
        if not session:
            raise UnauthorizedException("Session has been revoked or does not exist.")

        user_id = payload["sub"]
        new_access_token = create_access_token(user_id)
        return Token(access_token=new_access_token, refresh_token=refresh_token)

    def logout(self, refresh_token: str) -> None:
        session = self.db.query(UserSession).filter(UserSession.refresh_token == refresh_token).first()
        if session:
            session.is_revoked = True
            self.db.commit()

    def get_current_user(self, token: str) -> User:
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            raise UnauthorizedException("Invalid or expired access token.")

        user = self.users.get(payload["sub"])
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive.")
        return user
