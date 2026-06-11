from fastapi import FastAPI

app = FastAPI(
    title="LeadRadar API",
    description="Поиск и приоритизация B2B-лидов через API и AI",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"message": "LeadRadar is running"}


from app.core.config import settings

print(settings.DATABASE_URL)
