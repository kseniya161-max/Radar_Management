from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
import csv
import io


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
from app.models.company import Company, Progress
from app.repositories.company_repository import CompanyRepository


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
    page: int,
):
    repo = CompanyRepository(db)
    return await repo.get_all_paginated(limit, page)


def update_company_growth(company: Company):
    company.revenue_growth_3 = growth_calc(company.revenue_2025, company.revenue_2024)
    company.profit_growth_3 = growth_calc(company.profit_2025, company.profit_2024)


async def save_company_if_not_exists(db: AsyncSession, company_data):
    repo = CompanyRepository(db)
    return await repo.save_if_not_exists(company_data)


async def get_company_by_inn(db: AsyncSession, inn: str) -> Company:

    repo = CompanyRepository(db)
    company = await repo.get_by_inn(inn)
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


async def enrich_company_data(db: AsyncSession, company: Company):
    try:
        await update_company_contacts(db, company)
    except CheckoAPIError as e:
        logger.warning(
            "Failed to update contacts for %s: %s",
            company.inn,
            e,
        )
    try:
        await update_company_finances(db, company)
    except CheckoAPIError as e:
        logger.warning(
            "Failed to update finances for %s: %s",
            company.inn,
            e,
        )


async def sync_and_enrich_companies(
    okved_code: str, db: AsyncSession, page: int = 1, region: str | None = None
):
    data = await search_companies_by_okved(okved_code, page, region)

    for raw_company in data["data"]["Записи"]:
        company_data = parse_company(raw_company)
        company = await save_company_if_not_exists(db, company_data)

        await enrich_company_data(db, company)


async def archive_company(db: AsyncSession, inn: str):
    repo = CompanyRepository(db)
    company = await repo.change_status(inn)
    if not company:
        raise CompanyNotFoundError(f"Company with INN {inn} NOT FOUND")
    return company


async def restore_company(db: AsyncSession, inn: str):
    repo = CompanyRepository(db)
    company = await repo.restore(inn)
    if not company:
        raise CompanyNotFoundError(f"Company with INN {inn} NOT FOUND")
    return company


async def bulk_archive(db: AsyncSession, inns: list[str]) -> int:
    repo = CompanyRepository(db)
    count = await repo.bulk_change_progress(inns, Progress.ARCHIVED)
    return count


async def bulk_restore(db: AsyncSession, inns: list[str]) -> int:
    repo = CompanyRepository(db)
    count = await repo.bulk_change_progress(inns, Progress.ACTIVE)
    return count


async def bulk_soft_deleted(db: AsyncSession, inns: list[str]) -> int:
    repo = CompanyRepository(db)
    count = await repo.bulk_soft_delete(inns)
    return count


async def generate_csv(companies: list) -> str:
    output = io.StringIO()
    writer = csv.writer(
        output,
        delimiter=";",
        quoting=csv.QUOTE_MINIMAL,
    )

    writer.writerow([
        "ИНН", "Название", "Телефон", "Email", "Регион",
        "Дата регистрации", "Выручка 2024", "Выручка 2025",
        "Рост выручки", "Рост прибыли", "AI Priority", "AI Risk",
    ])
    for company in companies:
        writer.writerow([
            company.inn or "",
            company.name or "",
            company.phone or "",
            company.email or "",
            company.region or "",
            company.registration_date or "",
            company.revenue_2024 if company.revenue_2024 is not None else "",
            company.revenue_2025 if company.revenue_2025 is not None else "",
            company.revenue_growth_3 if company.revenue_growth_3 is not None else "",
            company.profit_growth_3 if company.profit_growth_3 is not None else "",
            company.ai_priority if company.ai_priority is not None else "",
            company.ai_risk or "",
        ])

    return "\ufeff" + output.getvalue()



