from django.db.models import QuerySet
from telegram import User

from app.internal.users.domain.interfaces import IFriendRequestRepository


class FriendRequestBotService:
    def __init__(self, request_repo: IFriendRequestRepository):
        self._request_repo = request_repo

    def get_usernames_to_friends(self, user: User) -> QuerySet[str]:
        return self._request_repo.get_usernames_to_friends(user.id)
