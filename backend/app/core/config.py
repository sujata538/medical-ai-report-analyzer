"""
Centralized application configuration.

All environment-dependent values are declared here and loaded from a `.env`
file (see `.env.example` at the project root). Using pydantic-settings gives
us type validation, sane defaults for local development, and a single
source of truth that both the app and Alembic migrations can import.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- General ---
    APP_NAME: str = "AI Medical Report Analyzer"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # development | staging | production
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # --- Security / JWT ---
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_super_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./medical_ai.db"

    # --- CORS ---
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # --- File storage ---
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 15
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".png", ".jpg", ".jpeg", ".tiff"]

    # --- OCR ---
    TESSERACT_CMD: str = "/usr/bin/tesseract"

    # --- ML / NLP ---
    ENABLE_TRANSFORMER_MODELS: bool = False  # set True once heavy deps are installed
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"
    SPACY_MODEL: str = "en_core_web_sm"

    # --- Logging ---
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"

    # --- Medical safety ---
    MEDICAL_DISCLAIMER: str = (
        "This application is intended only for educational and informational "
        "purposes and is NOT a substitute for professional medical advice, "
        "diagnosis, or treatment."
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (avoids re-parsing .env on every call)."""
    return Settings()


settings = get_settings()
