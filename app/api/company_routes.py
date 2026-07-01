from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.clients.company_api_client import sync_companies, update_company_contacts
from app.database.db import get_db
from fastapi import APIRouter
from app.models.company import Company
from app.schemas.company import SCompanyListResponse, SCompanyMessageResponse, SCompanyStatusResponse, SCompanyResponse
from app.services.company_service import growth_calc, update_company_finances, enrich_company_data, \
    sync_and_enrich_companies, get_company_by_inn

router = APIRouter(
    tags=["Companies"]
)

@router.get("/companies", response_model=list[SCompanyListResponse])
def all_companies(db: Session = Depends(get_db)):
    """Эндпоинт получения списка компаний с рассчетом прибыли и выручки"""
    companies = db.query(Company).all()
    result = []
    for c in companies:
        growth_profit = growth_calc(c.profit_2025, c.profit_2024)
        growth_revenue = growth_calc(c.revenue_2025, c.revenue_2024)
        result.append(
            {
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
            }
        )
    return result


@router.post("/create/{okved_code}", response_model=SCompanyMessageResponse)
def create_companies(okved_code: str, db: Session = Depends(get_db)):
    """Получение компаний по оквед"""
    sync_companies(okved_code, db)
    db.commit()
    return {
        "status": "ok",
        "message": f"Синхронизация для ОКВЭД {okved_code} завершена",
    }


@router.post("/companies/{inn}/finance", response_model=SCompanyStatusResponse)
def update_finance(inn: str, db: Session = Depends(get_db)):
    """Обогащение финансами по ИНН"""
    company = db.scalar(select(Company).where(Company.inn == inn))
    if not company:
        raise HTTPException(
            status_code=404,
            detail='Company not found',
        )
    update_company_finances(db, company)
    db.commit()
    return {"status": "ok"}


@router.post("/companies/{inn}/contacts", response_model=SCompanyStatusResponse)
def update_contacts(inn: str, db: Session = Depends(get_db)):
    """Обогащение контактами по ИНН"""
    company = get_company_by_inn(db, inn)
    update_company_contacts(db, company)
    db.commit()
    return {"status": "ok"}


@router.get("/companies/{inn}", response_model=SCompanyResponse)
def get_company(inn: str, db: Session = Depends(get_db)):
    """Эндпоинт получения информации по компании по ИНН"""
    company = db.query(Company).filter(Company.inn == inn).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail='Company not found'
        )
    return company


@router.post("/companies/{inn}/enrich", response_model=SCompanyStatusResponse)
def enrich_company(inn: str, db: Session = Depends(get_db)):
    """Обогащения по инн"""
    company = db.scalar(select(Company).where(Company.inn == inn))
    if not company:
        raise HTTPException(
            status_code=404,
            detail='Company not found',
        )
    enrich_company_data(db, company)
    db.commit()
    return {"status": "ok"}


@router.post("/sync/{okved_code}/", response_model=SCompanyMessageResponse)
def sync_company(okved_code: str, db: Session = Depends(get_db)):
    """Обогащение по оквед"""
    sync_and_enrich_companies(okved_code, db)
    db.commit()
    return {
        "status": "ok",
        "message": f"Компании по ОКВЭД {okved_code} загружены и обогащены",
    }