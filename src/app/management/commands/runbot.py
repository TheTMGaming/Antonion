from django.core.management.base import BaseCommand

from app.internal.polling import start_polling


class Command(BaseCommand):
    def handle(self, *args, **options):
        start_polling()
