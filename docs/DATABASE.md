# Database Schema

SQLite by default (see `DATABASE_URL` in `.env`); swap to PostgreSQL by
changing the connection string — SQLAlchemy handles the rest, though you
should regenerate migrations if you rely on SQLite-specific types.

## Entity-relationship overview

```
roles (1) ───< users (1) ───< reports (1) ───< uploaded_files
                    │                │
                    │                ├──< extracted_parameters >── reference_ranges
                    │                └──< recommendations
                    │
                    ├──< user_sessions
                    └──< audit_logs
```

## Tables

### `roles`
| column | type | notes |
|---|---|---|
| id | int PK | |
| name | string(50) unique | admin / patient / clinician |
| description | string(255) | |

### `users`
| column | type | notes |
|---|---|---|
| id | uuid PK | |
| email | string unique, indexed | |
| full_name | string | |
| hashed_password | string | bcrypt |
| is_active / is_verified | bool | |
| role_id | FK → roles.id | |
| date_of_birth, gender | nullable | |
| created_at, updated_at | datetime | |

### `reports`
| column | type | notes |
|---|---|---|
| id | uuid PK | |
| owner_id | FK → users.id | |
| title | string | |
| status | enum | uploaded / processing / extracted / analyzed / failed |
| raw_extracted_text | text | full OCR/PDF text |
| ai_summary | text | |
| health_score | float, nullable | 0–100 |
| risk_category | string | excellent / good / moderate / elevated / high |

### `uploaded_files`
Stores original filename, storage path on disk, content type, size — one
report can (in the schema) have multiple files, though the current upload
flow creates one per report.

### `reference_ranges`
Seeded on startup (`seed_reference_ranges`) with common adult lab ranges:
parameter name, unit, low/high, critical_low/critical_high, optional
sex/age segmentation columns for future refinement.

### `extracted_parameters`
One row per lab value found in a report: name, raw matched text, numeric
value, unit, computed `flag` (low/normal/high/critical_*), `confidence`
(0.0–1.0, reflecting whether it was matched by the high-confidence
vocabulary regex, a generic regex, or NER/semantic recovery), and a FK to
the matched `reference_ranges` row (nullable — `unknown` flag if no match).

### `recommendations`
Per-report cautious recommendation messages, each tagged with a severity
(`info` / `advisory` / `important`) and optionally linked to the parameter
that triggered it. The general disclaimer is always appended as an `info`
row.

### `user_sessions`
One row per issued refresh token, enabling per-device session listing and
revocation ("log out of all devices" = mark all as `is_revoked`).

### `audit_logs`
Append-only security/action trail (login, upload, deletion, password
change) for compliance and debugging. Not currently written to on every
action in this build — service methods are the natural place to add
`AuditLog` inserts as the feature set grows.

## Migrations

Managed with Alembic (`backend/alembic/`). The initial migration
(`0001_initial.py`) creates every table above. To generate a new migration
after modifying a model:

```bash
cd backend
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```
