from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, MessageHandler

from app.internal.general.bot.decorators import authorize_user, is_message_defined, is_not_user_in_conversation
from app.internal.general.bot.filters import TEXT
from app.internal.general.bot.handlers import cancel, mark_conversation_end, mark_conversation_start
from app.internal.general.services import user_service
from app.internal.user.presentation.handlers.bot.password.PasswordStates import PasswordStates

_UPDATING_WELCOME = (
    "Обновление пароля...\nВведите секретное слово (регистр не имеет значения), либо /cancel\n\nПодсказка: {tip}"
)
_SECRET_KEY_ERROR = "Неправильное секретной слово. Начните сначала"
_CREATING_WELCOME = "Создание пароля...\nПридумайте секретное слово (регистр не имеет значения), либо /cancel"
_CREATE_TIP = "Придумайте подсказку для секретного слова, либо /cancel"
_INPUT_PASSWORD = "Введите пароль, либо /cancel"
_CONFIRM_PASSWORD = "Введите ещё раз пароль, либо /cancel"
_WRONG_PASSWORD = "Пароль не подтверждён. Начините сначала!"
_UPDATING_SUCCESS = "Пароль успешно обновлён!"
_CREATING_SUCCESS = "Пароль успешно сохранён!"
_SERVER_ERROR = "Произошла неизвестная ошибка!"

_SECRET_KEY_SESSION = "secret_key_hash"
_TIP_SESSION = "tip"
_PASSWORD_SESSION = "password"


@is_message_defined
@authorize_user(phone=False)
@is_not_user_in_conversation
def handle_start(update: Update, context: CallbackContext) -> int:
    mark_conversation_start(context, entry_point.command)

    user = user_service.get_user(update.effective_user.id)

    if user.password:
        update.message.reply_text(_UPDATING_WELCOME.format(tip=user.secret_key.tip))
        return PasswordStates.SECRET_CONFIRMATION

    update.message.reply_text(_CREATING_WELCOME)
    return PasswordStates.SECRET_CREATING


@is_message_defined
def handle_confirmation_secret_key(update: Update, context: CallbackContext) -> int:
    update.message.delete()

    if not user_service.is_secret_key_correct(update.effective_user, update.message.text):
        update.message.reply_text(_SECRET_KEY_ERROR)

        return mark_conversation_end(context)

    update.message.reply_text(_INPUT_PASSWORD)
    return PasswordStates.PASSWORD_ENTERING_IN_UPDATING


@is_message_defined
def handle_entering_in_updating(update: Update, context: CallbackContext) -> int:
    _handle_entering(update, context)

    return PasswordStates.PASSWORD_CONFIRMATION_IN_UPDATING


@is_message_defined
def handle_confirmation_in_updating(update: Update, context: CallbackContext) -> int:
    status = _handle_confirmation(update, context)

    if status == PasswordStates.CONFIRMATION_OK:
        user_service.update_password(update.effective_user, context.user_data[_PASSWORD_SESSION])

        update.message.reply_text(_UPDATING_SUCCESS)

    return mark_conversation_end(context)


@is_message_defined
def handle_saving_secret_key(update: Update, context: CallbackContext) -> int:
    _handle_saving_secret_parameter(update, context, _SECRET_KEY_SESSION, update.message.text, _CREATE_TIP)

    return PasswordStates.TIP_CREATING


@is_message_defined
def handle_saving_tip(update: Update, context: CallbackContext) -> int:
    _handle_saving_secret_parameter(update, context, _TIP_SESSION, update.message.text, _INPUT_PASSWORD)

    return PasswordStates.PASSWORD_ENTERING_IN_CREATING


@is_message_defined
def handle_entering_in_creating(update: Update, context: CallbackContext) -> int:
    _handle_entering(update, context)

    return PasswordStates.PASSWORD_CONFIRMATION_IN_CREATING


@is_message_defined
def handle_confirmation_in_creating(update: Update, context: CallbackContext) -> int:
    status = _handle_confirmation(update, context)

    if status == PasswordStates.CONFIRMATION_OK:
        key: str = context.user_data[_SECRET_KEY_SESSION]
        tip: str = context.user_data[_TIP_SESSION]
        password: str = context.user_data[_PASSWORD_SESSION]

        is_success = user_service.try_create_password(update.effective_user, password, key, tip)

        update.message.reply_text(_CREATING_SUCCESS if is_success else _SERVER_ERROR)

    return mark_conversation_end(context)


def _handle_entering(update: Update, context: CallbackContext):
    update.message.delete()

    context.user_data[_PASSWORD_SESSION] = update.message.text

    update.message.reply_text(_CONFIRM_PASSWORD)


def _handle_confirmation(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    update.message.delete()

    password = context.user_data[_PASSWORD_SESSION]

    if text != password:
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
        PasswordStates.SECRET_CREATING: [MessageHandler(TEXT, handle_saving_secret_key)],
        PasswordStates.TIP_CREATING: [MessageHandler(TEXT, handle_saving_tip)],
        PasswordStates.PASSWORD_ENTERING_IN_CREATING: [MessageHandler(TEXT, handle_entering_in_creating)],
        PasswordStates.PASSWORD_CONFIRMATION_IN_CREATING: [MessageHandler(TEXT, handle_confirmation_in_creating)],
    },
    fallbacks=[cancel],
)
