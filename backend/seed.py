
import random
from datetime import date, timedelta
from decimal import Decimal
from app.database import Base, SessionLocal, engine
from app.models import Employee

FIRST_NAMES = ["Aarav", "Aisha", "Amara", "Arjun", "Daniel", "Fatima", "Grace", "Ibrahim", "Isha", "Jacob", "Kavya", "Liam", "Maya", "Noah", "Olivia", "Priya", "Rohan", "Sara", "Thomas", "Zara"]
LAST_NAMES = ["Anderson", "Brown", "Chen", "Das", "Fernandes", "Gupta", "Joseph", "Khan", "Kumar", "Lee", "Mathew", "Menon", "Nair", "Patel", "Rao", "Sharma", "Singh", "Thomas", "Wilson", "Zhang"]
DEPARTMENTS = ["Engineering", "Finance", "Human Resources", "Marketing", "Operations", "Sales", "Support", "Data"]
COUNTRIES = [("India", "INR"), ("United States", "USD"), ("United Kingdom", "GBP"), ("Germany", "EUR"), ("Canada", "CAD"), ("Australia", "AUD")]

def seed(count: int = 10_000):
    random.seed(42)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(Employee).count()
        if existing >= count:
            print(f"Database already has {existing} employees; no records added.")
            return
        records = []
        start = date(2020, 1, 1)
        for number in range(existing + 1, count + 1):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            country, currency = random.choice(COUNTRIES)
            salary = Decimal(random.randrange(2500, 18001) * 100) / Decimal(100)
            records.append(Employee(
                employee_code=f"ACME{number:05d}",
                full_name=f"{first} {last}",
                email=f"employee{number:05d}@example.com",
                department=random.choice(DEPARTMENTS),
                country=country,
                employment_status="active" if random.random() > 0.08 else "inactive",
                salary_amount=salary,
                currency=currency,
                salary_effective_date=start + timedelta(days=random.randrange(0, 2200)),
            ))
            if len(records) >= 500:
                db.bulk_save_objects(records)
                db.commit()
                records = []
        if records:
            db.bulk_save_objects(records)
            db.commit()
        print(f"Seed complete. Database now contains {db.query(Employee).count()} employees.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
