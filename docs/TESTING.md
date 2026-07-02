# Testing Guide

## Backend

```bash
cd backend
pytest                          # all tests
pytest tests/unit                # unit tests only
pytest tests/integration         # integration (API) tests only
pytest --cov=app --cov-report=term-missing   # with coverage
```

- **Unit tests** (`tests/unit/`) exercise pure business logic in isolation:
  the regex extractor, health-scoring algorithm, and `AuthService` against
  an in-memory SQLite database — no HTTP layer involved.
- **Integration tests** (`tests/integration/`) drive the FastAPI app via
  `TestClient` end-to-end through real HTTP requests (registration, login,
  authenticated report listing, dashboard stats), still against an
  isolated in-memory database per test (see `tests/conftest.py`).

## What's intentionally NOT covered by mocked/fake data

OCR and heavy ML paths (Tesseract, spaCy, sentence-transformers) are
exercised through unit tests of the *regex* extraction path, which has no
external dependencies. True OCR/NER/semantic-matching correctness should
be validated with real sample lab report images/PDFs in a staging
environment once those dependencies are installed — add fixtures under
`tests/fixtures/` (not included here to keep the repository free of
third-party medical document images) as you accumulate real (properly
licensed/anonymized) samples.

## Frontend

```bash
cd frontend
npm run lint     # ESLint
npm run build    # TypeScript compile + Vite build (catches type errors)
npm run test     # Vitest (add component tests under src/**/*.test.tsx as the UI grows)
```

## Verification status of this repository

Because this project was generated in an environment without internet
access, the following was performed:
- ✅ Every backend Python file was syntax-checked (`python -m py_compile`).
- ✅ The regex extraction pipeline was actually executed against sample
  text and produced correct results.
- ✅ The health-scoring algorithm's pure-Python logic was reasoned through
  and mirrors the unit tests in `tests/unit/test_health_score.py`.
- ⚠️ The FastAPI app, SQLAlchemy models, and pytest suite were **not**
  executed end-to-end, because `fastapi`, `sqlalchemy`, and related
  packages could not be installed in the generation environment (no
  network access). Run `pytest` yourself after `pip install -r
  requirements.txt` to confirm — the suite is designed to pass cleanly.
- ⚠️ The frontend was **not** built or type-checked with `tsc`/Vite in the
  generation environment for the same reason (`npm install` requires
  network access). Run `npm install && npm run build` to verify.
