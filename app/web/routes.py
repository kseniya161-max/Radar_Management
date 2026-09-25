from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.repositories.company_repository import CompanyRepository
from app.database.db import SessionDep

router_web = APIRouter(
    prefix="/web",
    tags=["Web"],
)

templates = Jinja2Templates(directory="app/templates")


@router_web.get("/companies", include_in_schema=False)
async def companies_page(
    request: Request,
    session: SessionDep,
    page: int = 1,
):
    repo = CompanyRepository(session)

    data = await repo.get_all_paginated(
        limit=20,
        page=page,
    )
    count_active = await repo.count_progress_active()
    count_phone = await repo.count_active_with_phone()
    count_finance = await repo.count_active_with_finance()
    count_archived = await repo.count_archived()

    return templates.TemplateResponse(
        request=request,
        name="companies.html",
        context={
            "companies": data["items"],
            "total": data["total"],
            "page": data["page"],
            "limit": data["limit"],
            "count_active": count_active,
            "count_phone": count_phone,
            "count_finance": count_finance,
            "count_archived": count_archived,
        },
    )


@router_web.get("/", include_in_schema=False)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
    )


@router_web.get("/ranked", include_in_schema=False)
async def rank(request: Request, session: SessionDep, page: int = 1):
    repo = CompanyRepository(session)

    data = await repo.get_all_ranked_paginated(
        limit=20,
        page=page,
    )

    has_ai_ranking = await repo.has_ai_ranked()
    count_rank = await repo.count_ranked()
    count_not_rank = await repo.count_not_ranked()

    return templates.TemplateResponse(
        request=request,
        name="ranked_companies.html",
        context={
            "companies": data["items"],
            "total": data["total"],
            "page": data["page"],
            "limit": data["limit"],
            "has_ai_ranking": has_ai_ranking,
            "count_rank": count_rank,
            "count_not_rank": count_not_rank,
        },
    )


@router_web.get("/archived", include_in_schema=False)
async def get_archived(request: Request, session: SessionDep, page: int = 1):

    repo = CompanyRepository(session)
    data = await repo.get_archive_paginate(limit=20, page=page)

    return templates.TemplateResponse(
        request=request,
        name="archived_companies.html",
        context={
            "companies": data["items"],
            "total": data["total"],
            "page": data["page"],
            "limit": data["limit"],
        },
    )
