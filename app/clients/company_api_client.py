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
        "limit": 2,
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
        "registration_date": raw_company.get("ДатаРег"),
    }


def save_company_if_not_exists(session, company_data):
    inn = company_data["inn"]

    company = session.execute(
        select(Company).where(Company.inn == inn)
    ).scalar_one_or_none()

    if company:
        return company

    company = Company(**company_data)
    session.add(company)
    return company


def sync_companies(okved_code: str, session):
    """Получает данные Checko API Парсит каждую компанию Сохраняет в БД(если ещё нет)"""
    data = search_companies_by_okved(okved_code)
    print(data)
    for raw_company in data["data"]["Записи"]:
        company_data = parse_company(raw_company)
        save_company_if_not_exists(session, company_data)


def get_company_contacts(inn: str):
    """Получаем по ИНН контакты"""
    params = {
        "key": settings.CHECKO_API_KEY,
        "inn": inn,
    }

    with httpx.Client() as client:
        response = client.get(COMPANY_URL, params=params)
        response.raise_for_status()
        return response.json()


def parse_contacts(data: dict):
    company_data = data.get("data", {})
    contacts = company_data.get("Контакты")

    region_info = company_data.get("Регион", {})
    region_name = region_info.get("Наим") if region_info else None

    if not contacts:
        return {
            "phone": None,
            "email": None,
            "website": None,
            "region": region_name,
        }

    phones = contacts.get("Тел", [])
    emails = contacts.get("Емэйл", [])
    return {
        "phone": ", ".join(phones) if phones else None,
        "email": ", ".join(emails) if emails else None,
        "website": contacts.get("ВебСайт"),
        "region": region_name,
    }


def update_company_contacts(session, company):
    if not company:
        return
    new_data = get_company_contacts(company.inn)
    contacts = parse_contacts(new_data)

    company.phone = contacts["phone"]
    company.email = contacts["email"]
    company.website = contacts["website"]
    company.region = contacts["region"]


def get_company_finances(inn: str):
    params = {
        "key": settings.CHECKO_API_KEY,
        "inn": inn,
        "extended": "true",
    }
    with httpx.Client() as client:
        response = client.get(
            FINANCES_URL,
            params=params,
        )
        response.raise_for_status()

        return response.json()


def parse_finances(data: dict):
    finances = data.get("data", {})

    return {
        "revenue_2024": finances.get("2024", {}).get("2110", {}).get("СумОтч"),
        "revenue_2025": finances.get("2025", {}).get("2110", {}).get("СумОтч"),
        "revenue_2023": finances.get("2023", {}).get("2110", {}).get("СумОтч"),
        "profit_2023": finances.get("2023", {}).get("2400", {}).get("СумОтч"),
        "profit_2024": finances.get("2024", {}).get("2400", {}).get("СумОтч"),
        "profit_2025": finances.get("2025", {}).get("2400", {}).get("СумОтч"),
    }
