"""Unit tests for AuthService (registration, login, token issuance)."""
import pytest

from app.core.exceptions import ConflictException, UnauthorizedException
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService


def test_register_creates_user(db_session):
    service = AuthService(db_session)
    user = service.register(UserCreate(email="jane@example.com", full_name="Jane Doe", password="Password123"))
    assert user.id is not None
    assert user.email == "jane@example.com"


def test_register_duplicate_email_raises(db_session):
    service = AuthService(db_session)
    payload = UserCreate(email="dupe@example.com", full_name="Dupe", password="Password123")
    service.register(payload)
    with pytest.raises(ConflictException):
        service.register(payload)


def test_authenticate_success(db_session):
    service = AuthService(db_session)
    service.register(UserCreate(email="ok@example.com", full_name="OK User", password="Password123"))
    user = service.authenticate("ok@example.com", "Password123")
    assert user.email == "ok@example.com"


def test_authenticate_wrong_password_raises(db_session):
    service = AuthService(db_session)
    service.register(UserCreate(email="wrong@example.com", full_name="Wrong", password="Password123"))
    with pytest.raises(UnauthorizedException):
        service.authenticate("wrong@example.com", "IncorrectPass1")


def test_issue_and_refresh_tokens(db_session):
    service = AuthService(db_session)
    user = service.register(UserCreate(email="tok@example.com", full_name="Tok", password="Password123"))
    tokens = service.issue_tokens(user)
    assert tokens.access_token
    assert tokens.refresh_token

    refreshed = service.refresh_access_token(tokens.refresh_token)
    assert refreshed.access_token
