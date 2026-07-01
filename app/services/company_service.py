from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.clients.company_api_client import (
    get_company_finances,
    parse_finances,
    update_company_contacts,
    search_companies_by_okved,
    parse_company,
    save_company_if_not_exists,
)
from app.core.logger import logger
from app.exceptions.checko import CheckoAPIError
from app.exceptions.company_exc import CompanyNotFoundError
from app.models.company import Company


def get_company_by_inn(db: Session, inn: str) -> Company:

    company = db.scalar(select(Company).where(Company.inn == inn))
    if not company:
        logger.warning("Company with INN %s not found", inn)
        raise CompanyNotFoundError(f"Company with INN {inn} NOT FOUND")

    return company


def update_company_finances(session, company):
    if not company:
        return
    new_data = get_company_finances(company.inn)
    finances = parse_finances(new_data)

    company.revenue_2024 = finances["revenue_2024"]
    company.revenue_2025 = finances["revenue_2025"]
    company.revenue_2023 = finances["revenue_2023"]
    company.profit_2023 = finances["profit_2023"]
    company.profit_2024 = finances["profit_2024"]
    company.profit_2025 = finances["profit_2025"]


def enrich_company_data(session, company):
    try:
        update_company_contacts(session, company)
    except CheckoAPIError as e:
        logger.warning(
            "Failed to update contacts for %s: %s",
            company.inn,
            e,
        )
    try:
        update_company_finances(session, company)
    except CheckoAPIError as e:
        logger.warning(
            "Failed to update finances for %s: %s",
            company.inn,
            e,
        )


def sync_and_enrich_companies(okved_code: str, session):
    data = search_companies_by_okved(okved_code)

    for raw_company in data["data"]["Записи"]:
        company_data = parse_company(raw_company)
        company = save_company_if_not_exists(session, company_data)

        enrich_company_data(session, company)


def growth_calc(current: int | None, previous: int | None) -> float | None:
    if previous is None or current is None:
        return None
    if previous == 0:
        if current == 0:
            return 0
        return 100
    return round((current - previous) / abs(previous) * 100, 1)
