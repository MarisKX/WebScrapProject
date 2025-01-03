import os
from django.apps import AppConfig


class SchedulerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "scheduler"

    def ready(self):
        if os.environ.get("RUN_MAIN", None) != "true":
            from .apscheduler import start

            start()
