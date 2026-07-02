# Development Guide

## Project layout

```
medical-ai/
├── backend/            FastAPI app, SQLAlchemy models, Alembic migrations, tests
├── frontend/           React + TypeScript + Vite + Tailwind SPA
├── docs/               This documentation
├── docker/             (reserved for extra deployment configs)
├── scripts/            setup/run/test helper scripts
├── .github/            CI workflow + issue/PR templates
├── docker-compose.yml  Full local stack (backend + frontend)
└── .env.example        Copy to .env before running
```

## Backend conventions

- **Type hints everywhere.** Every function signature is typed.
- **No business logic in routers.** Routers call a service method and
  translate the result/exception to an HTTP response — nothing else.
- **Exceptions, not error dicts.** Raise `app.core.exceptions.AppException`
  subclasses; the global handler translates them to consistent JSON.
- **Repositories own queries.** If you're writing `db.query(...)` outside
  `app/repositories/`, it probably belongs in a repository method instead.
- **New ML capability?** Add it as its own module under `app/ml/`, wrap it
  in an `is_available` guard if it depends on an optional heavy package,
  and wire it into the relevant service — never call ML libraries directly
  from routers.

## Frontend conventions

- **Pages** (`src/pages`) fetch data and compose components; they hold
  page-level state only.
- **Components** (`src/components`) are presentational/reusable; avoid
  putting API calls directly inside them — pass data via props.
- **API calls** live in `src/api/*.ts`, one file per resource area.
- **Design tokens** (colors, fonts) are defined once in
  `tailwind.config.js` — reach for the named tokens (`teal`, `coral`,
  `sage`, `ink`, etc.) rather than hardcoding hex values in components.

## Adding a new lab parameter

1. Add its canonical name to `KNOWN_PARAMETERS` in
   `app/ml/regex_extractor.py`.
2. Add a default reference range to `DEFAULT_RANGES` in
   `app/services/reference_range_service.py`.
3. (Optional) Add a clinical importance weight to `PARAMETER_WEIGHTS` in
   `app/ml/health_score.py` if it should influence the health score more
   or less than the default weight of 1.0.
4. Add a unit test asserting it's extracted and flagged correctly.

## Adding a new API endpoint

1. Add/extend a Pydantic schema in `app/schemas/`.
2. Add the business logic to the relevant service (or a new one) in
   `app/services/`.
3. Add the route in `app/api/v1/endpoints/`, using `Depends(get_current_user)`
   for anything user-scoped.
4. Register the router in `app/api/v1/router.py` if it's a new file.
5. Add an integration test in `backend/tests/integration/`.
