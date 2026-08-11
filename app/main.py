from fastapi import FastAPI
from app.api.company_routes import router as company_routes
from app.api.ai_routes import router as ai_routes
from app.api.task_routes import router as task_routes
print("LOADED MAIN 999")
app = FastAPI(
    title="KSENIA TEST 999",
    description="KSENIA TEST 778",
    version="0.1.0",
)
app.include_router(ai_routes)
app.include_router(company_routes)
app.include_router(task_routes)

