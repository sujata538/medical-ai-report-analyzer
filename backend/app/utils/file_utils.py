"""File handling utilities: safe storage of uploads."""
from __future__ import annotations

import os
import uuid
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import UnsupportedFileTypeException, ValidationException


def ensure_upload_dir() -> None:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


def validate_upload(filename: str, size_bytes: int) -> str:
    """Validate extension + size; returns the (lowercased) file extension."""
    suffix = Path(filename).suffix.lower()
    if suffix not in settings.ALLOWED_EXTENSIONS:
        raise UnsupportedFileTypeException(
            f"'{suffix}' is not supported. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        raise ValidationException(f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB size limit.")
    return suffix


def generate_storage_path(original_filename: str) -> str:
    ensure_upload_dir()
    suffix = Path(original_filename).suffix.lower()
    unique_name = f"{uuid.uuid4()}{suffix}"
    return os.path.join(settings.UPLOAD_DIR, unique_name)


def save_upload_bytes(data: bytes, storage_path: str) -> None:
    with open(storage_path, "wb") as f:
        f.write(data)
