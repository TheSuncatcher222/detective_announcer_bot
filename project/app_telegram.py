from http import HTTPStatus
import logging
import requests
import telegram
from time import sleep

import project.app_logger as app_logger

logger: logging.Logger = app_logger.get_logger(__name__)

def check_telegram_bot_response(token: str) -> None:
    """Проверяет ответ telegram BOT API."""
    response: requests.Response = requests.get(
        f'https://api.telegram.org/bot{token}/getMe')
    status: int = response.status_code
    if status == HTTPStatus.OK:
        return True
    elif status == HTTPStatus.UNAUTHORIZED:
        raise SystemExit('Telegram bot token is invalid!')
    logger.warning(
        f'Telegram API is unavailable with status {status}! '
        'Try to reconnect in 5 minutes.')
    sleep(300)
    check_telegram_bot_response(token=token)


def init_telegram_bot(token: str) -> telegram.Bot:
    return telegram.Bot(token=token)
