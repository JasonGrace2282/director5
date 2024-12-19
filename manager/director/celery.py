import logging
import os

from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "director.settings")

app = Celery("director5")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@after_setup_logger.connect
@after_setup_task_logger.connect
def setup_logger(logger, **kwargs):
    from django.conf import settings

    logger.level = getattr(logging, settings.LOG_LEVEL)
