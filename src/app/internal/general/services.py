from app.internal.authentication.db.repositories import AuthRepository
from app.internal.authentication.domain.services import JWTService
from app.internal.bank.db.repositories import BankAccountRepository, BankCardRepository, TransactionRepository
from app.internal.bank.domain.services import BankObjectService, TransactionService, TransferService
from app.internal.user.db.repositories import FriendRequestRepository, SecretKeyRepository, TelegramUserRepository
from app.internal.user.domain.services import FriendRequestService, FriendService, TelegramUserService

_user_repo = TelegramUserRepository()
_secret_repo = SecretKeyRepository()
_account_repo = BankAccountRepository()
_card_repo = BankCardRepository()
_transaction_repo = TransactionRepository()
_request_repo = FriendRequestRepository()

user_service = TelegramUserService(_user_repo, _secret_repo)
friend_service = FriendService(friend_repo=_user_repo)
request_service = FriendRequestService(_request_repo)
bank_object_service = BankObjectService(_account_repo, _card_repo)
transfer_service = TransferService(_account_repo, _card_repo, _transaction_repo)
transaction_service = TransactionService(_transaction_repo)
auth_service = JWTService(auth_repo=AuthRepository(), user_repo=TelegramUserRepository())
