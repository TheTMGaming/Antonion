from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, MessageHandler

from app.internal.bot.decorators import if_update_message_exists, if_user_exist, if_user_is_not_in_conversation
from app.internal.bot.modules.filters import TEXT
from app.internal.bot.modules.general import cancel, mark_conversation_end, mark_conversation_start
from app.internal.bot.modules.user.PasswordStates import PasswordStates
from app.internal.user.db.repositories import SecretKeyRepository, TelegramUserRepository
from app.internal.user.domain.services import TelegramUserService

_INPUT_SECRET_IF_EXISTS = "Введите секретное слово, либо /cancel\n\nПодсказка: {tip}"
_SECRET_KEY_ERROR = "Неправильное секретной слово. Поки"
_INPUT_SECRET_KEY = "Введите секретное слово, либо /cancel"
_CREATE_TIP = "Введите подсказку для секретного слова, либо /cancel"
_INPUT_PASSWORD = "Введите пароль, либо /cancel"
_CONFIRM_PASSWORD = "Введите ещё раз пароль, либо /cancel"
_WRONG_PASSWORD = "Пароль не подтверждён. Начините сначала!"
_UPDATING_SUCCESS = "Пароль успешно обновлён!"
_CREATING_SUCCESS = "Пароль успешно сохранён!"
_SERVER_ERROR = "Произошла неизвестная ошибка!"

_SECRET_KEY_SESSION = "secret_key_hash"
_TIP_SESSION = "tip"
_PASSWORD_SESSION = "password"

_user_service = TelegramUserService(user_repo=TelegramUserRepository(), secret_key_repo=SecretKeyRepository())


@if_update_message_exists
@if_user_exist
@if_user_is_not_in_conversation
def handle_start(update: Update, context: CallbackContext) -> int:
    mark_conversation_start(context, entry_point.command)

    user = _user_service.get_user(update.effective_user.id)

    if user.password is not None:
        update.message.reply_text(_INPUT_SECRET_IF_EXISTS.format(tip=user.secret_key.tip))
        return PasswordStates.SECRET_CONFIRMATION

    update.message.reply_text(_INPUT_SECRET_KEY)
    return PasswordStates.SECRET_CREATING


@if_update_message_exists
def handle_confirmation_secret_key(update: Update, context: CallbackContext) -> int:
    update.message.delete()

    if not _user_service.is_secret_key_correct(update.effective_user, update.message.text):
        update.message.reply_text(_SECRET_KEY_ERROR)

        return mark_conversation_end(context)

    update.message.reply_text(_INPUT_PASSWORD)
    return PasswordStates.PASSWORD_ENTERING_IN_UPDATING


@if_update_message_exists
def handle_entering_in_updating(update: Update, context: CallbackContext) -> int:
    _handle_entering(update, context)

    return PasswordStates.PASSWORD_CONFIRMATION_IN_UPDATING


@if_update_message_exists
def handle_confirmation_in_updating(update: Update, context: CallbackContext) -> int:
    status = _handle_confirmation(update, context)

    if status == PasswordStates.CONFIRMATION_OK:
        is_success = _user_service.try_update_password(update.effective_user, context.user_data[_PASSWORD_SESSION])

        update.message.reply_text(_UPDATING_SUCCESS if is_success else _SERVER_ERROR)

    return mark_conversation_end(context)


@if_update_message_exists
def handle_creating_secret_key(update: Update, context: CallbackContext) -> int:
    _handle_saving_secret_parameter(update, context, _SECRET_KEY_SESSION, update.message.text, _CREATE_TIP)

    return PasswordStates.TIP_CREATING


@if_update_message_exists
def handle_creating_tip(update: Update, context: CallbackContext) -> int:
    _handle_saving_secret_parameter(update, context, _TIP_SESSION, update.message.text, _INPUT_PASSWORD)

    return PasswordStates.PASSWORD_ENTERING_IN_CREATING


@if_update_message_exists
def handle_entering_in_creating(update: Update, context: CallbackContext) -> int:
    _handle_entering(update, context)

    return PasswordStates.PASSWORD_CONFIRMATION_IN_CREATING


@if_update_message_exists
def handle_confirmation_in_creating(update: Update, context: CallbackContext) -> int:
    status = _handle_confirmation(update, context)

    if status == PasswordStates.CONFIRMATION_OK:
        key: str = context.user_data[_SECRET_KEY_SESSION]
        tip: str = context.user_data[_TIP_SESSION]
        password: str = context.user_data[_PASSWORD_SESSION]

        is_success = _user_service.try_create_password(update.effective_user, password, key, tip)

        update.message.reply_text(_CREATING_SUCCESS if is_success else _SERVER_ERROR)

    return mark_conversation_end(context)


def _handle_entering(update: Update, context: CallbackContext):
    update.message.delete()

    context.user_data[_PASSWORD_SESSION] = update.message.text

    update.message.reply_text(_CONFIRM_PASSWORD)


def _handle_confirmation(update: Update, context: CallbackContext) -> int:
    password = context.user_data[_PASSWORD_SESSION]

    if update.message.text != password:
        update.message.reply_text(_WRONG_PASSWORD)

        return mark_conversation_end(context)

    return PasswordStates.CONFIRMATION_OK


def _handle_saving_secret_parameter(
    update: Update, context: CallbackContext, parameter_session: str, value: str, next_message: str
):
    update.message.delete()

    context.user_data[parameter_session] = value

    update.message.reply_text(next_message)


entry_point = CommandHandler("password", handle_start)

password_conversation = ConversationHandler(
    entry_points=[entry_point],
    states={
        PasswordStates.SECRET_CONFIRMATION: [MessageHandler(TEXT, handle_confirmation_secret_key)],
        PasswordStates.PASSWORD_ENTERING_IN_UPDATING: [MessageHandler(TEXT, handle_entering_in_updating)],
        PasswordStates.PASSWORD_CONFIRMATION_IN_UPDATING: [MessageHandler(TEXT, handle_confirmation_in_updating)],
        PasswordStates.SECRET_CREATING: [MessageHandler(TEXT, handle_creating_secret_key)],
        PasswordStates.TIP_CREATING: [MessageHandler(TEXT, handle_creating_tip)],
        PasswordStates.PASSWORD_ENTERING_IN_CREATING: [MessageHandler(TEXT, handle_entering_in_creating)],
        PasswordStates.PASSWORD_CONFIRMATION_IN_CREATING: [MessageHandler(TEXT, handle_confirmation_in_creating)],
    },
    fallbacks=[cancel],
)
