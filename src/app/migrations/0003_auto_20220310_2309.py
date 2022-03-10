# Generated by Django 3.2.12 on 2022-03-10 18:09

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_telegramuser"),
    ]

    operations = [
        migrations.CreateModel(
            name="BankAccount",
            fields=[
                ("number", models.BigAutoField(primary_key=True, serialize=False)),
                ("balance", models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ("created_at", models.DateField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Bank Account",
                "verbose_name_plural": "Bank Accounts",
                "db_table": "bank_accounts",
            },
        ),
        migrations.AlterModelOptions(
            name="telegramuser",
            options={"verbose_name": "Telegram User", "verbose_name_plural": "Telegram Users"},
        ),
        migrations.AlterModelTable(
            name="telegramuser",
            table="telegram_users",
        ),
        migrations.CreateModel(
            name="Passport",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("series", models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(9999)])),
                ("number", models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(999999)])),
                ("surname", models.CharField(max_length=127)),
                ("name", models.CharField(max_length=127)),
                ("citizenship", models.CharField(max_length=127)),
                ("place_of_birth", models.CharField(max_length=511)),
                ("birthday", models.DateField()),
                ("created_at", models.DateField()),
            ],
            options={
                "verbose_name": "Passport",
                "verbose_name_plural": "Passports",
                "db_table": "passports",
                "unique_together": {("series", "number")},
            },
        ),
        migrations.CreateModel(
            name="BankCard",
            fields=[
                ("number", models.BigAutoField(primary_key=True, serialize=False)),
                ("code", models.CharField(max_length=255)),
                ("created_at", models.DateField(auto_now_add=True)),
                ("closed_at", models.DateField()),
                ("bank_account", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="app.bankaccount")),
                ("passport", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="app.passport")),
            ],
            options={
                "verbose_name": "Bank Card",
                "verbose_name_plural": "Bank Cards",
                "db_table": "bank_cards",
            },
        ),
        migrations.AddField(
            model_name="bankaccount",
            name="passport",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="app.passport"),
        ),
        migrations.AddField(
            model_name="telegramuser",
            name="passport",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="app.passport"),
        ),
        migrations.AddConstraint(
            model_name="bankaccount",
            constraint=models.CheckConstraint(check=models.Q(("balance__gte", 0)), name="check_balance"),
        ),
    ]
