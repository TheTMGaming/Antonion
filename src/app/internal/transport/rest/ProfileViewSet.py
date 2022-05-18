from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from app.internal.permissions import IsAuthenticated
from app.internal.serializers import ProfileSerializer


class ProfileViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        serializer = ProfileSerializer(request.user)

        return Response(data=serializer.data)
