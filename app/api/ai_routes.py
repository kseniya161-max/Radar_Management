from fastapi import HTTPException, APIRouter
from app.database.db import SessionDep
from app.schemas.company import (
    SCompanyRankedResponse,
    SCompanyAiScoreResponse,
    SCompanyScoreAllResponse,
    SCompanyTaskResponse,
)
from app.services.ai_service import score_company
from app.tasks.ai_tasks import score_all_companies_task
from app.exceptions.ai import AiAPIError
from app.repositories.company_repository import CompanyRepository



router_ai = APIRouter(
    prefix="/companies",
    tags=["AI"]
)


@router_ai.get("/ai_ranked", response_model=list[SCompanyRankedResponse])
async def get_ranked(session: SessionDep):
    repo = CompanyRepository(session)
    companies = await repo.get_all_companies()
    ranked = sorted(companies, key=lambda c: c.ai_priority or 0, reverse=True)

    return [
        {
            "inn": c.inn,
            "name": c.name,
            "ai_priority": c.ai_priority,
            "ai_risk": c.ai_risk,
            "phone": c.phone,
            "email": c.email,
            "website": c.website,
        }
        for c in ranked
    ]


@router_ai.post("/{inn}/ai_score", response_model=SCompanyAiScoreResponse)
async def ai_score_company(inn: str, session: SessionDep):
    repo = CompanyRepository(session)
    company = await repo.get_by_inn(inn)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    try:
        return await score_company(company)

    except AiAPIError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )


@router_ai.post("/ai_score_all", response_model=SCompanyTaskResponse)
def ai_score_company_all():
    task = score_all_companies_task.delay()

    return {
        "status": "started",
        "task_id": task.id,
    }
