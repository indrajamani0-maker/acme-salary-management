
import csv
import io
from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Employee
from .schemas import EmployeeCreate, EmployeeOut, EmployeePage, EmployeeUpdate


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ACME Salary Management API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "ACME Salary Management API",
    }


@app.get("/api/employees", response_model=EmployeePage)
def list_employees(
    search: str | None = None,
    country: str | None = None,
    department: str | None = None,
    status: str | None = Query(
        default=None,
        pattern="^(active|inactive)$",
    ),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Employee)

    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Employee.full_name.ilike(term),
                Employee.email.ilike(term),
                Employee.employee_code.ilike(term),
            )
        )

    if country:
        query = query.filter(Employee.country == country)

    if department:
        query = query.filter(Employee.department == department)

    if status:
        query = query.filter(Employee.employment_status == status)

    total = query.count()

    items = (
        query.order_by(Employee.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }


# CSV export must be registered before /{employee_id}.
@app.get("/api/employees/export.csv")
def export_employees(
    search: str | None = None,
    country: str | None = None,
    department: str | None = None,
    status: str | None = Query(
        default=None,
        pattern="^(active|inactive)$",
    ),
    db: Session = Depends(get_db),
):
    query = db.query(Employee)

    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Employee.full_name.ilike(term),
                Employee.email.ilike(term),
                Employee.employee_code.ilike(term),
            )
        )

    if country:
        query = query.filter(Employee.country == country)

    if department:
        query = query.filter(Employee.department == department)

    if status:
        query = query.filter(Employee.employment_status == status)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "employee_code",
        "full_name",
        "email",
        "department",
        "country",
        "status",
        "salary_amount",
        "currency",
        "salary_effective_date",
    ])

    for employee in query.order_by(Employee.id).yield_per(1000):
        writer.writerow([
            employee.employee_code,
            employee.full_name,
            employee.email,
            employee.department,
            employee.country,
            employee.employment_status,
            str(employee.salary_amount),
            employee.currency,
            employee.salary_effective_date.isoformat(),
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="acme-employees.csv"'
        },
    )


@app.post(
    "/api/employees",
    response_model=EmployeeOut,
    status_code=201,
)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
):
    employee = Employee(**payload.model_dump())
    db.add(employee)

    try:
        db.commit()
        db.refresh(employee)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Employee code or email already exists",
        )

    return employee


@app.get(
    "/api/employees/{employee_id}",
    response_model=EmployeeOut,
)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
):
    employee = db.get(Employee, employee_id)

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    return employee


@app.put(
    "/api/employees/{employee_id}",
    response_model=EmployeeOut,
)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
):
    employee = db.get(Employee, employee_id)

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    for key, value in payload.model_dump().items():
        setattr(employee, key, value)

    try:
        db.commit()
        db.refresh(employee)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Employee code or email already exists",
        )

    return employee


@app.delete(
    "/api/employees/{employee_id}",
    response_model=EmployeeOut,
)
def deactivate_employee(
    employee_id: int,
    db: Session = Depends(get_db),
):
    employee = db.get(Employee, employee_id)

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    employee.employment_status = "inactive"
    db.commit()
    db.refresh(employee)

    return employee


@app.get("/api/analytics")
def analytics(db: Session = Depends(get_db)):
    total = (
        db.query(func.count(Employee.id)).scalar() or 0
    )

    active = (
        db.query(func.count(Employee.id))
        .filter(Employee.employment_status == "active")
        .scalar()
        or 0
    )

    by_country = (
        db.query(
            Employee.country,
            Employee.currency,
            func.count(Employee.id),
            func.sum(Employee.salary_amount),
        )
        .group_by(Employee.country, Employee.currency)
        .order_by(Employee.country, Employee.currency)
        .all()
    )

    by_department = (
        db.query(
            Employee.department,
            Employee.currency,
            func.count(Employee.id),
            func.sum(Employee.salary_amount),
        )
        .group_by(Employee.department, Employee.currency)
        .order_by(Employee.department, Employee.currency)
        .all()
    )

    return {
        "total_employees": total,
        "active_employees": active,
        "inactive_employees": total - active,
        "by_country": [
            {
                "country": country,
                "currency": currency,
                "employee_count": count,
                "salary_total": str(
                    salary_total or Decimal("0.00")
                ),
            }
            for country, currency, count, salary_total in by_country
        ],
        "by_department": [
            {
                "department": department,
                "currency": currency,
                "employee_count": count,
                "salary_total": str(
                    salary_total or Decimal("0.00")
                ),
            }
            for department, currency, count, salary_total in by_department
        ],
        "note": (
            "Salary totals are grouped by currency; "
            "different currencies are never added together."
        ),
    }
