from django.apps import AppConfig
from django.conf import settings

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

# class TestConfig(AppConfig):
#     name = 'test'

#     def ready(self):
#         if settings.SCHEDULER_DEFAULT:
#             from . import operator
#             operator.start()