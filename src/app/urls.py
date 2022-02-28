from django.urls import path

from app.internal.transport.rest.handlers import handle_me

urlpatterns = [path("me/<int:user_id>", handle_me)]
