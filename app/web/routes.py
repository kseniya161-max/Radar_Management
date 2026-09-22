from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.database.db import SessionLocal
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
    page: int = 1,
):
    async with SessionLocal() as session:
        repo = CompanyRepository(session)

        data = await repo.get_all_paginated(
            limit=20,
            page=page,
        )

    return templates.TemplateResponse(
        request=request,
        name="companies.html",
        context={
            "companies": data["items"],
            "total": data["total"],
            "page": data["page"],
            "limit": data["limit"],
        },
    )


@router_web.get("/", include_in_schema=False)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
    )


@router_web.get("/ranked", include_in_schema=False)
async def rank(request: Request, page: int = 1):
    async with SessionLocal() as session:
        repo = CompanyRepository(session)

        data = await repo.get_all_ranked_paginated(
            limit=20,
            page=page,
        )

        has_ai_ranking = await repo.has_ai_ranked()

    return templates.TemplateResponse(
        request=request,
        name="ranked_companies.html",
        context={
            "companies": data["items"],
            "total": data["total"],
            "page": data["page"],
            "limit": data["limit"],
            "has_ai_ranking": has_ai_ranking,
        },
    )

@router_web.get("/archived",include_in_schema=False)
async def get_archived(request: Request, page: int = 1):
    async with SessionLocal() as session:
        repo = CompanyRepository(session)
        data = await repo.get_archive_paginate(limit=20, page=page)
        return templates.TemplateResponse(
            request=request,
            name="archived_companies.html",
            context={
                "companies": data["companies"],
                "total": data["total"],
                "page": data["page"],
                "limit": data["limit"],
            },
        )

