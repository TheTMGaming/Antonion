from django.core.management.base import BaseCommand

import app.internal.bot as bot


class Command(BaseCommand):
    def handle(self, *args, **options):
        bot.start()
