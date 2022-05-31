from ninja import NinjaAPI

from app.internal.authentication.api import add_auth_api
from app.internal.bank.api import add_bank_api
from app.internal.general.exceptions import add_exceptions
from app.internal.user.api import add_friend_api, add_user_api


def get_api() -> NinjaAPI:
    api = NinjaAPI(title="Банк мечты", description="Самый лучший банк из самых лучших банков")

    add_exceptions(api)

    add_auth_api(api)
    add_user_api(api)
    add_friend_api(api)
    add_bank_api(api)

    return api
