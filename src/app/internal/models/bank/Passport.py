from django.core.validators import MaxValueValidator
from django.db import models


class Passport(models.Model):
    series = models.PositiveIntegerField(validators=[MaxValueValidator(9999)])
    number = models.PositiveIntegerField(validators=[MaxValueValidator(999999)])

    surname = models.CharField(max_length=127)
    name = models.CharField(max_length=127)

    citizenship = models.CharField(max_length=127)
    place_of_birth = models.CharField(max_length=511)

    birthday = models.DateField()
    created_at = models.DateField()

    def __str__(self):
        return f"{self.series} {self.number}"

    class Meta:
        db_table = "passports"
        verbose_name = "Passport"
        verbose_name_plural = "Passports"
        unique_together = (("series", "number"),)
