"""Celery worker entrypoint.

Run with:  celery -A worker.celery_app worker --loglevel=info
Importing tasks here ensures they are registered on the worker.
"""
from app.infrastructure.queue.celery_app import celery_app  # noqa: F401
from app.infrastructure.queue import tasks  # noqa: F401
