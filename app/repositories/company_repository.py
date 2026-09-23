from sqlalchemy import select, func, case, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company, Progress


class CompanyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_inn(self, inn: str) -> Company | None:
        company = await self.session.execute(select(Company).where(Company.inn == inn).where(Company.is_deleted == False))
        return company.scalar_one_or_none()

    async def save_if_not_exists(self, company_data: dict) -> Company:
        inn = company_data["inn"]
        company = await self.session.execute(select(Company).where(Company.inn == inn))
        company = company.scalar_one_or_none()
        if company:
            if company.is_deleted == True:
                company.is_deleted = False
            return company
        company = Company(**company_data)
        self.session.add(company)
        return company

    async def get_all_paginated(
        self,
        limit: int,
        page: int,
    ) -> dict:
        total_stmt = (
            select(func.count())
            .select_from(Company)
            .where(Company.progress == Progress.ACTIVE).where(Company.is_deleted == False)
        )
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
            .where(Company.progress == Progress.ACTIVE).where(Company.is_deleted == False)
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
            select(Company)
            .where(Company.progress == Progress.ACTIVE).where(Company.is_deleted == False)
            .order_by(Company.ai_priority.desc().nulls_last())
            .offset(offset)
            .limit(limit)
        )
        companies = result.scalars().all()
        total_result = await self.session.execute(
            select(func.count())
            .select_from(Company)
            .where(Company.progress == Progress.ACTIVE).where(Company.is_deleted == False)
        )

        total = total_result.scalar_one()

        return {
            "items": companies,
            "total": total,
            "page": page,
            "limit": limit,
        }

    async def get_all_companies(self) -> list[Company]:

        result = await self.session.execute(select(Company).where(Company.is_deleted == False))
        return result.scalars().all()

    async def has_ai_ranked(self) -> bool:
        result = await self.session.execute(
            select(Company.id)
            .where(
                Company.progress == Progress.ACTIVE, Company.ai_priority.is_not(None)
            ).where(Company.is_deleted == False)
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def change_status(self, inn: str):
        company = await self.get_by_inn(inn)
        if company is None:
            return None

        company.progress = Progress.ARCHIVED

        return company

    async def restore(self, inn: str):
        company = await self.get_by_inn(inn)
        if company is None:
            return None
        company.progress = Progress.ACTIVE
        return company

    async def get_archive_paginate(self, limit: int = 20, page: int = 1):
        total_amount_company = (
            select(func.count())
            .select_from(Company)
            .where(Company.progress == Progress.ARCHIVED).where(Company.is_deleted == False)
        )
        total_amount = await self.session.scalar(total_amount_company)
        offset = (page - 1) * limit
        total_company = (
            select(Company)
            .where(Company.progress == Progress.ARCHIVED).where(Company.is_deleted == False)
            .order_by(Company.id.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(total_company)
        items = result.scalars().all()
        return {"total": total_amount, "limit": limit, "page": page, "items": items}

    async def bulk_change_progress(
        self, inns: list[str], new_progress: Progress
    ) -> int:
        stmt = (
            update(Company).where(Company.inn.in_(inns)).where(Company.is_deleted == False).values(progress=new_progress)
        )
        result = await self.session.execute(stmt)
        total_result = result.rowcount
        return total_result


    async def bulk_soft_delete(self, inns: list[str]):
        stmt = (update(Company).where(Company.inn.in_(inns)).where(Company.is_deleted == False).values(is_deleted = True))
        result = await self.session.execute(stmt)
        total_result = result.rowcount
        return total_result
