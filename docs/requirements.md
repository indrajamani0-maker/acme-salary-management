# ACME Salary Management — Requirements

## Goal
Help an HR Manager manage salary information across countries and replace manual spreadsheet workflows. Support 10,000 synthetic employee records.

## In scope
- Create, read, update, and deactivate employee records.
- Store employee code, name, email, department, country, status, salary amount, currency, and effective date.
- Search by code, name, and email; filter by country, department, and status.
- Database pagination, dashboard metrics, grouped compensation analytics, and CSV export.
- Seed 10,000 synthetic records and automate tests for core API behavior.

## Technical approach
- React + Vite frontend.
- Python + FastAPI backend.
- SQLite relational database and SQLAlchemy ORM.
- pytest + FastAPI TestClient; Vitest + React Testing Library.
- Git commits by working feature; deploy frontend and backend separately if required.

## Out of scope
Payroll processing, bank integration, tax calculations, live FX rates, and enterprise SSO.

## Key decisions
- Use decimal-compatible numeric storage for salaries.
- Never sum amounts from different currencies together.
- Use server-side pagination and indexed columns.
- Use synthetic data only.

## Acceptance criteria
The app starts locally, supports employee CRUD/search/filtering, seeds 10,000 records, shows currency-separated analytics, exports CSV, passes tests, and includes architecture/trade-off notes, setup instructions, incremental commits, and a demo.
