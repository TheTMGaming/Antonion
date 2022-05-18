from django.urls import path

from app.internal.transport.rest import ProfileViewSet

urlpatterns = [path("profile/", ProfileViewSet.as_view(), name="me")]
