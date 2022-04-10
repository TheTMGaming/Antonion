from django.core.management.base import BaseCommand

from app.internal.transport.bot.starters import start


class Command(BaseCommand):
    def handle(self, *args, **options):
        start()
