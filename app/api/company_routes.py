from fastapi import Depends
from sqlalchemy.orm import Session, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.company_api_client import sync_companies, update_company_contacts
from app.database.db import get_db
from fastapi import APIRouter
from app.schemas.company import (
    SCompanyListResponse,
    SCompanyMessageResponse,
    SCompanyStatusResponse,
    SCompanyResponse, SCompanyPageResponse,
)
from app.services.company_service import (
    update_company_finances,
    enrich_company_data,
    sync_and_enrich_companies,
    get_company_by_inn,
    get_all_companies,
)

router = APIRouter(tags=["Companies"])


@router.get("/companies", response_model=SCompanyPageResponse)
async def all_companies(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Эндпоинт получения списка компаний с рассчетом прибыли и выручки"""
    return await get_all_companies(db, limit, offset)


@router.post("/create/{okved_code}", response_model=SCompanyMessageResponse)
async def create_companies(okved_code: str, db: AsyncSession = Depends(get_db)):
    """Получение компаний по оквед"""
    await sync_companies(okved_code, db)
    await db.commit()
    return {
        "status": "ok",
        "message": f"Синхронизация для ОКВЭД {okved_code} завершена",
    }


@router.post("/companies/{inn}/finance", response_model=SCompanyStatusResponse)
async def update_finance(inn: str, db: AsyncSession = Depends(get_db)):
    """Обогащение финансами по ИНН"""
    company = await get_company_by_inn(db, inn)
    await update_company_finances(db, company)
    await db.commit()
    return {"status": "ok"}


@router.post("/companies/{inn}/contacts", response_model=SCompanyStatusResponse)
async def update_contacts(inn: str, db: AsyncSession = Depends(get_db)):
    """Обогащение контактами по ИНН"""
    company = await get_company_by_inn(db, inn)
    await update_company_contacts(db, company)
    await db.commit()
    return {"status": "ok"}


@router.get("/companies/{inn}", response_model=SCompanyResponse)
async def get_company(inn: str, db: AsyncSession = Depends(get_db)):
    """Эндпоинт получения информации по компании по ИНН"""
    company = await get_company_by_inn(db, inn)
    return company


@router.post("/companies/{inn}/enrich", response_model=SCompanyStatusResponse)
def enrich_company(inn: str, db: Session = Depends(get_db)):
    """Обогащения по инн"""
    company = get_company_by_inn(db, inn)
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
