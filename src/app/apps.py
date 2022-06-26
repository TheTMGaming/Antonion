from django.apps import AppConfig as Config
from django.conf import settings
from prometheus_client import start_http_server


class AppConfig(Config):
    name = "app"

    def ready(self) -> None:
        if settings.METRICS:
            start_http_server(settings.METRICS_PORT)
