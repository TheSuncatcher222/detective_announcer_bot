# -*- coding: UTF-8 -*-

import logging

import app_data # ВЕСЬ??
import app_logger # ВЕСЬ??

from app_telegram import (
    check_telegram_bot_response,
    init_telegram_bot)
from app_vk import(
    init_vk_bot_response)

ALL_DATA = [
    app_data.TELEGRAM_BOT_TOKEN,
    app_data.TELEGRAM_TEAM_CHAT,
    app_data.TELEGRAM_ME,
    app_data.VK_TOKEN_ADMIN,
    app_data.VK_USER_ME,
    app_data.VK_GROUP_TARGET,
    app_data.TEAM_NAME]

logger: logging.Logger = app_logger.get_logger(__name__)


def check_env(data: list) -> None:
    """Checks env data."""
    if not all(data):
        raise SystemExit('Env data is unavaliable!')
    return


def main():
    """Main program."""
    logger.info('Program is running.')
    check_env(data=ALL_DATA)
    check_telegram_bot_response(token=app_data.TELEGRAM_BOT_TOKEN)
    vk_bot = init_vk_bot_response(
        token=app_data.VK_TOKEN_ADMIN, user_id=app_data.VK_USER_ME)
    telegram_bot = init_telegram_bot(token=app_data.TELEGRAM_BOT_TOKEN)
    logger.info('Data check succeed. All API are available.')


if __name__ == '__main__':
    main()
