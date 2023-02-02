from http import HTTPStatus
import logging
import requests
import sys
import telegram
import vk_api

import app_data
import app_logger

logger: logging.Logger = app_logger.get_logger(__name__)

ALL_TOKENS = [
    app_data.TELEGRAM_BOT_TOKEN,
    app_data.VK_TOKEN,
    app_data.VK_USER_ME,
    app_data.VK_CHAT_TARGET,
    app_data.VK_GROUP_TARGET,
]


def check_tokens(tokens: list) -> None:
    """Проверяет доступность токенов."""
    logger.debug('Try to check the availability of tokens.')
    if all(tokens):
        logger.debug('Tokens check succeed.')
        return
    logger.critical(f'Tokens check failed!')
    sys.exit()


def check_telegram_bot_response(token: str) -> None:
    """Проверяет ответ TELEGRAM BOT API."""
    logger.debug('Try to connect to telegram API with given token')
    response: requests.Response = requests.get(
        f'https://api.telegram.org/bot{token}/getMe')
    status: int = response.status_code
    if status == HTTPStatus.OK:
        logger.debug('Bot is available.')
        return
    if status == HTTPStatus.UNAUTHORIZED:
        logger.critical(f'Bot is unavailable! Invalid token!')
    else:
        logger.warning(f'Telegram API is unavailable!')
    sys.exit()


def check_vk_response(token: str) -> vk_api.VkApi.method:
    """Проверяет доступность методов VK API."""
    session: vk_api.VkApi = vk_api.VkApi(token=token)
    vk: vk_api.VkApi.method = session.get_api()
    try:
        vk.status.get(user_id=app_data.VK_USER_ME)
    except vk_api.exceptions.ApiError:
        logger.critical(f'VK is unavailable! Invalid token!')
        sys.exit()
    return vk


def main():
    """Основная логика работы бота."""
    logger.info('Program is running.')
    check_tokens(tokens=ALL_TOKENS)
    check_telegram_bot_response(token=app_data.TELEGRAM_BOT_TOKEN)
    vk: vk_api.VkApi.method = check_vk_response(token=app_data.VK_TOKEN)
    telegram_bot: telegram.Bot = telegram.Bot(token=app_data.TELEGRAM_BOT_TOKEN)
    logger.info('All check passed successfully!')


if __name__ == '__main__':
    main()
