from django.apps import AppConfig as Config
from django.conf import settings
from prometheus_client import start_http_server


class AppConfig(Config):
    name = "app"

    def ready(self):
        if not settings.DEBUG:
            start_http_server(8010)
