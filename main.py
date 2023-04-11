# -*- coding: UTF-8 -*-

import asyncio
import json
import logging
from telegram.ext import Updater, CallbackQueryHandler

from project.data.app_data import (
    APP_JSON_FOLDER, API_TELEGRAM_UPDATE_SEC, API_VK_UPDATE_SEC, TEAM_CONFIG,
    TEAM_NAME, TELEGRAM_BOT_TOKEN, TELEGRAM_TEAM_CHAT, TELEGRAM_USER,
    VK_TOKEN_ADMIN, VK_USER, VK_GROUP_TARGET)

import project.app_logger as app_logger
from project.app_telegram import (
    check_telegram_bot_response, edit_message, init_telegram_bot,
    rebuild_team_config_game_dates, send_message, send_update)
from project.app_vk import (
    define_post_topic, get_vk_chat_update, get_vk_wall_update, init_vk_bot,
    parse_post)

ALL_DATA: tuple[str, int] = (
    TEAM_NAME,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_TEAM_CHAT,
    TELEGRAM_USER,
    VK_TOKEN_ADMIN,
    VK_USER,
    VK_GROUP_TARGET)

logger: logging.Logger = app_logger.get_logger(__name__)


def check_env(data: list) -> None:
    """Checks env data."""
    if not all(data):
        logger.critical('Env data is empty!')
        raise SystemExit
    return


def json_data_read(
        file_name: str, key: str = None) -> dict[str, any] | None:
    """Read json file and return it's data.
    If there is no file or no given key if data - return 0.
    Optional: return certain value for given key."""
    try:
        with open(f'{APP_JSON_FOLDER}{file_name}') as read_file:
            data: dict[str] = json.load(read_file)
        if key:
            return data[key]
        return data
    except FileNotFoundError:
        logger.info(f"JSON '{file_name}' doesn't exists.")
    except KeyError:
        logger.info(f"JSON doesn't contain key '{key}'.")
    return


def json_data_write(file_name: str, write_data: dict) -> None:
    """Write given data to json file. Create new if not exists."""
    with open(f'{APP_JSON_FOLDER}{file_name}', 'w') as write_file:
        json.dump(write_data, write_file)
    return


async def vk_listener(
        last_vk_message_id: int,
        last_vk_wall_id: int,
        team_config: dict[str, any],
        telegram_bot,
        vk_bot) -> None:
    """Use VK API for checking updates from target VK group.
    If new post available - parse it and sent to target telegram chat."""
    last_api_error: str = None
    while 1:
        try:
            logger.debug('Try to receive data from VK group wall.')
            update_wall: dict[str, any] = get_vk_wall_update(
                last_vk_wall_id=last_vk_wall_id['last_vk_wall_id'],
                vk_bot=vk_bot,
                vk_group_id=VK_GROUP_TARGET)
            if update_wall:
                logger.info('New post available!')
                topic: str = define_post_topic(post=update_wall)
                parsed_post: dict[str, any] = parse_post(
                    post=update_wall, post_topic=topic)
                if parsed_post:
                    if 'post_text' in parsed_post:
                        send_update(
                            parsed_post=parsed_post,
                            team_config=team_config,
                            telegram_bot=telegram_bot)
                        json_data_write(
                            file_name='team_config.json',
                            write_data=team_config)
                    json_data_write(
                        file_name='last_vk_wall_id.json',
                        write_data={'last_vk_wall_id': parsed_post['post_id']})
                    last_vk_wall_id['last_vk_wall_id'] = parsed_post['post_id']
            logger.debug('Try to receive data from VK group chat.')
            update_message: str = get_vk_chat_update(
                last_vk_message_id=last_vk_message_id, vk_bot=vk_bot)
            if update_message:
                logger.info('New message available!')
                send_message(bot=telegram_bot, message=update_message)
                json_data_write(
                    file_name='last_vk_message_id.json',
                    write_data=last_vk_message_id)
        except Exception as err:
            """Error on the API side.
            The program will continue to run normally."""
            last_api_error: str = json_data_read(
                file_name='last_api_error.json')
            err_str: str = str(err)
            if err_str != last_api_error:
                logger.warning(err)
                send_message(
                    bot=telegram_bot, message=err_str, chat_id=TELEGRAM_USER)
        logger.debug(f'vk_listener sleep for {API_VK_UPDATE_SEC} sec.')
        await asyncio.sleep(API_VK_UPDATE_SEC)


async def telegram_listener(team_config: dict, telegram_bot) -> None:
    """Use Telegram API for handle callback query from target chat."""
    def handle_callback_query(update, context) -> None:
        """Handle callback query. Initialize edit message with query."""
        try:
            query: any = update.callback_query
            username: str = (
                query.from_user.username if query.from_user.username
                else query.from_user.first_name)
            game_num, decision = query.data.split()
            rebuild: bool = rebuild_team_config_game_dates(
                team_config=team_config,
                teammate_decision={
                    'teammate': username,
                    'game_num': int(game_num),
                    'decision': int(decision)})
            if rebuild:
                edit_message(
                    bot=telegram_bot,
                    team_config=team_config)
        except Exception as err:
            """Error on the API side.
            The program will continue to run normally."""
            last_api_error: str = json_data_read(
                file_name='last_api_error.json')
            err_str: str = str(err)
            if err_str != last_api_error:
                logger.warning(err)
                send_message(
                    bot=telegram_bot, message=err_str, chat_id=TELEGRAM_USER)
        return

    updater: Updater = Updater(token=TELEGRAM_BOT_TOKEN)
    dispatcher: Updater.dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_callback_query))
    updater.start_polling(poll_interval=API_TELEGRAM_UPDATE_SEC)


async def main():
    """Main program. Manage vk_listener and telegram_listener."""
    try:
        logger.info('Program is running.')
        check_env(data=ALL_DATA)
        check_telegram_bot_response(token=TELEGRAM_BOT_TOKEN)
        vk_bot = init_vk_bot(
            token=VK_TOKEN_ADMIN, user_id=VK_USER)
        telegram_bot = init_telegram_bot(token=TELEGRAM_BOT_TOKEN)
    except SystemExit as err:
        """Error in code. Program execution is not possible."""
        logger.critical(err)
        raise
    last_vk_message_id: dict = json_data_read(
        file_name='last_vk_message_id.json')
    if not last_vk_message_id:
        last_vk_message_id = {'last_vk_message_id': 0}
    last_vk_wall_id: dict = json_data_read(file_name='last_vk_wall_id.json')
    if not last_vk_wall_id:
        last_vk_wall_id = {'last_vk_wall_id': 0}
    team_config: dict = json_data_read(file_name='team_config.json')
    if team_config:
        team_config['game_dates'] = {
            int(num): data for num, data in team_config['game_dates'].items()}
    else:
        team_config = TEAM_CONFIG
    logger.info('All data are available. Start asyncio API polling.')
    task_telegram = asyncio.create_task(
        telegram_listener(team_config=team_config, telegram_bot=telegram_bot))
    task_vk = asyncio.create_task(
        vk_listener(
            last_vk_message_id,
            last_vk_wall_id=last_vk_wall_id,
            team_config=team_config,
            telegram_bot=telegram_bot,
            vk_bot=vk_bot))
    await asyncio.gather(task_telegram, task_vk)


if __name__ == '__main__':
    asyncio.run(main())
