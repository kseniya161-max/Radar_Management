from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.company import Company


class CompanyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_by_inn(self, inn:str) -> Company | None:
        company = await self.session.execute(select(Company).where(Company.inn == inn))
        return company.scalar_one_or_none()
