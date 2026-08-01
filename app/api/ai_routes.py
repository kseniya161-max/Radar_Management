from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.company import Company
from app.schemas.company import (
    SCompanyRankedResponse,
    SCompanyAiScoreResponse,
    SCompanyScoreAllResponse,
)
from app.services.ai_service import score_company
from app.tasks.ai_tasks import score_all_companies_task

router = APIRouter(tags=["AI"])


@router.get("/companies/ai_ranked", response_model=list[SCompanyRankedResponse])
async def get_ranked(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company))
    companies = result.scalars().all()
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


@router.post("/companies/{inn}/ai_score", response_model=SCompanyAiScoreResponse)
async def ai_score_company(inn: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.inn == inn))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return await score_company(company)


@router.post("/companies/ai_score_all", response_model=SCompanyScoreAllResponse)
def ai_score_company_all():
    task = score_all_companies_task.delay()

    return {
        "status": "started",
        "task_id": task.id,
    }
