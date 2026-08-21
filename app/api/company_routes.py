from fastapi import APIRouter, Query
from app.clients.company_api_client import sync_companies, update_company_contacts
from app.database.db import SessionDep
from fastapi import APIRouter
from app.schemas.company import (
    SCompanyListResponse,
    SCompanyMessageResponse,
    SCompanyStatusResponse,
    SCompanyResponse,
    SCompanyPageResponse,
)
from app.services.company_service import (
    update_company_finances,
    enrich_company_data,
    sync_and_enrich_companies,
    get_company_by_inn,
    get_all_companies,
)


router_companies  = APIRouter(
    prefix="/companies",
    tags=["Companies"]
)


@router_companies.get("", response_model=SCompanyPageResponse)
async def all_companies(
    session: SessionDep,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),

):
    """Эндпоинт получения списка компаний с рассчетом прибыли и выручки"""
    return await get_all_companies(session, limit, offset)


@router_companies.post("/create/{okved_code}", response_model=SCompanyMessageResponse)
async def create_companies(okved_code: str, session: SessionDep):
    """Получение компаний по оквед"""
    await sync_companies(okved_code, session)
    await session.commit()
    return {
        "status": "ok",
        "message": f"Синхронизация для ОКВЭД {okved_code} завершена",
    }


@router_companies.post("/{inn}/finance", response_model=SCompanyStatusResponse)
async def update_finance(inn: str, session: SessionDep):
    """Обогащение финансами по ИНН"""
    company = await get_company_by_inn(session, inn)
    await update_company_finances(session, company)
    await session.commit()
    return {"status": "ok"}


@router_companies.post("/{inn}/contacts", response_model=SCompanyStatusResponse)
async def update_contacts(inn: str, session: SessionDep):
    """Обогащение контактами по ИНН"""
    company = await get_company_by_inn(session, inn)
    await update_company_contacts(session, company)
    await session.commit()
    return {"status": "ok"}


@router_companies.get("/{inn}", response_model=SCompanyResponse)
async def get_company(inn: str, session: SessionDep):
    """Эндпоинт получения информации по компании по ИНН"""
    company = await get_company_by_inn(session, inn)
    return company


@router_companies.post("/{inn}/enrich", response_model=SCompanyStatusResponse)
async def enrich_company(inn: str, session: SessionDep):
    """Обогащения по инн контактами и финансами сразу"""
    company = await get_company_by_inn(session, inn)
    await enrich_company_data(session, company)
    await session.commit()
    return {"status": "ok"}


@router_companies.post("/sync/{okved_code}/", response_model=SCompanyMessageResponse)
async def sync_company(okved_code: str, session: SessionDep):
    """Обогащение по оквед"""
    await sync_and_enrich_companies(okved_code, session)
    await session.commit()
    return {
        "status": "ok",
        "message": f"Компании по ОКВЭД {okved_code} загружены и обогащены",
    }
