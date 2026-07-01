from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.clients.ai_scoring_service import score_company, score_all_companies
from app.database.db import get_db
from app.models.company import Company
from app.schemas.company import SCompanyRankedResponse, SCompanyAiScoreResponse, SCompanyScoreAllResponse

router = APIRouter(
    tags=["AI"]
)

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
        raise HTTPException(
        status_code=404,
        detail="Company not found"
    )
    result = score_company(company)
    return result


@router.post("/companies/ai_score_all", response_model=SCompanyScoreAllResponse)
def ai_score_company_all(db: Session = Depends(get_db)):
    result = score_all_companies(db)

    db.commit()

    return {
        "status": "ok",
        "total": result["total"],
        "processed": result["processed"],
        "failed": result["total"] - result["processed"],
    }