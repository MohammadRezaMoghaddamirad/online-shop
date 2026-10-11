"""
Celery tasks for authentication app.
"""
import time
from celery import shared_task


@shared_task
def test_task(name):
    """تست ساده برای Celery"""
    time.sleep(3)
    return f"Hello, {name}! Task completed."