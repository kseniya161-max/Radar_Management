from app.database.session import SessionLocal
from app.services.company_service import get_companies

db = SessionLocal()

try:
    companies = get_companies(db)

    for company in companies:
        print(
            company.id,
            company.inn,
            company.name,
            company.status,
            company.okved,
        )
finally:
    db.close()
