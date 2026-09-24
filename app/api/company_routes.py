from fastapi import Query
from app.clients.company_api_client import sync_companies, update_company_contacts
from app.database.db import SessionDep
from fastapi import APIRouter
from app.schemas.company import (
    SCompanyListResponse,
    SCompanyMessageResponse,
    SCompanyStatusResponse,
    SCompanyResponse,
    SCompanyPageResponse,
    SBulkInnsRequest,
)
from app.services.company_service import (
    update_company_finances,
    enrich_company_data,
    sync_and_enrich_companies,
    get_company_by_inn,
    get_all_companies,
    archive_company,
    restore_company,
    bulk_archive,
    bulk_restore, bulk_soft_deleted,
)

router_companies = APIRouter(prefix="/companies", tags=["Companies"])


@router_companies.get("", response_model=SCompanyPageResponse)
async def all_companies(
    session: SessionDep,
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
):
    """Эндпоинт получения списка компаний с рассчетом прибыли и выручки"""
    return await get_all_companies(session, limit, page)


@router_companies.post("/create/{okved_code}", response_model=SCompanyMessageResponse)
async def create_companies(
    okved_code: str,
    session: SessionDep,
    page: int = Query(1, ge=1),
):
    """Получение компаний по оквед"""
    await sync_companies(okved_code, session, page)
    await session.commit()
    return {
        "status": "ok",
        "message": f"Синхронизация для ОКВЭД {okved_code} завершена",
    }


@router_companies.post("/bulk/archive")
async def bulk_archive_companies(payload: SBulkInnsRequest, session: SessionDep):
    count = await bulk_archive(session, payload.inns)
    await session.commit()
    return {"status": "ok", "count": count}


@router_companies.post("/bulk/restore")
async def bulk_restore_companies(payload: SBulkInnsRequest, session: SessionDep):
    count = await bulk_restore(session, payload.inns)
    await session.commit()
    return {"status": "ok", "count": count}

@router_companies.post("/bulk/delete")
async def bulk_delete_companies(payload: SBulkInnsRequest, session: SessionDep):
    count = await bulk_soft_deleted(session, payload.inns)
    await session.commit()
    return {"status": "ok", "count": count}


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
async def sync_company(
    okved_code: str,
    session: SessionDep,
    page: int = Query(1, ge=1),
    region: str | None = Query(None),
):
    """Обогащение по оквед"""
    await sync_and_enrich_companies(okved_code, session, page, region)
    await session.commit()
    return {
        "status": "ok",
        "message": f"Компании по ОКВЭД {okved_code} загружены и обогащены",
    }


@router_companies.post("/{inn}/archive")
async def archive_company_status(inn: str, session: SessionDep):
    await archive_company(session, inn)
    await session.commit()
    return {"status": "ok"}


@router_companies.post("/{inn}/restore")
async def restore_company_status(inn: str, session: SessionDep):
    await restore_company(session, inn)
    await session.commit()
    return {"status": "restored from archive"}






