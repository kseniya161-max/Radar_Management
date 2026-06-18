import json
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.clients.ai_client import ask_ai
from app.models.company import Company
from app.services.company_service import growth_calc


def build_company_prompt(company: Company) -> str:
    growth_revenue = growth_calc(company.revenue_2025, company.revenue_2024)
    growth_profit = growth_calc(company.profit_2025, company.profit_2024)

    return f"""Вычисли прирост прибыли revenue_2025 и revenue_2024 в 
    процентном соотношении вычисли прирост выручки profit_2025 и profit_2024 в приоритетном соотношении и 
    cоздай приритетность. ты  B2B lead scoring system верни только валидный JSON ответ должен быть на русском языке{{
  "priority": 1-100,
  "risk": "low|medium|high",
  "summary": "short explanation"
}}
Company data:
- Name: {company.name}
- INN: {company.inn}
- OKVED: {company.okved}
- Region: {company.region}
- Revenue 2025: {company.revenue_2025}
- Revenue 2024: {company.revenue_2024}
- Revenue growth %: {growth_revenue}
- Profit 2025: {company.profit_2025}
- Profit 2024: {company.profit_2024}
- Profit growth %: {growth_profit}
- Website: {company.website}
- Email: {company.email}
- Phone: {company.phone}"""


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


def score_company(company:Company)->dict:
    prompt = build_company_prompt(company)
    ai_response = ask_ai(prompt)
    parsed = extract_json(ai_response)
    return {
        "inn": company.inn,
        "name": company.name,
        "ai_score": parsed
    }


def score_all_companies(db: Session):
    companies = db.scalars(select(Company)).all()

    results = []

    for company in companies:
        try:
            result = score_company(company)
            if not result:
                continue

            ai = result.get("ai_score") or {}

            priority = ai.get("priority")
            if priority is None:
                priority = 0

            company.ai_priority = priority
            company.ai_risk = ai.get("risk", "unknown")

            results.append(result)

        except Exception as e:
            print(f"ERROR scoring {company.inn}: {e}")
            continue

    return {
        "total": len(companies),
        "processed": len(results),
        "results": results,
    }
