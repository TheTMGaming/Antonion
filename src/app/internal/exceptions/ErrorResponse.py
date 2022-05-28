from abc import ABC, abstractmethod

from django.http import HttpRequest
from ninja import NinjaAPI, Schema


class ErrorResponse(Schema, ABC):
    error: str

    @staticmethod
    @abstractmethod
    def message() -> str:
        pass

    @staticmethod
    @abstractmethod
    def status() -> int:
        pass

    @staticmethod
    def create(api: NinjaAPI, request: HttpRequest, exc):
        return api.create_response(request, data={"error": ErrorResponse.message()}, status=ErrorResponse.status())
