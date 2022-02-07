from django.core.management.base import BaseCommand
from app.internal import bot


class Command(BaseCommand):
    def handle(self, *args, **options):
        bot.start()
