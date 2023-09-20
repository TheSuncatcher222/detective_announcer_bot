# -*- coding: UTF-8 -*-

"""
=================
Detective Announcer Bot
=================
The bot is designed to forward posts from the Alibi and Detectit community
walls to a selected Telegram chat/channel, create a more convenient system
for scheduling game days than Telegram can offer, and keep a chat record of
the team's victories.
=================
Author: Svidunovich Kirill
        TheSuncatcher222@gmail.com
        https://github.com/TheSuncatcher222
=================
Project description and instructions:
https://github.com/TheSuncatcher222/detective_announcer_bot
=================
"""

import asyncio
import json
import logging
import os
from telegram.ext import (
    Updater,
    Filters,
    CallbackQueryHandler, CommandHandler, MessageHandler)

from project.data.app_data import (
    InlineKeyboardButton,

    API_TELEGRAM_UPDATE_SEC, API_VK_UPDATE_SEC, LAST_API_ERR_DEL_SEC,
    REPLY_FATHER_MARKUP, REPLY_TO_FORWARD_ABORT_TEXT, REPLY_TO_FORWARD_TEXT,
    SKIP_IF_NOT_IMPORTANT, TOPICS_BLACK_LIST,

    TELEGRAM_BOT_TOKEN, TELEGRAM_TEAM_CHAT, TELEGRAM_USER,
    VK_TOKEN_ADMIN, VK_USER,

    ALIBI, BUTTONS_TEAM_CONFIG_ALIBI, BUTTONS_TEAM_CONFIG_DETECTIT,
    CALLBACK_DATA_NONE,

    API_ERROR_NAME, DATA_FOLDER, SAVED_DATA_JSON_DEFAULT, SAVED_DATA_JSON_NAME,
    TEAM_NAME, TEAM_CAPITAN_PROP,

    GAME_REMINDER_LOOKUP)

import project.app_logger as app_logger

from project.app_telegram import (
    TelegramBot,
    check_telegram_bot_response, delete_message, edit_message,
    init_telegram_bot, form_game_dates_text, rebuild_team_config, send_message,
    send_photo, send_update_message, send_update_wall)

from project.app_vk import (
    VkApi,
    define_message_topic, define_post_topic, get_vk_chat_update_groups,
    get_vk_wall_update_groups, init_vk_bot, parse_message, parse_post,
    update_last_game)

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
    if type(data) is not tuple or len(data) == 0 or not all(data):
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


def saved_data_check(
        saved_data: any = None) -> dict[str, int | dict[str, any]]:
    """Check saved data in json file. if some data is missing - assigns a
    default value to them."""
    if saved_data is None:
        saved_data: any = file_read(
            file_name=f'{DATA_FOLDER}{SAVED_DATA_JSON_NAME}')
    if saved_data is None:
        return SAVED_DATA_JSON_DEFAULT
    for key in (
            'last_alibi_game',
            'last_detectit_game',
            'last_vk_message_id_alibi',
            'last_vk_message_id_detectit',
            'last_vk_wall_id_alibi',
            'last_vk_wall_id_detectit',
            'pinned_telegram_message_id_alibi',
            'pinned_telegram_message_id_detectit',
            'pinned_vk_message_id_alibi',
            'pinned_vk_message_id_detectit',
            'team_config_alibi',
            'team_config_detectit'):
        if key not in saved_data:
            saved_data[key] = SAVED_DATA_JSON_DEFAULT[key]
    for key in ('team_config_alibi', 'team_config_detectit'):
        saved_data[key] = {
            int(num): data for num, data in saved_data[key].items()}
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
    logger.info(f'New message available from {group_name}!')
    topic: str = define_message_topic(message=message['items'][0]['text'])
    if topic:
        logger.info('Sending message update to telegram.')
        parsed_message: str = parse_message(
            group_name=group_name,
            message=message,
            topic=topic)
        send_update_message(
            group_name=group_name,
            message=parsed_message,
            saved_data=saved_data,
            telegram_bot=telegram_bot)
        if topic == GAME_REMINDER_LOOKUP:
            update_last_game(
                group_name=group_name,
                saved_data=saved_data,
                text=message['items'][0]['text'])
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
    logger.info(f'New post available from {group_name}!')
    topic: str = define_post_topic(post=update)
    logger.info(f"Post's topic is: '{topic}'")
    if SKIP_IF_NOT_IMPORTANT and topic not in TOPICS_BLACK_LIST:
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
        file_remove(f'{DATA_FOLDER}{API_ERROR_NAME}')
        await asyncio.sleep(LAST_API_ERR_DEL_SEC)


async def telegram_listener(
        saved_data: dict[str, int | dict[str, any]],
        telegram_bot: TelegramBot) -> None:
    """Use Telegram API for handle callback query from target chat."""

    def __is_from_father(update) -> bool:
        """Return True if from_user.id is TELEGRAM_USER."""
        if update.message is not None:
            return str(update.message.from_user.id) == TELEGRAM_USER
        return None

    def __handle_callback_query(update, context) -> None:
        """Handle callback query. Initialize edit message with query."""
        query: any = update.callback_query
        if query.data == CALLBACK_DATA_NONE:
            return
        username: str = (
            query.from_user.username if query.from_user.username
            else query.from_user.first_name)
        game_num, decision, pref = query.data.split()
        if pref == ALIBI:
            buttons: dict[int, list[list[InlineKeyboardButton]]] = (
                BUTTONS_TEAM_CONFIG_ALIBI)
            key_team_config: str = 'team_config_alibi'
            key_pinned_message_id: str = 'pinned_telegram_message_id_alibi'
        else:
            buttons: dict[int, list[list[InlineKeyboardButton]]] = (
                BUTTONS_TEAM_CONFIG_DETECTIT)
            key_team_config: str = 'team_config_detectit'
            key_pinned_message_id: str = 'pinned_telegram_message_id_detectit'
        saved_data[key_team_config] = rebuild_team_config(
            team_config=saved_data[key_team_config],
            teammate_decision={
                'teammate': username,
                'game_num': int(game_num),
                'decision': int(decision)})
        edit_message(
            bot=telegram_bot,
            keyboard=buttons.get(len(saved_data[key_team_config]) - 1, None),
            message_id=saved_data[key_pinned_message_id],
            new_text=form_game_dates_text(
                group_name=pref,
                team_config=saved_data[key_team_config]))
        return

    def __handle_forward_command(update, context) -> None:
        """Handle "/forward" command. Send confirm message.
        Reply only if user is TELEGRAM_USER."""
        __handle_forward(
            update=update,
            father_forward=True,
            reply_text=REPLY_TO_FORWARD_TEXT)
        return

    def __handle_forward_abort_command(update, context) -> None:
        """Handle "/forward_abort" command. Send confirm message.
        Reply only if user is TELEGRAM_USER."""
        __handle_forward(
            update=update,
            father_forward=False,
            reply_text=REPLY_TO_FORWARD_ABORT_TEXT)
        return

    def __handle_forward(
            update: any,
            father_forward: bool,
            reply_text: str) -> None:
        """Change saved_data['father_forward'] state and make reply."""
        if __is_from_father(update=update):
            saved_data['father_forward'] = father_forward
            update.message.reply_text(
                reply_text,
                reply_markup=REPLY_FATHER_MARKUP)
        return

    def __handle_forward_perform(update, context) -> None:
        """Forward incoming message to TELEGRAM_TEAM_CHAT
        if saved_data['father_forward'] = True.
        Bot's forward method is not used due to the original author's mention.
        Create new message instead.
        Can handle both text and photo messages.
        Delete 3 last messages from father chat (clear command history).
        """
        if (not __is_from_father(update=update) or
                not saved_data.get('father_forward', False)):
            return
        if update.message.photo:
            photos: list = update.message.photo
            largest_photo: dict = max(photos, key=lambda p: p.width)
            file_id: int = largest_photo.file_id
            send_photo(
                bot=telegram_bot,
                photo_id=file_id,
                message=update.message.caption)
        else:
            send_message(
                bot=telegram_bot,
                message=update.message.text)
        message_id: int = update.message.message_id
        for i in range(3):
            delete_message(
                bot=telegram_bot,
                chat_id=TELEGRAM_USER,
                message_id=message_id-i)
        saved_data['father_forward'] = False
        return

    try:
        updater: Updater = Updater(token=TELEGRAM_BOT_TOKEN)
        dispatcher: Updater.dispatcher = updater.dispatcher
        dispatcher.add_handler(
            CallbackQueryHandler(__handle_callback_query))
        dispatcher.add_handler(
            CommandHandler("forward", __handle_forward_command))
        dispatcher.add_handler(
            CommandHandler("forward_abort", __handle_forward_abort_command))
        dispatcher.add_handler(
            MessageHandler(Filters.text | Filters.photo,
                           __handle_forward_perform))
        updater.start_polling(poll_interval=API_TELEGRAM_UPDATE_SEC)
    except Exception as err:
        """Error on the API side.
        The program will continue to run normally."""
        last_api_error: str = file_read(
            file_name=f'{DATA_FOLDER}{API_ERROR_NAME}')
        err_str = f'From telegram_listener: {str(err)}'
        if err_str != last_api_error:
            logger.warning()
            send_message(
                bot=telegram_bot, message=err_str, chat_id=TELEGRAM_USER)
            file_write(
                file_name=f'{DATA_FOLDER}{API_ERROR_NAME}',
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
                file_name=f'{DATA_FOLDER}{API_ERROR_NAME}')
            err_str: str = f'From vk_listener: {str(err)}'
            if err_str != last_api_error:
                logger.warning(err_str)
                send_message(
                    bot=telegram_bot, message=err_str, chat_id=TELEGRAM_USER)
            file_write(
                file_name=f'{DATA_FOLDER}{API_ERROR_NAME}',
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
