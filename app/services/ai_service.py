import json
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.clients.ai_client import ask_ai
from app.core.logger import logger
from app.exceptions.ai import AiAPIError
from app.models.company import Company
from app.repositories.company_repository import CompanyRepository
from app.services.company_service import growth_calc


def build_company_prompt(company: Company) -> str:
    growth_revenue = growth_calc(company.revenue_2025, company.revenue_2024)
    growth_profit = growth_calc(company.profit_2025, company.profit_2024)

    return f"""
Ты — B2B lead scoring system.

Твоя задача- оценить компанию как потенциального B2B-клиента.

AI Priority - это коммерческий приоритет компании для отдела продаж
по шкале от 1 до 100.

Чем выше AI Priority, тем выше потенциальная коммерческая привлекательность
компании и тем выше приоритет для работы с ней.

При определении AI Priority учитывай в первую очередь:
- рост выручки за 2024 и 2025 год revenue_2025 и revenue_2024;
- рост прибыли за 2024 и 2025 profit_2025 и profit_2024;
- абсолютный размер выручки;
- абсолютный размер прибыли;
- устойчивость финансовой динамики;
- доступные контактные данные;
- другие предоставленные данные о компании.

AI Risk- отдельная характеристика.
Она показывает уровень риска при работе с компанией.

Используй:
- low — низкий риск;
- medium — средний риск;
- high — высокий риск.

AI Risk НЕ является прямой обратной шкалой AI Priority.
Компания может иметь одновременно высокий AI Priority и высокий AI Risk,
если она коммерчески привлекательна, но при этом имеет существенные риски.

Верни только валидный JSON на русском языке:

{{
    "priority": 1-100,
    "risk": "low|medium|high",
    "summary": "краткое объяснение оценки"
}}

Данные компании:

- Название: {company.name}
- ИНН: {company.inn}
- ОКВЭД: {company.okved}
- Регион: {company.region}

- Выручка 2025: {company.revenue_2025}
- Выручка 2024: {company.revenue_2024}
- Рост выручки %: {growth_revenue}

- Прибыль 2025: {company.profit_2025}
- Прибыль 2024: {company.profit_2024}
- Рост прибыли %: {growth_profit}

- Website: {company.website}
- Email: {company.email}
- Phone: {company.phone}
"""


def extract_json(text: str | None) -> dict:
    if not text:
        return {"error": "empty_response", "raw": text}

    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        return {"error": "invalid_json", "raw": text}

    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return {"error": "json_decode_error", "raw": text}


async def score_company(company: Company) -> dict:
    prompt = build_company_prompt(company)
    ai_response = ask_ai(prompt)
    parsed = extract_json(ai_response)
    return {"inn": company.inn, "name": company.name, "ai_score": parsed}


async def score_all_companies(db: AsyncSession):
    repo = CompanyRepository(db)
    companies = await repo.get_all_companies()

    results = []
    for company in companies:
        try:
            result = await score_company(company)
            if not result:
                continue

            ai = result.get("ai_score") or {}

            priority = ai.get("priority")
            if priority is None:
                priority = 0

            company.ai_priority = priority
            company.ai_risk = ai.get("risk", "unknown")

            results.append(result)

        except AiAPIError as e:
            logger.error("Error scoring company %s: %s", company.inn, e)
            continue

    await db.commit()

    return {
        "total": len(companies),
        "processed": len(results),
        "results": results,
    }
