from fastapi import FastAPI
from app.api.company_routes import router_companies
from app.api.ai_routes import router_ai
from app.api.task_routes import router_tasks
from app.exceptions.ai import AiAPIError
from app.exceptions.checko import CheckoAPIError
from app.exceptions.company_exc import CompanyNotFoundError
from app.exceptions.handlers import (
    company_exception_handler,
    checko_exception_handler,
    ai_exception_handler,
)

print("LOADED MAIN 998")
app = FastAPI(
    title="KSENIA TEST 995",
    description="KSENIA TEST 77",
    version="0.1.0",
)
app.include_router(router_ai)
app.include_router(router_companies)
app.include_router(router_tasks)


app.add_exception_handler(CompanyNotFoundError, company_exception_handler)
app.add_exception_handler(CheckoAPIError, checko_exception_handler)
app.add_exception_handler(AiAPIError, ai_exception_handler)
