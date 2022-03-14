from django.contrib.admin import ModelAdmin, register

from app.internal.models.bank import Passport


@register(Passport)
class PassportAdmin(ModelAdmin):
    list_display = ("series", "number", "surname", "name", "birthday", "citizenship", "place_of_birth", "created_at")
    list_display_links = ("series", "number")
