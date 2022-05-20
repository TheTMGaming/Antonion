from rest_framework.permissions import BasePermissionMetaclass
from rest_framework.request import Request


class IsAuthenticated(metaclass=BasePermissionMetaclass):
    def has_permission(self, request: Request, view) -> bool:
        return hasattr(request, "telegram_user") and request.telegram_user is not None
