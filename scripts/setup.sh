#!/usr/bin/env bash
# One-time project setup: backend venv + deps, frontend deps, .env file.
set -e

echo "== Setting up backend =="
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..

echo "== Setting up frontend =="
cd frontend
npm install
cd ..

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example — edit it before running in production."
fi

echo "Setup complete. Run ./scripts/run_backend.sh and ./scripts/run_frontend.sh in separate terminals."
