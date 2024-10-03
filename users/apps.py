from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta

from django.core.management import call_command
import logging
import os


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        # Prevents running on management commands like `runserver`
        if os.environ.get('RUN_MAIN', None) != 'true':
            return

        scheduler = BackgroundScheduler()
        scheduler.add_job(self.run_periodic_task, IntervalTrigger(
            # + timedelta(weeks=1)
            days=1))
        scheduler.start()

    def run_periodic_task(self):
        call_command('run_job')
