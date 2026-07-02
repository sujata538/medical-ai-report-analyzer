# MedInsight — AI Medical Report Analyzer

An AI-assisted web application that turns uploaded lab/pathology reports
(scanned or digital PDFs, or images) into structured, plain-language
insights: extracted parameters, reference-range comparisons, a
transparent health score, cautious recommendations, and historical
tracking.

> **Disclaimer:** This application is intended only for educational and
> informational purposes and is **NOT** a substitute for professional
> medical advice, diagnosis, or treatment.

## Features

- 🔐 JWT authentication (register, login, refresh, logout, password change)
- 📄 Upload PDFs or images (drag & drop)
- 🔍 OCR pipeline: native PDF text extraction with Tesseract OCR fallback
  for scanned documents, OpenCV-based image preprocessing
- 🧠 Medical NLP: regex-based extraction (zero-dependency baseline),
  optional spaCy NER and sentence-transformer semantic matching for
  non-standard phrasing
- 📊 Reference-range comparison and parameter flagging (low/normal/high/critical)
- 💯 Transparent, weighted health-score algorithm (0–100) with a
  per-parameter explainability breakdown
- 💡 Cautious, non-diagnostic recommendations
- 📈 Dashboard with trend charts across report history
- 🔎 Search across reports and parameters
- 📥 PDF export of any analyzed report
- 🌓 Dark mode, responsive UI, accessible components
- 🧪 Unit + integration test suite (pytest)
- 🐳 Docker Compose for one-command local stack

## Tech stack

**Backend:** Python, FastAPI, SQLAlchemy, Alembic, SQLite, Pydantic, JWT, bcrypt
**Frontend:** React, TypeScript, Vite, Tailwind CSS, React Router, Chart.js
**OCR:** Tesseract, PyMuPDF, pdfplumber, OpenCV, Pillow
**ML/NLP:** scikit-learn, spaCy, Sentence Transformers, SHAP (optional, see below)

## Quick start

### Option A: Docker Compose (fastest)

```bash
git clone <this-repo>
cd medical-ai
cp .env.example .env      # edit SECRET_KEY before any real use
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/api/docs

### Option B: Local (no Docker)

Requires Python 3.11+, Node 20+, and `tesseract-ocr` installed on your system.

```bash
./scripts/setup.sh          # creates venv, installs backend + frontend deps
./scripts/run_backend.sh    # terminal 1
./scripts/run_frontend.sh   # terminal 2
```

Then open http://localhost:5173.

## Enabling full ML features

By default `ENABLE_TRANSFORMER_MODELS=False` in `.env` — the app runs
entirely on the zero-dependency regex extraction pipeline, which handles
the majority of standard lab report layouts. To enable spaCy NER and
sentence-transformer semantic matching for messier/non-standard reports:

```bash
pip install spacy sentence-transformers transformers torch shap scikit-learn
python -m spacy download en_core_web_sm
# then set ENABLE_TRANSFORMER_MODELS=True in .env
```

These downloads require internet access and add noticeable memory/startup
cost — evaluate before enabling in a resource-constrained deployment.

## Project structure

See [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) for a full breakdown.

```
medical-ai/
├── backend/     FastAPI app (see backend/README below via docs/)
├── frontend/    React + TypeScript SPA
├── docs/        Architecture, API, database, deployment, testing docs
├── docker/      Reserved for extra deployment configs
├── scripts/     setup / run / test helper scripts
└── .github/     CI workflow, issue & PR templates
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Database Schema](docs/DATABASE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Testing Guide](docs/TESTING.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [Roadmap: Future ML Architecture](docs/ROADMAP.md)

## Verification status

This project was built in an offline sandbox. Every backend Python file
was syntax-validated and the core (dependency-free) regex extraction and
health-scoring logic was actually executed and confirmed correct. The
full FastAPI/pytest suite and the frontend build were **not** executed
end-to-end because `pip install` / `npm install` require network access
not available during generation. See [`docs/TESTING.md`](docs/TESTING.md)
for the exact verification breakdown and how to run everything yourself.

## Safety principle

This system is designed, by construction, to **never diagnose**. Every
generated message is templated with cautious language, every report
carries the disclaimer above, and the roadmap for future ML work
(`docs/ROADMAP.md`) explicitly preserves this boundary.

## License

MIT — see [LICENSE](LICENSE).
