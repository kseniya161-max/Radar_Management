import httpx
from app.core.config import settings


BASE_URL = 'https://api.checko.ru/v2/search'



def search_companies_by_okved(okved_code: str):
    params = {
        "key": settings.CHECKO_API_KEY,
        "by": "okved",
        "obj": "org",
        "query": okved_code,
        "limit": 2
    }
    with httpx.Client() as client:
        response = client.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()

