from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession


from app.clients.company_api_client import (
    get_company_finances,
    parse_finances,
    update_company_contacts,
    search_companies_by_okved,
    parse_company,
)
from app.core.logger import logger
from app.exceptions.checko import CheckoAPIError
from app.exceptions.company_exc import CompanyNotFoundError
from app.models.company import Company



def growth_calc(current: int | None, previous: int | None) -> float | None:
    if previous is None or current is None:
        return None
    if previous == 0:
        if current == 0:
            return 0
        return 100
    return round((current - previous) / abs(previous) * 100, 1)


async def get_all_companies(
    db: AsyncSession,
    limit: int,
    offset: int,
):

    total_stmt = select(func.count()).select_from(Company)
    total = await db.scalar(total_stmt)
    stmt = select(Company).order_by(case((Company.phone.is_not (None), 1), else_ = 0,)).desc().offset(offset).limit(limit)
    result = await db.execute(stmt)

    companies = result.scalars().all()
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": companies,
    }


def update_company_growth(company: Company):
    company.revenue_growth_3 = growth_calc(company.revenue_2025, company.revenue_2024)
    company.profit_growth_3 = growth_calc(company.profit_2025,company.profit_2024)




async def save_company_if_not_exists(session: AsyncSession, company_data):
    inn = company_data["inn"]
    result = await session.execute(select(Company).where(Company.inn == inn))
    company = result.scalar_one_or_none()

    if company:
        return company

    company = Company(**company_data)
    session.add(company)
    return company


async def get_company_by_inn(db: AsyncSession, inn: str) -> Company:

    company = await db.scalar(select(Company).where(Company.inn == inn))
    if not company:
        logger.warning("Company with INN %s not found", inn)
        raise CompanyNotFoundError(f"Company with INN {inn} NOT FOUND")

    return company




async def update_company_finances(db: AsyncSession, company: Company):
    if not company:
        return
    new_data = await get_company_finances(company.inn)
    finances = parse_finances(new_data)

    company.revenue_2024 = finances["revenue_2024"]
    company.revenue_2025 = finances["revenue_2025"]
    company.revenue_2023 = finances["revenue_2023"]
    company.profit_2023 = finances["profit_2023"]
    company.profit_2024 = finances["profit_2024"]
    company.profit_2025 = finances["profit_2025"]

    update_company_growth(company)



async def enrich_company_data(session: AsyncSession, company: Company):
    try:
        await update_company_contacts(session, company)
    except CheckoAPIError as e:
        logger.warning(
            "Failed to update contacts for %s: %s",
            company.inn,
            e,
        )
    try:
        await update_company_finances(session, company)
    except CheckoAPIError as e:
        logger.warning(
            "Failed to update finances for %s: %s",
            company.inn,
            e,
        )


async def sync_and_enrich_companies(okved_code: str, session: AsyncSession):
    data = await search_companies_by_okved(okved_code)

    for raw_company in data["data"]["Записи"]:
        company_data = parse_company(raw_company)
        company = await save_company_if_not_exists(session, company_data)

        await enrich_company_data(session, company)


