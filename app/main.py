from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.clients.company_api_client import sync_companies, update_company_contacts
from app.database.db import get_db
from app.models.company import Company
from app.services.company_service import update_company_finances

app = FastAPI(
    title="KSENIA TEST 777",
    description="KSENIA TEST 777",
    version="0.1.0",
)


@app.get("/companies")
def all_companies(db: Session = Depends(get_db)):
    companies = db.query(Company).all()
    return companies


@app.post("/create/{okved_code}")
def create_companies(okved_code: str,db: Session = Depends(get_db)):
    sync_companies(okved_code, db)
    db.commit()
    return {"status": "ok", "message": f"Синхронизация для ОКВЭД {okved_code} завершена"}


@app.post("/companies/{inn}/finance")
def update_finance(inn:str, db: Session = Depends(get_db)):
    update_company_finances(db, inn)
    return {"status": "ok", inn: inn}


@app.post("/companies/{inn}/contacts")
def update_contacts(inn:str, db: Session = Depends(get_db)):
    update_company_contacts(db, inn)
    return {"status": "ok", inn: inn}


@app.get("/companies/{inn}")
def get_company(inn: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.inn == inn).first()

    if not company:
        return {"error": "Company not found"}

    return company






