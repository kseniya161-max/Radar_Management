from fastapi import APIRouter
from celery.result import AsyncResult

from app.celery_app import celery

router = APIRouter(tags=["Tasks"])


@router.get("/tasks/{task_id}")
def get_task_status(task_id: str):

    task = AsyncResult(
        task_id,
        app=celery,
    )

    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result,
    }
