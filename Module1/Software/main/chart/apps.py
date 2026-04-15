from django.apps import AppConfig
import os
class ChartConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chart'
    def ready(self):
        os.startfile("http://127.0.0.1:8000/")