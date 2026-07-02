# Deployment Guide

## Local development (no Docker)

```bash
./scripts/setup.sh          # one-time: creates venv, installs deps, copies .env
./scripts/run_backend.sh    # terminal 1 — http://localhost:8000
./scripts/run_frontend.sh   # terminal 2 — http://localhost:5173
```

## Docker Compose (recommended for a full local stack)

```bash
cp .env.example .env        # edit SECRET_KEY at minimum
docker compose up --build
```
- Backend: http://localhost:8000 (docs at `/api/docs`)
- Frontend: http://localhost:3000

## Production considerations

1. **Database**: switch `DATABASE_URL` to PostgreSQL and run
   `alembic upgrade head` instead of relying on `create_all()` at startup.
2. **Secrets**: set a strong, random `SECRET_KEY`; never commit `.env`.
3. **CORS**: restrict `CORS_ORIGINS` to your real frontend domain(s).
4. **File storage**: for multi-instance deployments, point `UPLOAD_DIR` at
   shared/object storage (e.g. S3) rather than local disk.
5. **Background processing**: the analysis pipeline currently runs via
   FastAPI's `BackgroundTasks`. For higher throughput, move
   `ReportService.process_report` to a task queue (Celery/RQ + Redis).
6. **ML dependencies**: `ENABLE_TRANSFORMER_MODELS=True` requires spaCy,
   sentence-transformers, and their downloaded models — see README
   "Enabling full ML features" for exact commands. These add real memory
   and cold-start cost; evaluate before enabling in production.
7. **HTTPS/reverse proxy**: put both services behind Nginx or a managed
   load balancer with TLS termination in real deployments.
8. **Monitoring**: `app/core/logging_config.py` writes rotating file logs;
   ship these to your logging backend of choice (e.g. via a sidecar).

## CI/CD

`.github/workflows/ci.yml` runs backend tests (pytest) and a frontend
build/lint on every push and pull request to `main`. Extend this workflow
with a deploy job once you have a target environment (e.g. push a built
Docker image to a registry).
