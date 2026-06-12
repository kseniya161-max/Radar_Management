from sqlalchemy.orm import Session
from app.models.company import Company
from sqlalchemy import select


def create_company(db: Session):
    company = Company(
        inn="1234567890", name="ООО Ромашка", status="ACTIVE", okved="01.04"
    )

    db.add(company)
    db.commit()
    db.refresh(company)

    return company


def get_companies(db: Session):
    stmt = select(Company)
    result = db.execute(stmt)
    return result.scalars().all()


def get_company_by_inn(db: Session, inn: str):
    stmt = select(Company).where(Company.inn == inn)

    result = db.execute(stmt)

    return result.scalar_one_or_none()
