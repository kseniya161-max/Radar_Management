from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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
from app.web.routes import router_web

print("LOADED MAIN 1")
app = FastAPI(
    title="KSENIA TEST 0",
    description="KSENIA TEST 0",
    version="0.1.0",
)



templates = Jinja2Templates(directory="app/templates")


app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)



@app.get("/", include_in_schema=False)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
    )
app.include_router(router_ai)
app.include_router(router_companies)
app.include_router(router_tasks)


app.add_exception_handler(CompanyNotFoundError, company_exception_handler)
app.add_exception_handler(CheckoAPIError, checko_exception_handler)
app.add_exception_handler(AiAPIError, ai_exception_handler)
app.include_router(router_web)