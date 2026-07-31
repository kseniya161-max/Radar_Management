import asyncio

from app.celery_app import celery
from app.services.ai_service import score_all_companies
from app.database.db import SessionLocal



@celery.task
def score_all_companies_task():

    async def run():
        async with SessionLocal() as db:
            result = await score_all_companies(db)
            await db.commit()
            return result

    return asyncio.run(run())