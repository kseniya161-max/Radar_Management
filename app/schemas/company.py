from pydantic import BaseModel


class SCompanyResponse(BaseModel):
    id: int
    inn: str
    name: str
    status: str
    okved: str
    revenue_2025: int | None
    revenue_2024: int | None
    revenue_2023: int | None
    tenders_count: int
    courts_count: int
    phone: str | None
    email: str | None
    website: str | None
    registration_date: str | None
    region: str | None
    profit_2023: int | None
    profit_2024: int | None
    profit_2025: int | None
    ai_priority: int | None
    ai_risk: str | None


