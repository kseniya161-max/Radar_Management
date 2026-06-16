from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.clients.company_api_client import sync_companies, update_company_contacts
from app.database.db import get_db
from app.models.company import Company
from app.services.company_service import update_company_finances, enrich_company_data, growth_calc

app = FastAPI(
    title="KSENIA TEST 998",
    description="KSENIA TEST 777",
    version="0.1.0",
)

@app.get("/ping")
def ping():
    return {"status": "ok", "message": "pong"}

@app.get("/companies")
def all_companies(db: Session = Depends(get_db)):
    companies = db.query(Company).all()
    result = []
    for c in companies:
        growth_profit = growth_calc(c.profit_2025, c.profit_2024)
        growth_revenue = growth_calc(c.revenue_2025, c.revenue_2024)
        result.append({
            "id": c.id,
            "inn": c.inn,
            "name": c.name,
            "status": c.status,
            "okved": c.okved,
            "revenue_2025": c.revenue_2025,
            "revenue_2024": c.revenue_2024,
            "revenue_2023": c.revenue_2023,
            "profit_2025": c.profit_2025,
            "profit_2024": c.profit_2024,
            "profit_2023": c.profit_2023,
            "revenue_growth": growth_revenue,
            "profit_growth": growth_profit,
            "phone": c.phone,
            "email": c.email,
            "website": c.website,
            "region": c.region,
            "registration_date": c.registration_date,
            "tenders_count": c.tenders_count,
            "courts_count": c.courts_count,
        })
    return result





@app.post("/create/{okved_code}")
def create_companies(okved_code: str,db: Session = Depends(get_db)):
    sync_companies(okved_code, db)
    db.commit()
    return {"status": "ok", "message": f"Синхронизация для ОКВЭД {okved_code} завершена"}


@app.post("/companies/{inn}/finance")
def update_finance(inn:str, db: Session = Depends(get_db)):
    update_company_finances(db, inn)
    db.commit()
    return {"status": "ok", inn: inn}


@app.post("/companies/{inn}/contacts")
def update_contacts(inn:str, db: Session = Depends(get_db)):
    update_company_contacts(db, inn)
    db.commit()
    return {"status": "ok", inn: inn}


@app.get("/companies/{inn}")
def get_company(inn: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.inn == inn).first()

    if not company:
        return {"error": "Company not found"}

    return company


@app.post("/companies/{inn}/enrich")
def enrich_company(
        inn: str,
        db: Session = Depends(get_db)
):
    enrich_company_data(db, inn)
    db.commit()
    return {"status": "ok", inn: inn}


@app.post("/sync/{okved_code}/")
def sync_company(okved_code: str, limit: int = 10, db: Session = Depends(get_db)):
    sync_companies(okved_code, db)
    db.commit()

    companies = db.query(Company).filter(Company.okved == okved_code).limit(limit).all()
    if not companies:
        return {"status": "error", "message": f"Нет компаний с ОКВЭД {okved_code}"}

    for company in companies:
        try:
            enrich_company_data(db, company.inn)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Ошибка для {company.inn}: {e}")
            continue
    return {
        "status": "ok",
        "message": f"Обработано {len(companies)} компаний по ОКВЭД {okved_code}",
        "processed_count": len(companies),
        "okved": okved_code
    }











