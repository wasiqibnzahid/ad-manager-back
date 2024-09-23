from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        # Automatically create an admin user if it doesn't exist
        try:
            User = get_user_model()
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    password='12345',
                    email='admin@gmail.com'
                )
        except OperationalError:
            # This might occur during the first migration when tables are not yet created
            pass
