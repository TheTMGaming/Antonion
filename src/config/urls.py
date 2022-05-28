import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt

from app.internal.api import get_api
from app.internal.bot.webhook import BotWebhook

api = get_api()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("bot/", csrf_exempt(BotWebhook.as_view())),
    path("__debug__/", include(debug_toolbar.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
