from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.exceptions.ai import AiAPIError
from app.models.company import Company
from app.services.ai_service import score_company


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
        total_stmt = select(func.count()).select_from(Company)
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
            select(Company)
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

    async def get_all_companies(self) -> list[Company]:

        result = await self.session.execute(select(Company))
        return result.scalars().all()
