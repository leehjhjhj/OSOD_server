from django.apps import AppConfig
from django.conf import settings

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        from .scheduler import MyScheduler
        scheduler = MyScheduler()
        scheduler.scheduler.start()
