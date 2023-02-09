# -*- coding: UTF-8 -*-

from http import HTTPStatus
import json
from json.decoder import JSONDecodeError
import logging
import os
from PyPDF2 import PdfReader
from re import findall
import requests
import sys
import telegram
from telegram import TelegramError
import vk_api
from vk_api.exceptions import ApiError
from time import sleep

import app_data
import app_logger

logger: logging.Logger = app_logger.get_logger(__name__)

ALL_DATA = [
    app_data.TELEGRAM_BOT_TOKEN,
    app_data.TELEGRAM_TEAM_CHAT,
    app_data.TELEGRAM_ME,
    app_data.VK_TOKEN_ADMIN,
    app_data.VK_USER_ME,
    app_data.VK_GROUP_TARGET,
    app_data.TEAM_NAME
]

"""
Функционал на стороне VK API.
"""


def get_vk_wall_update(vk: vk_api.VkApi.method, last_id: int) -> dict:
    """Определяет, есть ли в таргет-группе VK новый пост."""
    post: dict = {}
    try:
        wall: dict = vk.wall.get(
            owner_id=f'-{app_data.VK_GROUP_TARGET}', count=2)
    except ApiError:
        logger.critical('VK group ID is invalid!')
        raise SystemExit
    for num in (app_data.NON_PINNED_POST, app_data.PINNED_POST):
        try:
            if wall['items'][num]['id'] > last_id:
                post = wall['items'][num]
                break
        except IndexError:
            pass
        except KeyError:
            logger.warning("Post's json from VK wall has unknown structure!")
            logger.error(exc_info=True)
            raise Exception
    return post


def recognize_post_topic(post: dict) -> str:
    """Определяет тематику поста."""
    try:
        post_text: str = post['text']
    except KeyError:
        logger.warning("Post's json from VK wall has unknown structure!")
        logger.error(exc_info=True)
        raise Exception
    for key_tag in app_data.POST_TOPICS:
        if key_tag in post_text:
            return app_data.POST_TOPICS[key_tag]
    return 'other'


def parse_post(post: dict, post_topic: str) -> dict:
    """Производит структурный анализ и разделяет пост на составные части."""
    try:
        post_id: int = post['id']
    except KeyError:
        logger.warning("Post's json from VK wall has unknown structure!")
        logger.error(exc_info=True)
        raise Exception
    post_text: str = None
    if post_topic == 'stop-list':
        try:
            response = requests.get(
                post['attachments'][1]['doc']['url'])
        except Exception:
            logger.warning("Post's json from VK wall has unknown structure!")
            logger.error(exc_info=True)
            raise Exception
        filename = 'stop-list.pdf'
        open(filename, 'wb').write(response.content)
        reader = PdfReader(filename)
        pages_count = len(reader.pages)
        for i in range(pages_count):
            if app_data.TEAM_NAME in reader.pages[i].extract_text():
                post_text = ['Команда уже была на представленной серии игр!']
                break
        os.remove(filename)
    else:
        try:
            unfixed_text: str = post['text']
            if not isinstance(unfixed_text, str):
                raise KeyError
        except KeyError:
            logger.warning("Post's json from VK wall has unknown structure!")
            logger.error(exc_info=True)
            raise Exception
        fixed_text: str = unfixed_text.replace('\n \n', '\n\n')
        fixed_text = fixed_text.replace('\n', '\n\n')
        splitted_text: list = fixed_text.split('\n\n')
        try:
            while 1:
                splitted_text.remove('')
        except ValueError:
            pass
    if post_topic not in ('photos', 'prize_results'):
        try:
            post_image_url = post['attachments'][0]['photo']['sizes'][4]['url']
            if 'http' not in post_image_url:
                raise Exception
        except Exception:
            logger.warning("Post's json from VK wall has unknown structure!")
            logger.error(exc_info=True)
            raise Exception
    if post_topic == 'preview':
        post_text = splitted_text[:3]
        game_dates: list = findall(
            r'\d+\s\w+,\s\d+\:\d+\s\—\s\w+\s\w+\s\w+\s\w+',
            fixed_text)
        post_text += splitted_text[len(splitted_text)-3:len(splitted_text)-2]
    if post_topic == 'checkin':
        post_text_1 = splitted_text[:1]
        post_text_2 = splitted_text[len(splitted_text)-5:len(splitted_text)-3]
        post_text_3 = [
            'Действует розыгрыш бесплатного входа на всю команду! '
            'Чтобы принять в нем участие, нужно вступить в группу и сделать '
            'репост этой записи:']
        post_link = [app_data.VK_POST_LINK.format(
            app_data.VK_GROUP_TARGET, post_id)]
        post_text = post_text_1 + post_text_2 + post_text_3 + post_link
    if post_topic == 'teams':
        post_text = ['🖇Списки команд🖇']
    if post_topic == 'game_results' and app_data.TEAM_NAME in fixed_text:
        post_text = splitted_text[:2]
        post_text += (splitted_text[len(splitted_text)-7:len(splitted_text)-1])
        for paragraph, medal in app_data.MEDALS.items():
            if app_data.TEAM_NAME in post_text[paragraph]:
                post_text += medal
                break
    if post_topic == 'prize_results':
        post_text = splitted_text[:len(splitted_text)-1]
        response = requests.get(app_data.VK_GROUP_TARGET_LOGO)
        if response.status_code != HTTPStatus.OK:
            logger.warning(
                "Group main picture URL is unavaliable with "
                f"status {response.status_code}!")
            raise Exception
        post_image_url = app_data.VK_GROUP_TARGET_LOGO
    if post_topic == 'photos':
        post_text_1 = ['📷 Фотографии 📷']
        post_text_2 = splitted_text[:len(splitted_text)-2]
        post_link = [
            app_data.VK_POST_LINK.format(app_data.VK_GROUP_TARGET, post_id)]
        post_text = post_text_1 + post_text_2 + post_link
        post_image_url = (
            post['attachments'][0]['album']['thumb']['sizes'][3]['url'])
    if post_topic == 'other':
        if '#detectitspb' in splitted_text[len(splitted_text)-1]:
            post_text = splitted_text[:len(splitted_text)-1]
        else:
            post_text = splitted_text
    parsed_post: dict[str, any] = {
        'post_id': post_id,
        'post_image_url': post_image_url,
        'post_text': post_text}
    if 'game_dates' in locals():
        parsed_post['game_dates'] = game_dates
    return parsed_post


def send_update(telegram_bot: telegram.Bot, parsed_post: dict) -> True:
    """Отправляет полученные данные с ВК в телеграм чат."""
    if not parsed_post['post_text']:
        return True
    output_text: str = ''
    for paragraph in parsed_post['post_text']:
        output_text += (paragraph + 2*'\n')
    try:
        telegram_bot.send_photo(
            chat_id=app_data.TELEGRAM_ME,
            photo=parsed_post['post_image_url'],
            caption=output_text)
        if 'game_dates' in parsed_post:
            send_message_dates(game_dates = parsed_post['game_dates'])
    except TelegramError:
        text: str = ("Bot can't send the message")
        logger.error(text, exc_info=True)
        raise Exception
    return True


"""
Функционал на стороне TELEGRAM API.
"""


def send_message_dates(game_dates: list, message_id: int = None):
    """
    Отправляет сообщение с датами игр и участниками.
    Если указан message_id - редактирует раннее отправленное сообщение.
    """
    print(game_dates)


def send_message(bot: telegram.Bot, message: str) -> True:
    """Отправляет сообщение в Telegram."""
    try:
        logger.debug('Bot try to sent message.')
        bot.send_message(
            chat_id=app_data.TELEGRAM_TEAM_CHAT,
            text=message
        )
    except TelegramError:
        text: str = ("Bot can't send the message")
        logger.error(text, exc_info=True)
    logger.debug('Message sent.')
    return True


"""
Общий функционал.
"""


def check_env(data: list) -> None:
    """Проверяет доступность переменных окружения."""
    if not all(data):
        raise SystemExit


def check_telegram_bot_response(token: str) -> None:
    """Проверяет ответ telegram BOT API."""
    response: requests.Response = requests.get(
        f'https://api.telegram.org/bot{token}/getMe')
    status: int = response.status_code
    if status == HTTPStatus.OK:
        return
    if status == HTTPStatus.UNAUTHORIZED:
        logger.critical('Telegram bot token is invalid!')
        raise SystemExit
    else:
        logger.warning(
            f'Telegram API is unavailable with status {status}! '
            'Try to reconnect in 5 minutes.')
        sleep(300)
        check_telegram_bot_response(token=token)


def check_vk_response(token: str) -> vk_api.VkApi.method:
    """Проверяет доступность методов VK API. Создает сессию."""
    session: vk_api.VkApi = vk_api.VkApi(token=token)
    vk: vk_api.VkApi.method = session.get_api()
    try:
        vk.status.get(user_id=app_data.VK_USER_ME)
    except vk_api.exceptions.ApiError:
        logger.critical('VK is unavailable! Invalid token!')
        raise SystemExit
    return vk


def json_data_read(file_name: str, key: str):
    try:
        with open(file_name) as read_file:
            data = json.load(read_file)
            return data[key]
    except FileNotFoundError:
        logger.info(f"JSON '{file_name}' doesn't exists. Creating new one.")
    except JSONDecodeError:
        logger.info(f"JSON doesn't contain key '{key}'")
    return None


def json_data_write(file_name: str, data: dict):
    with open(file_name, 'w') as write_file:
        json.dump(data, write_file)


def main():
    """Основная логика работы бота."""
    logger.info('Program is running.')
    check_env(data=ALL_DATA)
    logger.debug('Data check succeed.')
    check_telegram_bot_response(token=app_data.TELEGRAM_BOT_TOKEN)
    logger.debug('Bot is available.')
    vk: vk_api.VkApi.method = check_vk_response(token=app_data.VK_TOKEN_ADMIN)
    logger.debug('VK is available.')
    telegram_bot: telegram.Bot = telegram.Bot(
        token=app_data.TELEGRAM_BOT_TOKEN)
    last_vk_wall_id = json_data_read(
        file_name='last_vk_wall_id.json',
        key='last_vk_wall_id')
    if not last_vk_wall_id:
        last_vk_wall_id = 0
        json_data_write(
            file_name='last_vk_wall_id.json',
            data={'last_vk_wall_id': 0})
    logger.info('All check passed successfully! Start polling.')
    while 1:
        try:
            logger.debug('Try to receive data from VK group wall.')
            update = get_vk_wall_update(vk=vk, last_id=last_vk_wall_id)
            import vk_wall_json_example
            update = vk_wall_json_example.preview
            if update:
                logger.info('New post available!')
                topic = recognize_post_topic(post=update)
                parsed_post = parse_post(post=update, post_topic=topic)
                message: bool = send_update(
                    telegram_bot=telegram_bot,
                    parsed_post=parsed_post)
                if message:
                    logger.info('Sending update complete!')
                    last_vk_wall_id = parsed_post['post_id']
                    json_data_write(
                        file_name='last_vk_wall_id.json',
                        data={'last_vk_wall_id': last_vk_wall_id})
            else:
                logger.debug('No updates available.')
        except SystemExit:
            sys.exit()
        except Exception:
            pass
        logger.debug(f'Sleep for {app_data.API_UPDATE} sec.')
        sleep(app_data.API_UPDATE)
        sys.exit()


if __name__ == '__main__':
    main()
