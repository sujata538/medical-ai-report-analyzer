# Architecture

## Overview

MedInsight follows a classic **layered / clean architecture** on the backend and a
component-based SPA on the frontend, connected over a versioned REST API.

```
┌─────────────┐      HTTPS/JSON       ┌──────────────────────────────┐
│   React SPA │  ───────────────────▶ │           FastAPI            │
│  (Vite/TS)  │  ◀───────────────────  │                              │
└─────────────┘                       │  ┌────────────────────────┐  │
                                       │  │   API layer (routers)  │  │
                                       │  └───────────┬────────────┘  │
                                       │  ┌───────────▼────────────┐  │
                                       │  │   Service layer        │  │
                                       │  │  (business logic, DTOs)│  │
                                       │  └───────────┬────────────┘  │
                                       │  ┌───────────▼────────────┐  │
                                       │  │  Repository layer      │  │
                                       │  │  (SQLAlchemy queries)  │  │
                                       │  └───────────┬────────────┘  │
                                       │  ┌───────────▼────────────┐  │
                                       │  │   SQLite / Postgres    │  │
                                       │  └────────────────────────┘  │
                                       │                              │
                                       │  ┌────────────────────────┐  │
                                       │  │  ML/NLP layer (app/ml)  │ │
                                       │  │  regex → NER → semantic│  │
                                       │  │  → scoring → recs      │  │
                                       │  └────────────────────────┘  │
                                       └──────────────────────────────┘
```

## Layers

- **API layer** (`app/api`): FastAPI routers. Only concerned with HTTP
  concerns — request parsing, status codes, auth dependency injection.
  Contains no business logic.
- **Service layer** (`app/services`): all business logic and orchestration.
  Services depend on repositories and ML modules, never on FastAPI types.
- **Repository layer** (`app/repositories`): the only place that writes
  SQLAlchemy queries. Enables swapping persistence (e.g. SQLite →
  PostgreSQL) without touching services.
- **ML/NLP layer** (`app/ml`): pure-Python modules with no FastAPI/DB
  dependency, so they can be unit tested and reused outside the web
  context entirely (e.g. in a notebook or CLI script).
- **Models** (`app/models`): SQLAlchemy ORM models — the source of truth
  for the DB schema, mirrored by Alembic migrations.
- **Schemas** (`app/schemas`): Pydantic DTOs — define the public API
  contract, decoupled from internal ORM models.

## Design patterns used

| Pattern | Where |
|---|---|
| Repository | `app/repositories/*` |
| Service layer | `app/services/*` |
| Dependency Injection | FastAPI `Depends()` throughout `app/api` |
| DTO | `app/schemas/*` |
| Strategy (extraction fallback) | `ExtractionService` chooses regex vs. NER vs. semantic recovery |
| Factory-ish construction | `get_auth_service`, `get_db` dependency providers |

## Processing pipeline (upload → analysis)

1. **Upload** (`/api/v1/upload`): file validated (type/size), stored to disk,
   a `Report` + `UploadedFile` row created with status `uploaded`.
2. **Background task** kicks off `ReportService.process_report()`:
   - **OCR** (`OCRService`): native PDF text extraction, falling back to
     Tesseract OCR (with OpenCV preprocessing) for scanned documents/images.
   - **Extraction** (`ExtractionService`): regex-based parameter extraction
     (always on), optionally augmented by spaCy NER + sentence-transformer
     semantic matching for non-standard phrasing.
   - **Reference range flagging** (`ReferenceRangeService`): each value is
     compared against seeded reference ranges to produce a `ParameterFlag`.
   - **Health scoring** (`HealthScoreService`): a transparent, weighted
     rule-based score (0–100) + risk category, with a breakdown per
     parameter for explainability.
   - **Recommendations** (`RecommendationEngine`): cautious, non-diagnostic
     message templates per abnormal parameter.
   - **AI summary** (`AIService`): deterministic template summary, with a
     documented (optional) extension point to rephrase via an LLM without
     ever adding new claims.
3. Report status becomes `analyzed` (or `failed` if any step raised).

## Why this pipeline is intentionally "regex-first"

The regex extractor requires zero ML dependencies and correctly handles
the large majority of real-world lab report layouts. The NER/semantic
layers are additive — they only run to *recover* parameters the regex
missed, and the whole system degrades gracefully (with reduced recall,
never a crash) when the heavier ML dependencies aren't installed. See
`docs/ROADMAP.md` for the path to a trained predictive model.
