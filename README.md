# ACME Salary Management

A starter full-stack employee salary management app for an HR Manager.

## Requirements
- Python 3.12+
- Node.js LTS and npm
- Git

## Run the backend (Windows PowerShell)
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

## Run the frontend
Open a second terminal:
```powershell
cd frontend
npm install
npm run dev
```
Open the URL printed by Vite, normally http://localhost:5173.

## Run backend tests
From the project root:
```powershell
cd backend
python -m pytest -q
```

## Run frontend tests and production build
```powershell
cd frontend
npm test
npm run build
```

## Seed data
`python seed.py` creates 10,000 deterministic synthetic employees if the database has fewer than 10,000 records. Existing records are not duplicated by repeated seed runs.

## API endpoints
See `docs/architecture.md` or visit `/docs` while the backend is running.

## Security and deployment note
This is an assessment/demo starter, not a production-ready payroll system. Before real use, add authentication, role-based access, audit logging, secrets management, backups, and a production database. SQLite storage on many free hosting platforms may be ephemeral; choose persistent storage or managed PostgreSQL before deploying.

## Suggested Git commits
1. `docs: add requirements and architecture`
2. `feat: add employee database model and API`
3. `feat: seed 10000 synthetic employees`
4. `feat: build HR salary dashboard`
5. `test: cover employee API behavior`
6. `docs: add run and deployment guidance`
