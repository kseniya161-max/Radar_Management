import httpx
from sqlalchemy import select

from app.core.config import settings
from app.models.company import Company

BASE_URL = "https://api.checko.ru/v2/search"
COMPANY_URL = "https://api.checko.ru/v2/company"
FINANCES_URL = "https://api.checko.ru/v2/finances"


def search_companies_by_okved(okved_code: str):
    """Делает запрос в API Checko и получает список компаний по ОКВЭД."""
    params = {
        "key": settings.CHECKO_API_KEY,
        "by": "okved",
        "obj": "org",
        "query": okved_code,
        "limit": 50,
        "active": "true",
    }
    with httpx.Client() as client:
        response = client.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()


def parse_company(raw_company: dict):
    """Преобразует ответ от Checko API в нормальный словарь"""
    return {
        "inn": raw_company["ИНН"],
        "name": raw_company["НаимСокр"],
        "status": raw_company["Статус"],
        "okved": raw_company["ОКВЭД"],
    }


def save_company_if_not_exists(session, company_data):
    """Сохраняет компанию в БД, если её ещё нет (проверка по ИНН)"""

    inn = company_data["inn"]
    company = session.execute(
        select(Company).where(Company.inn == inn)
    ).scalar_one_or_none()

    if company:
        return company
    new_company = Company(
        inn=company_data["inn"],
        name=company_data["name"],
        status=company_data["status"],
        okved=company_data["okved"],
    )
    session.add(new_company)
    session.commit()
    session.refresh(new_company)
    return new_company


def sync_companies(okved_code: str, session):
    """Получает данные Checko API Парсит каждую компанию Сохраняет в БД(если ещё нет)"""
    data = search_companies_by_okved(okved_code)
    for raw_company in data["data"]["Записи"]:
        company_data = parse_company(raw_company)
        save_company_if_not_exists(session, company_data)


def get_company_contacts(inn: str):
    """Получаем по ИНН контакты"""
    params = {
        "key":settings.CHECKO_API_KEY,
        "inn": inn,
    }

    with httpx.Client() as client:
        response = client.get(COMPANY_URL, params=params)
        response.raise_for_status()
        return response.json()


def parse_contacts(data: dict):
    contacts = data["data"]["Контакты"]
    return {
        "phone": contacts["Тел"][0] if contacts["Тел"] else None,
        "email": contacts["Емэйл"][0] if contacts["Емэйл"] else None,
        "website": contacts["ВебСайт"] if contacts["ВебСайт"] else None,

    }


def update_company_contacts(session, inn: str):
    new_data = get_company_contacts(inn)
    contacts = parse_contacts(new_data)

    company = session.execute(select(Company).where(Company.inn==inn)).scalar_one_or_none()

    if not company:
        return
    company.phone = contacts["phone"]
    company.email = contacts["email"]
    company.website = contacts["website"]

    session.commit()


def get_company_finances(inn: str):
    params = {
        "key": settings.CHECKO_API_KEY,
        "inn": inn,
    }
    with httpx.Client() as client:
        response = client.get(
            FINANCES_URL,
            params=params,
        )
        response.raise_for_status()

        return response.json()


def parse_finances(data: dict):
    finances = data["data"]
    return {"revenue_2024": finances.get("2024", {}).get("2110"),
           "revenue_2025": finances.get("2025", {}).get("2110"),}







