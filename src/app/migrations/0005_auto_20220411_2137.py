# Generated by Django 3.2.12 on 2022-04-11 16:37

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0004_auto_20220410_2159"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="bankaccount",
            name="balance_currency",
        ),
        migrations.AlterField(
            model_name="bankaccount",
            name="balance",
            field=models.DecimalField(
                decimal_places=2, default=0, max_digits=20, validators=[django.core.validators.MinValueValidator(0)]
            ),
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("type", models.IntegerField(choices=[(1, "Transfer")], default=1)),
                (
                    "accrual",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=20,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now=True)),
                (
                    "destination",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transactions_to_me",
                        to="app.telegramuser",
                    ),
                ),
                (
                    "source",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="transactions", to="app.telegramuser"
                    ),
                ),
            ],
            options={
                "verbose_name": "Transaction",
                "verbose_name_plural": "Transactions",
                "db_table": "transactions",
            },
        ),
    ]
