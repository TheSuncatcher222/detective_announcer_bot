# -*- coding: UTF-8 -*-

import json
from json.decoder import JSONDecodeError
import logging
from time import sleep

import project.data.app_data as app_data # ВЕСЬ??
import project.app_logger as app_logger
from project.app_telegram import (
    check_telegram_bot_response,
    init_telegram_bot)
from project.app_vk import(
    init_vk_bot,
    get_vk_wall_update)


ALL_DATA: tuple[str] = (
    app_data.TELEGRAM_BOT_TOKEN,
    app_data.TELEGRAM_TEAM_CHAT,
    app_data.TELEGRAM_ME,
    app_data.VK_TOKEN_ADMIN,
    app_data.VK_USER_ME,
    app_data.VK_GROUP_TARGET,
    app_data.TEAM_NAME)

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


def main():
    """Main program."""
    logger.info('Program is running.')
    check_env(data=ALL_DATA)
    check_telegram_bot_response(token=app_data.TELEGRAM_BOT_TOKEN)
    vk_bot = init_vk_bot(
        token=app_data.VK_TOKEN_ADMIN, user_id=app_data.VK_USER_ME)
    telegram_bot = init_telegram_bot(token=app_data.TELEGRAM_BOT_TOKEN)
    last_vk_wall_id: int = json_data_read(
        file_name='last_vk_wall_id.json', key='last_vk_wall_id')
    if not last_vk_wall_id:
        last_vk_wall_id = 0
        json_data_write(
            file_name='last_vk_wall_id.json',
            data={'last_vk_wall_id': 0})
    logger.info('Data check succeed. All API are available. Start polling.')
    while 1:
        try:
            logger.info('Try to receive data from VK group wall.')
            update = get_vk_wall_update(
                vk_bot=vk_bot,
                vk_group_id=app_data.VK_GROUP_TARGET,
                last_vk_wall_id=last_vk_wall_id)
        except SystemExit as err:
            """Error in code.
            Program execution is not possible."""
            logger.critical(err)
            raise
        except Exception as err:
            """Error on the API side.
            The program will continue to run normally."""
            last_api_error: str = json_data_read(file_name=last_api_error)
            # if err != last_api_error:
            #     pass
            logger.warning(err)
            pass
        logger.debug(f'Sleep for {app_data.API_UPDATE} sec.')
        sleep(app_data.API_UPDATE)  
        break


if __name__ == '__main__':
    main()
    