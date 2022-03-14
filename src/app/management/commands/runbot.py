from django.core.management.base import BaseCommand

from app.internal.bot import start


class Command(BaseCommand):
    def handle(self, *args, **options):
        start()
