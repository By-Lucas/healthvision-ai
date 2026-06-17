"""Celery application configured to use RabbitMQ as broker.

Kept in its own module so both the API (which only needs to *send* tasks) and
the worker (which executes them) can import the same configured instance.
"""
from __future__ import annotations

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "healthvision",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_time_limit=120,
    task_soft_time_limit=90,
    worker_max_tasks_per_child=100,
    timezone="UTC",
    enable_utc=True,
)

# Ensure tasks module is imported so tasks register on the worker.
celery_app.autodiscover_tasks(["app.infrastructure.queue"])
