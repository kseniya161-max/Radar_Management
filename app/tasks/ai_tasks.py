import asyncio

from app.celery_app import celery
from app.services.ai_service import score_all_companies
from app.database.db import SessionLocal

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@celery.task
def score_all_companies_task():

    async def run():
        async with SessionLocal() as db:
            result = await score_all_companies(db)
            return result

    return asyncio.run(run())
