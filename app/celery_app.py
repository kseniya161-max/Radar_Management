from celery import Celery

celery = Celery(
    "radar",
    broker="redis://localhost:6379/0",
    include=["app.tasks.ai_tasks"],
)
