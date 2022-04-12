from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt

from app.internal.transport.bot.webhook import BotWebhook

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("app.urls")),
    path("bot/", csrf_exempt(BotWebhook.as_view())),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
