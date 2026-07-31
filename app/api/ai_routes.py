from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy import select
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
def get_ranked(db: Session = Depends(get_db)):
    companies = db.scalars(select(Company)).all()
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
def ai_score_company(inn: str, db: Session = Depends(get_db)):
    company = db.scalar(select(Company).where(Company.inn == inn))
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    result = score_company(company)
    return result


@router.post("/companies/ai_score_all", response_model=SCompanyScoreAllResponse)
def ai_score_company_all():
    task = score_all_companies_task.delay()

    return {
        "status": "started",
        "task_id": task.id,
    }
