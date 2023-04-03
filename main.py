# -*- coding: UTF-8 -*-

import json
from json.decoder import JSONDecodeError
import logging
# from telegram.ext import CommandHandler
# from telegram.ext import MessageHandler
# from telegram.ext import Updater
from time import sleep

from project.data.app_data import (
    API_TELEGRAM_UPDATE_SEC,
    API_VK_UPDATE_SEC,
    DATE_HEADLIGHT,
    EMOJI_NUMBERS,
    TEAM_NAME,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_TEAM_CHAT,
    TELEGRAM_USER,
    VK_TOKEN_ADMIN,
    VK_USER,
    VK_GROUP_TARGET
)
import project.app_logger as app_logger
from project.app_telegram import (
    check_telegram_bot_response,
    init_telegram_bot,
    send_update)
from project.app_vk import (
    define_post_topic,
    get_vk_wall_update,
    init_vk_bot,
    parse_post)

ALL_DATA: tuple[str] = (
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


def json_data_read(file_name: str, key: str = None) -> any:
    """Read json file and return it's data.
    Optional: return certain value for given key."""
    try:
        with open(file_name) as read_file:
            data: dict[str] = json.load(read_file)
        if key:
            return data[key]
        return data
    except FileNotFoundError:
        logger.info(f"JSON '{file_name}' doesn't exists.")
    except JSONDecodeError:
        logger.info(f"JSON doesn't contain key '{key}'.")
    return


def json_data_write(file_name: str, data: dict) -> None:
    """Write given data to json file."""
    with open(file_name, 'w') as write_file:
        json.dump(data, write_file)
    return


def get_game_dates_json(data: dict) -> str:
    """Преобразует записи из game_dates.json в текстовое сообщение."""
    message: str = ''
    for game in data['games'].values():
        message += (game['date'] + str(game['total_teammates']) + '\n')
        for teammate in game['teammates']:
            message += 'teammate' + '\n'
            i = 1
            while i != game['teammates']['teammate']:
                message += f'{teammate} (гость)' + '\n'
    return message


def rebuild_game_dates_json(
        game_num: int = None,
        teammate: int = None,
        teammate_action: int = None,
        message_id: int = None,
        new_game: list = None
        ) -> dict:
    """Направляет запрос на перезапись данных в game_dates.json.
    При получении номера игры и id участника или получении id сообщения:
    перезапись существующих данных. При получении данных о новой игре:
    формирование новых данных (количество и описание игровых дней).
    """
    if new_game is None:
        file_name: str = 'game_dates.json'
        data: dict[str] = json_data_read(file_name=file_name)
        if data is None:
            raise SystemExit(f'{file_name} is damaged and must be checked!')
    if all((game_num, teammate, teammate_action)):
        if teammate_action not in (-1, 1):
            raise SystemExit(
                f"Teammate action has wrong data! Got '{teammate_action}', but"
                "'-1' or '1' expected.")
        selected_game = data['games'][str(game_num)]
        if str(teammate) not in selected_game['teammates']:
            if teammate_action == -1:
                return
            elif teammate_action == 1:
                selected_game['teammates'][str(teammate)] = 1
                selected_game['total_teammates'] += 1
        else:
            if teammate_action == 1:
                selected_game['teammates'][str(teammate)] += 1
                selected_game['total_teammates'] += 1
            else:
                teammate_current = selected_game['teammates'][str(teammate)]
                if teammate_current <= 1:
                    del selected_game['teammates'][str(teammate)]
                    selected_game['total_teammates'] -= 1
                else:
                    selected_game['teammates'][str(teammate)] -= 1
                    selected_game['total_teammates'] -= 1
        data['games'][str(game_num)] = selected_game
    elif message_id:
        data['message_id'] = message_id
    elif new_game:
        count: str = 0
        data = {
            'message_id': None,
            'games': {}}
        for date in new_game:
            count += 1
            date_split = date.split(' — ')
            date = DATE_HEADLIGHT.format(
                number=EMOJI_NUMBERS[count],
                date=date_split[0],
                location=date_split[1],
                count=0)
            data['games'][count] = {
                'total_teammates': 0,
                'date': date,
                'teammates': {}}
    else:
        raise SystemExit(
            'Something is wrong with input data in rebuild_game_dates_json!'
            f'Got: game_num = {game_num}, teammate = {teammate}, '
            f'teammate_action = {teammate_action}, message_id = {message_id}, '
            f'new_game = {new_game}')
    return data


def vk_listener(last_vk_wall_id: int, telegram_bot, vk_bot) -> None:
    """."""
    logger.info('Try to receive data from VK group wall.')
    update = get_vk_wall_update(
        vk_bot=vk_bot,
        vk_group_id=VK_GROUP_TARGET,
        last_vk_wall_id=last_vk_wall_id)
    if update:
        logger.info('New post available!')
        topic = define_post_topic(post=update)
        parsed_post = parse_post(post=update, post_topic=topic)
        send_update(telegram_bot=telegram_bot, parsed_post=parsed_post)
        json_data_write(
            file_name='last_vk_wall_id.json',
            data={'last_vk_wall_id': parsed_post['post_id']})
    logger.debug(f'vk_listener sleep for {API_VK_UPDATE_SEC} sec.')
    sleep(API_VK_UPDATE_SEC)
    return


def telegram_listener() -> None:
    sleep(API_TELEGRAM_UPDATE_SEC)
    pass


def main():
    """Main program."""
    logger.info('Program is running.')
    check_env(data=ALL_DATA)
    check_telegram_bot_response(token=TELEGRAM_BOT_TOKEN)
    vk_bot = init_vk_bot(
        token=VK_TOKEN_ADMIN, user_id=VK_USER)
    telegram_bot = init_telegram_bot(token=TELEGRAM_BOT_TOKEN)
    last_vk_wall_id: int = json_data_read(
        file_name='last_vk_wall_id.json', key='last_vk_wall_id')
    if not last_vk_wall_id:
        last_vk_wall_id = 0
        json_data_write(
            file_name='last_vk_wall_id.json',
            data={'last_vk_wall_id': 0})
    # updater = Updater(token=app_data.TELEGRAM_BOT_TOKEN)
    # dispatcher = updater.dispatcher
    # dispatcher.add_handler(CommandHandler(
    #     'start', send_message(bot=telegram_bot, message='Привет!'))
    logger.info('Data check succeed. All API are available. Start polling.')
    while 1:
        try:
            vk_listener(
                last_vk_wall_id=last_vk_wall_id,
                telegram_bot=telegram_bot,
                vk_bot=vk_bot)
            telegram_listener()
        except SystemExit as err:
            """Error in code.
            Program execution is not possible."""
            logger.critical(err)
            raise
        except Exception as err:
            """Error on the API side.
            The program will continue to run normally."""
            # last_api_error: str = json_data_read(file_name=last_api_error)
            # if err != last_api_error:
            #     pass
            logger.warning(err)
            pass
        break


if __name__ == '__main__':
    main()
