from django.urls import path

from app.internal.transport.rest import UserDetailsView

urlpatterns = [path("me/<int:user_id>", UserDetailsView.as_view(), name="me")]
