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



class SCompanyListResponse(BaseModel):
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
    revenue_growth: float | None
    profit_growth: float | None


class SCompanyMessageResponse(BaseModel):
    status: str
    message: str


class SCompanyStatusResponse(BaseModel):
    status: str

class SAiScore(BaseModel):
    priority: int
    risk: str
    summary: str


class SCompanyAiScoreResponse(BaseModel):
    inn: str
    name: str
    ai_score: SAiScore


class SCompanyScoreAllResponse(BaseModel):
    status: str
    total: int
    processed: int
    failed: int


class SCompanyRankedResponse(BaseModel):
    inn: str
    name: str
    ai_priority: int | None
    ai_risk: str | None
    phone: str | None
    email: str | None
    website: str | None