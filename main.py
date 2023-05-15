# -*- coding: UTF-8 -*-

import asyncio
import json
import logging
import os
from telegram.ext import Updater, CallbackQueryHandler

from project.data.app_data import (
    InlineKeyboardButton,

    API_TELEGRAM_UPDATE_SEC, API_VK_UPDATE_SEC, LAST_API_ERR_DEL_SEC,

    TELEGRAM_BOT_TOKEN, TELEGRAM_TEAM_CHAT, TELEGRAM_USER,
    VK_TOKEN_ADMIN, VK_USER,

    ALIBI, BUTTONS_TEAM_CONFIG_ALIBI, BUTTONS_TEAM_CONFIG_DETECTIT,

    DATA_FOLDER, SAVED_DATA_JSON_DEFAULT, SAVED_DATA_JSON_NAME,
    TEAM_NAME, TEAM_CAPITAN_PROP)

import project.app_logger as app_logger
from project.app_telegram import (
    TelegramBot,
    check_telegram_bot_response, edit_message, init_telegram_bot,
    form_game_dates_text, rebuild_team_config, send_message,
    send_update_message, send_update_wall)
from project.app_vk import (
    VkApi,
    define_post_topic, get_vk_chat_update_groups, get_vk_wall_update_groups,
    init_vk_bot, parse_message, parse_post)

ALL_DATA: tuple[str, int] = (
    TEAM_CAPITAN_PROP,
    TEAM_NAME,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_TEAM_CHAT,
    TELEGRAM_USER,
    VK_TOKEN_ADMIN,
    VK_USER)

logger: logging.Logger = app_logger.get_logger(__name__)


def check_env(data: tuple[str, int]) -> None:
    """Check env data."""
    if not all(data):
        logger.critical('Env data is not full! Check "project/data/.env"!')
        raise SystemExit
    return


def file_read(file_name: str) -> any or None:
    """Read the file and return it's data. Return None if there is no file."""
    try:
        with open(file_name) as read_file:
            return json.load(read_file)
    except FileNotFoundError:
        logger.info(f"JSON '{file_name}' doesn't exists.")
    return None


def file_write(file_name: str, write_data: any) -> None:
    """Write given data to the file. If the file doesn't exists create new."""
    with open(file_name, 'w') as write_file:
        json.dump(write_data, write_file)
    return


def file_remove(file_name: str) -> None:
    """Delete the file."""
    try:
        os.remove(file_name)
    except FileNotFoundError:
        pass
    return


def saved_data_check() -> dict[str, int | dict[str, any]]:
    """Check saved data in json file. if some data is missing - assigns a
    default value to them."""
    saved_data: any = file_read(
        file_name=f'{DATA_FOLDER}{SAVED_DATA_JSON_NAME}')
    if saved_data is None:
        return SAVED_DATA_JSON_DEFAULT
    for key in (
            'last_vk_message_id_alibi',
            'last_vk_message_id_detectit',
            'last_vk_wall_id_alibi',
            'last_vk_wall_id_detectit',
            'pinned_vk_message_id_alibi',
            'pinned_vk_message_id_detectit',
            'team_config_alibi',
            'team_config_detectit'):
        if key not in saved_data:
            saved_data[key] = SAVED_DATA_JSON_DEFAULT[key]
    for key in ('team_config_alibi', 'team_config_detectit'):
        saved_data[key]['game_dates'] = {
            int(num): data for num, data in saved_data[
                key]['game_dates'].items()}
    return saved_data


def vk_listen_message(
        saved_data: dict[str, int | dict[str, any]],
        telegram_bot: TelegramBot,
        vk_bot: VkApi.method) -> None:
    """Use VK API for checking updates from the VK group chat.
    If an update available - parse it and send to the telegram chat."""
    logger.debug('Try to receive data from VK groups wall.')
    group_name, message = get_vk_chat_update_groups(
        last_message_id_alibi=saved_data['last_vk_message_id_alibi'],
        last_message_id_detectit=saved_data['last_vk_message_id_detectit'],
        vk_bot=vk_bot)
    if not message:
        return
    logger.info('New message available!')
    parsed_message: str = parse_message(group_name=group_name, message=message)
    if parsed_message:
        logger.info('Sending message update to telegram.')
        send_update_message(
            group_name=group_name,
            message=parsed_message,
            saved_data=saved_data,
            telegram_bot=telegram_bot)
    if group_name == ALIBI:
        key_group: str = 'last_vk_message_id_alibi'
    else:
        key_group: str = 'last_vk_message_id_detectit'
    saved_data[key_group] = message['items'][0]['id']
    file_write(
        file_name=f'{DATA_FOLDER}{SAVED_DATA_JSON_NAME}',
        write_data=saved_data)
    logger.info('Done!')
    return


def vk_listen_wall(
        saved_data: dict[str, int | dict[str, any]],
        telegram_bot: TelegramBot,
        vk_bot: VkApi.method) -> None:
    """Use VK API for checking updates from the VK group.
    If an update available - parse it and send to the telegram chat."""
    logger.debug('Try to receive data from VK groups chat.')
    group_name, update = get_vk_wall_update_groups(
        last_wall_id_alibi=saved_data['last_vk_wall_id_alibi'],
        last_wall_id_detectit=saved_data['last_vk_wall_id_detectit'],
        vk_bot=vk_bot)
    if not update:
        return
    logger.info('New post available!')
    topic: str = define_post_topic(post=update)
    logger.info(f"Post's topic is: '{topic}'")
    parsed_post: dict[str, any] = parse_post(
        group_name=group_name,
        post=update,
        post_topic=topic)
    if parsed_post:
        logger.info('Sending wall update to telegram.')
        send_update_wall(
            group_name=group_name,
            parsed_post=parsed_post,
            saved_data=saved_data,
            telegram_bot=telegram_bot)
    if group_name == ALIBI:
        key_group: str = 'last_vk_wall_id_alibi'
    else:
        key_group: str = 'last_vk_wall_id_detectit'
    saved_data[key_group] = update['id']
    file_write(
        file_name=f'{DATA_FOLDER}{SAVED_DATA_JSON_NAME}',
        write_data=saved_data)
    logger.info('Done!')
    return


async def last_api_error_delete() -> None:
    """Delete periodically the file 'last_api_error.json'."""
    while 1:
        file_remove('last_api_error.json')
        await asyncio.sleep(LAST_API_ERR_DEL_SEC)


async def telegram_listener(
        saved_data: dict[str, int | dict[str, any]],
        telegram_bot: TelegramBot) -> None:
    """Use Telegram API for handle callback query from target chat."""

    def __handle_callback_query(update, context) -> None:
        """Handle callback query. Initialize edit message with query."""
        query: any = update.callback_query
        username: str = (
            query.from_user.username if query.from_user.username
            else query.from_user.first_name)
        game_num, decision, pref = query.data.split()
        if pref == 'A':
            buttons: dict[int, list[list[InlineKeyboardButton]]] = (
                BUTTONS_TEAM_CONFIG_ALIBI)
            key_team: str = 'team_config_alibi'
        else:
            buttons: dict[int, list[list[InlineKeyboardButton]]] = (
                BUTTONS_TEAM_CONFIG_DETECTIT)
            key_team: str = 'team_config_detectit'
        saved_data[key_team] = rebuild_team_config(
            team_config=saved_data[key_team],
            teammate_decision={
                'teammate': username,
                'game_num': int(game_num),
                'decision': int(decision)})
        edit_message(
            bot=telegram_bot,
            message_id=saved_data[key_team]['pinned_telegram_message_id'],
            new_text=form_game_dates_text(
                game_dates=saved_data[key_team]['game_dates']),
            reply_markup=buttons.get(
                len(saved_data[key_team]['game_dates']), None))
        return

    try:
        updater: Updater = Updater(token=TELEGRAM_BOT_TOKEN)
        dispatcher: Updater.dispatcher = updater.dispatcher
        dispatcher.add_handler(CallbackQueryHandler(__handle_callback_query))
        updater.start_polling(poll_interval=API_TELEGRAM_UPDATE_SEC)
    except Exception as err:
        """Error on the API side.
        The program will continue to run normally."""
        last_api_error: str = file_read(
            file_name=f'{DATA_FOLDER}last_api_error.json')
        err_str = f'From telegram_listener: {str(err)}'
        if err_str != last_api_error:
            logger.warning()
            send_message(
                bot=telegram_bot, message=err_str, chat_id=TELEGRAM_USER)
            file_write(
                file_name=f'{DATA_FOLDER}last_api_error.json',
                write_data=err_str)


async def vk_listener(
        saved_data: dict[str, int | dict[str, any]],
        telegram_bot: TelegramBot,
        vk_bot: VkApi.method) -> None:
    """Manage checking updates from the VK group wall and chat.
    If an update available - it will be sent to the telegram chat."""
    while 1:
        try:
            vk_listen_message(
                saved_data=saved_data,
                telegram_bot=telegram_bot,
                vk_bot=vk_bot)
            vk_listen_wall(
                saved_data=saved_data,
                telegram_bot=telegram_bot,
                vk_bot=vk_bot)
        except Exception as err:
            """Error on the API side.
            The program will continue to run normally."""
            last_api_error: str = file_read(
                file_name='last_api_error.json')
            err_str: str = f'From vk_listener: {str(err)}'
            if err_str != last_api_error:
                logger.warning(err_str)
                send_message(
                    bot=telegram_bot, message=err_str, chat_id=TELEGRAM_USER)
            file_write(
                file_name='last_api_error.json',
                write_data=err_str)
        logger.debug(f'vk_listener sleep for {API_VK_UPDATE_SEC} sec.')
        await asyncio.sleep(API_VK_UPDATE_SEC)


async def main() -> None:
    """Check initial data. Manage asyncio tasks."""
    try:
        logger.info('Program is running.')
        check_env(data=ALL_DATA)
        check_telegram_bot_response(token=TELEGRAM_BOT_TOKEN)
        vk_bot: VkApi.method = init_vk_bot(
            token=VK_TOKEN_ADMIN, user_id=VK_USER)
        telegram_bot: TelegramBot = init_telegram_bot(
            token=TELEGRAM_BOT_TOKEN)
    except SystemExit as err:
        """Error in data. Program execution is not possible."""
        logger.critical(err)
        raise
    saved_data: dict[str, int | dict[str, any]] = saved_data_check()
    logger.info('All data are available. Start asyncio API polling.')
    task_delete_last_api_error: asyncio.Task[None] = asyncio.create_task(
        last_api_error_delete())
    task_telegram: asyncio.Task[None] = asyncio.create_task(
        telegram_listener(saved_data=saved_data, telegram_bot=telegram_bot))
    task_vk: asyncio.Task[None] = asyncio.create_task(
        vk_listener(
            saved_data=saved_data, telegram_bot=telegram_bot, vk_bot=vk_bot))
    await asyncio.gather(task_delete_last_api_error, task_telegram, task_vk)


if __name__ == '__main__':
    asyncio.run(main())
