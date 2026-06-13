from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.clients.company_api_client import sync_companies
from app.database.db import get_db
from app.models.company import Company

app = FastAPI(
    title="LeadRadar API",
    description="Поиск и приоритизация B2B-лидов через API и AI",
    version="0.1.0",
)

@app.get("/companies")
def all_companies(db: Session = Depends(get_db)):
    companies = db.query(Company).all()
    return companies


@app.post("/create/{okved_code}")
def create_companies(okved_code: str,db: Session = Depends(get_db)):
    sync_companies(okved_code, db)
    return {"status": "ok", "message": f"Синхронизация для ОКВЭД {okved_code} завершена"}




