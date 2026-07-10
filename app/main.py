from fastapi import FastAPI
from app.api.company_routes import router as company_routes
from app.api.ai_routes import router as ai_routes

app = FastAPI(
    title="KSENIA TEST 998",
    description="KSENIA TEST 777",
    version="0.1.0",
)

app.include_router(company_routes)
app.include_router(ai_routes)

