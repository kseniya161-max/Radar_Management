from fastapi import FastAPI
from app.api.company_routes import router as company_routes
from app.api.ai_routes import router as ai_routes
from app.api.task_routes import router as task_routes
from app.exceptions.ai import AiAPIError
from app.exceptions.checko import CheckoAPIError
from app.exceptions.company_exc import CompanyNotFoundError
from app.exceptions.handlers import (
    company_exception_handler,
    checko_exception_handler,
    ai_exception_handler,
)

print("LOADED MAIN 999")
app = FastAPI(
    title="KSENIA TEST 999",
    description="KSENIA TEST 778",
    version="0.1.0",
)
app.include_router(ai_routes)
app.include_router(company_routes)
app.include_router(task_routes)


app.add_exception_handler(CompanyNotFoundError, company_exception_handler)
app.add_exception_handler(CheckoAPIError, checko_exception_handler)
app.add_exception_handler(AiAPIError, ai_exception_handler)
