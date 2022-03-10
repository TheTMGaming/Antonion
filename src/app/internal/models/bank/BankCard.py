from django.contrib.auth.hashers import BCryptPasswordHasher
from django.db import models


class BankCard(models.Model):
    number = models.BigAutoField(primary_key=True)

    bank_account = models.ForeignKey("BankAccount", on_delete=models.CASCADE)
    passport = models.ForeignKey("Passport", on_delete=models.PROTECT)
    code = models.CharField(max_length=255)

    created_at = models.DateField(auto_now_add=True)
    closed_at = models.DateField()

    def __str__(self):
        return str(self.number)

    def save(self, *args, **kwargs):
        hasher = BCryptPasswordHasher()
        self.code = hasher.encode(self.code, hasher.salt())
        super().save(*args, **kwargs)

    class Meta:
        db_table = "bank_cards"
        verbose_name = "Bank Card"
        verbose_name_plural = "Bank Cards"
