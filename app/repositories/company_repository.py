from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company, Progress


class CompanyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_inn(self, inn: str) -> Company | None:
        company = await self.session.execute(select(Company).where(Company.inn == inn))
        return company.scalar_one_or_none()

    async def save_if_not_exists(self, company_data: dict) -> Company:
        inn = company_data["inn"]
        company = await self.get_by_inn(inn)
        if company:
            return company

        company = Company(**company_data)
        self.session.add(company)
        return company

    async def get_all_paginated(
        self,
        limit: int,
        page: int,
    ) -> dict:
        total_stmt = select(func.count()).select_from(Company).where(Company.progress == Progress.ACTIVE)
        total = await self.session.scalar(total_stmt)

        offset = (page - 1) * limit

        priority = case(
            (
                Company.phone.is_not(None)
                & Company.revenue_2024.is_not(None)
                & Company.revenue_2025.is_not(None),
                1,
            ),
            (
                Company.phone.is_not(None),
                2,
            ),
            else_=3,
        )

        stmt = (
            select(Company).where(Company.progress == Progress.ACTIVE)
            .order_by(
                priority.asc(),
                Company.revenue_growth_3.desc().nulls_last(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        companies = result.scalars().all()

        return {
            "total": total,
            "limit": limit,
            "page": page,
            "items": companies,
        }

    async def get_all_ranked_paginated(self, limit: int = 20, page: int = 1):
        offset = (page - 1) * limit
        result = await self.session.execute(
            select(Company).where(Company.progress == Progress.ACTIVE)
            .order_by(Company.ai_priority.desc().nulls_last())
            .offset(offset)
            .limit(limit)
        )
        companies = result.scalars().all()
        total_result = await self.session.execute(
            select(func.count()).select_from(Company).where(Company.progress == Progress.ACTIVE)
        )

        total = total_result.scalar_one()

        return {
            "items": companies,
            "total": total,
            "page": page,
            "limit": limit,
        }

    async def get_all_companies(self) -> list[Company]:

        result = await self.session.execute(select(Company))
        return result.scalars().all()


    async def has_ai_ranked(self) -> bool:
        result = await self.session.execute(select(Company.id).where(Company.progress == Progress.ACTIVE,Company.ai_priority.is_not(None)).limit(1))
        return result.scalar_one_or_none() is not None


    async def change_status(self,inn: str):
        company = await self.get_by_inn(inn)
        if company is None:
            return None

        company.progress = Progress.ARCHIVED

        return company