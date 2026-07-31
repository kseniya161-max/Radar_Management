from app.celery_app import celery
from app.services.ai_service import score_all_companies
from app.database.db import SessionLocal

@celery.task
def score_all_companies_task():
    db = SessionLocal

    try:
        result = score_all_companies(db)
        db.commit()
        return result
    finally:
        db.close()