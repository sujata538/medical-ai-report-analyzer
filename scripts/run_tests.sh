#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../backend"
source venv/bin/activate 2>/dev/null || true
pytest --cov=app --cov-report=term-missing
