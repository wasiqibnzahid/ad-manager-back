from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
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
        scheduler.add_job(self.run_periodic_task, 'interval', hours=6)
        scheduler.start()

    def run_periodic_task(self):
        call_command('run_job')
