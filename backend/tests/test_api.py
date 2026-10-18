from datetime import date
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app
from app.models import Employee

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def setup_function():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

def sample_employee(code="ACME00001", email="test@example.com"):
    return {
        "employee_code": code,
        "full_name": "Test Employee",
        "email": email,
        "department": "Engineering",
        "country": "India",
        "employment_status": "active",
        "salary_amount": "75000.00",
        "currency": "INR",
        "salary_effective_date": date.today().isoformat(),
    }

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_and_get_employee():
    response = client.post("/api/employees", json=sample_employee())
    assert response.status_code == 201
    employee_id = response.json()["id"]
    fetched = client.get(f"/api/employees/{employee_id}")
    assert fetched.status_code == 200
    assert fetched.json()["employee_code"] == "ACME00001"

def test_duplicate_employee_code_is_rejected():
    client.post("/api/employees", json=sample_employee())
    response = client.post("/api/employees", json=sample_employee(email="other@example.com"))
    assert response.status_code == 409

def test_negative_salary_is_rejected():
    payload = sample_employee()
    payload["salary_amount"] = "-1"
    assert client.post("/api/employees", json=payload).status_code == 422

def test_list_search_and_pagination():
    client.post("/api/employees", json=sample_employee())
    client.post("/api/employees", json=sample_employee("ACME00002", "second@example.com"))
    response = client.get("/api/employees?search=second&page=1&page_size=1")
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert len(response.json()["items"]) == 1

def test_deactivate_employee():
    created = client.post("/api/employees", json=sample_employee()).json()
    response = client.delete(f"/api/employees/{created['id']}")
    assert response.status_code == 200
    assert response.json()["employment_status"] == "inactive"

def test_csv_export():
    client.post("/api/employees", json=sample_employee())
    response = client.get("/api/employees/export.csv")
    assert response.status_code == 200
    assert "employee_code" in response.text
    assert "ACME00001" in response.text

def test_analytics_keeps_currencies_separate():
    client.post("/api/employees", json=sample_employee())
    payload = sample_employee("ACME00002", "us@example.com")
    payload["country"] = "United States"
    payload["currency"] = "USD"
    payload["salary_amount"] = "1000.00"
    client.post("/api/employees", json=payload)
    response = client.get("/api/analytics")
    assert response.status_code == 200
    assert response.json()["total_employees"] == 2
    assert {row["currency"] for row in response.json()["by_country"]} == {"INR", "USD"}
