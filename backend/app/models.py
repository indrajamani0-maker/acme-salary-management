from sqlalchemy import Boolean, Column, Date, DateTime, Index, Integer, Numeric, String, func
from .database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String(20), unique=True, nullable=False, index=True)
    full_name = Column(String(120), nullable=False, index=True)
    email = Column(String(180), unique=True, nullable=False, index=True)
    department = Column(String(80), nullable=False, index=True)
    country = Column(String(80), nullable=False, index=True)
    employment_status = Column(String(20), nullable=False, default="active", index=True)
    salary_amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, index=True)
    salary_effective_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_employee_country_department", "country", "department"),
    )
