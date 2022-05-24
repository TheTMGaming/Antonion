from django.db.models import IntegerChoices


class TransactionTypes(IntegerChoices):
    TRANSFER = 1
