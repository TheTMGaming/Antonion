from logging import NOTSET, Handler, LogRecord
from typing import Union

from telegram import Bot


class TelegramLogHandler(Handler):
    def __init__(self, token: str, chat_id: Union[str, int], level=NOTSET):
        super().__init__(level)

        self.chat_id = chat_id
        self.bot = Bot(token)

    def emit(self, record: LogRecord) -> None:
        self.bot.send_message(chat_id=self.chat_id, text=self.format(record))
