"""Celery application configuration."""
from celery import Celery
from celery.schedules import crontab
from app.config import get_settings

settings = get_settings()

celery = Celery(
    "scraper_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.core.tasks.beat_tasks",
        "app.core.tasks.scrape_task"
    ]
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Celery Beat periodic tasks
    beat_schedule={
        "dispatch-due-schedules": {
            "task": "schedules.dispatch_due",
            "schedule": crontab(minute="*"),  # every minute
        },
    },
)

# Auto-discover tasks in app.core.tasks
celery.autodiscover_tasks(["app.core.tasks"])
