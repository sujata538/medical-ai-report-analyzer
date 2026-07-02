"""
FastAPI application entrypoint.

Wires together configuration, logging, exception handlers, CORS, database
initialization (dev convenience — use Alembic in production), and the
versioned API router.

Run locally with:
    uvicorn app.main:app --reload
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import configure_logging
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.services.reference_range_service import seed_reference_ranges

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "An AI-assisted medical lab report analyzer. "
        f"\n\n**Disclaimer:** {settings.MEDICAL_DISCLAIMER}"
    ),
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
def on_startup() -> None:
    """Create tables (dev convenience) and seed reference lookup data."""
    init_db()
    db = SessionLocal()
    try:
        seed_reference_ranges(db)
    finally:
        db.close()
    logger.info("%s v%s started in %s mode.", settings.APP_NAME, settings.APP_VERSION, settings.ENVIRONMENT)


@app.get("/", tags=["Health"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "ok",
        "disclaimer": settings.MEDICAL_DISCLAIMER,
    }


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
