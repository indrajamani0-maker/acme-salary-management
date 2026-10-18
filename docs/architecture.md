# Architecture

```text
React + Vite (browser)
       |
       | HTTP / JSON
       v
FastAPI REST API
       |
       | SQLAlchemy ORM
       v
SQLite database (salary.db)
```

- `GET /api/health`: liveness check.
- `GET /api/employees`: search, filters, pagination.
- `POST /api/employees`: create employee.
- `GET /api/employees/{id}`: fetch one employee.
- `PUT /api/employees/{id}`: update employee.
- `DELETE /api/employees/{id}`: soft-deactivate employee.
- `GET /api/analytics`: employee counts and salary totals grouped by currency.
- `GET /api/employees/export.csv`: export filtered data.

SQLite is suitable for a local assessment/demo. For production multi-user deployment, consider PostgreSQL, authentication/authorization, audit logging, backups, and secret management.
