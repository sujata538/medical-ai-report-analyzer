# Docker configs

Extra deployment-specific Docker configs can live here (e.g. a
production-hardened Nginx config, a Postgres-backed compose override).
The primary Dockerfiles live alongside their respective services:
`backend/Dockerfile` and `frontend/Dockerfile`. The root `docker-compose.yml`
wires them together for local development.
