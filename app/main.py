from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.auth_routes import router_auth
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
    user_already_exists_handler,
)
from app.exceptions.user import UserAlreadyExistsError
from app.middlewares.logging import log_companies_only
from app.web.routes import router_web

print("LOADED MAIN !")
app = FastAPI(
    title="Тест",
    description="KSENIA TEST 16.10",
    version="0.1.0",
)


app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)


app.middleware('http')(log_companies_only)

app.include_router(router_ai)
app.include_router(router_companies)
app.include_router(router_tasks)
app.include_router(router_auth)


app.add_exception_handler(CompanyNotFoundError, company_exception_handler)
app.add_exception_handler(CheckoAPIError, checko_exception_handler)
app.add_exception_handler(AiAPIError, ai_exception_handler)
app.add_exception_handler(UserAlreadyExistsError, user_already_exists_handler)
app.include_router(router_web)
