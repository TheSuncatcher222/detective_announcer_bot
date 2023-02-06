# -*- coding: UTF-8 -*-

from http import HTTPStatus
import logging
from re import findall
import requests
from requests.exceptions import ConnectionError
import sys
import telegram
from telegram import TelegramError
import vk_api
from vk_api.exceptions import ApiError
from time import sleep


import app_data
import app_logger
import vk_wall_json_example

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

next_game_teammates = 5

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
            'Try to reconnect in 5 minutes.'
        )
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


"""
Функционал на стороне VK API.
"""


def get_vk_wall_update(vk: vk_api.VkApi.method, last_id: int) -> dict:
    """Определяет, есть ли в таргет-группе VK новый пост."""
    post: dict = {}
    try:
        wall: dict = vk.wall.get(
            owner_id=f'-{app_data.VK_GROUP_TARGET}',
            count=2
        )
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
        post_text = ['Вы в белом списке регистрации на эту игру!']
        pdf_text: str = ''
        # https://www.youtube.com/watch?v=RULkvM7AdzY&themeRefresh=1
        # https://pypi.org/project/PyPDF2/
        if app_data.TEAM_NAME in pdf_text:
            post_text = ['Команда уже была на представленной серии игр!']
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
            fixed_text
        )
        post_text += splitted_text[len(splitted_text)-3:len(splitted_text)-2]
    if post_topic == 'checkin' and next_game_teammates >= 4:
        post_text_1 = splitted_text[:1]
        post_text_2 = splitted_text[len(splitted_text)-5:len(splitted_text)-3]
        post_text_3 = [
            'Действует розыгрыш бесплатного входа на всю команду! '
            'Чтобы принять в нем участие, нужно вступить в группу и сделать '
            'репост этой записи:'
        ]
        post_link = [app_data.VK_POST_LINK.format(app_data.VK_GROUP_TARGET, post_id)]
        post_text = post_text_1 + post_text_2 + post_text_3 + post_link
    if post_topic == 'teams':
        post_text = ['🖇Списки команд🖇']
    if post_topic == 'game_results' and app_data.TEAM_NAME in fixed_text:
        post_text = splitted_text[:2]
        post_text += (splitted_text[len(splitted_text)-7:len(splitted_text)-1])
    if post_topic == 'prize_results':
        post_text = splitted_text[:len(splitted_text)-1]
        try:
            response = requests.get(app_data.VK_GROUP_TARGET_LOGO)
        except ConnectionError:
            logger.warning("Post's json from VK wall has unknown structure!")
            logger.error(exc_info=True)
            raise Exception
        if response.status_code != HTTPStatus.OK:
            logger.warning(
                "Post's picture URL is unavaliable with "
                f"status {response.status_code}!")
            raise Exception
        post_image_url = app_data.VK_GROUP_TARGET_LOGO
    if post_topic == 'photos':
        post_text_1 = ['📷 Фотографии 📷']
        post_text_2 = splitted_text[:len(splitted_text)-2]
        post_link = [app_data.VK_POST_LINK.format(app_data.VK_GROUP_TARGET, post_id)]
        post_text = post_text_1 + post_text_2 + post_link
        post_image_url = post['attachments'][0]['album']['thumb']['sizes'][3]['url']
    if post_topic == 'other':
        if '#detectitspb' in splitted_text[len(splitted_text)-1]:
            post_text = splitted_text[:len(splitted_text)-1]
        else:
            post_text = splitted_text
    parsed_post: dict = {
        'post_id': post_id,
        'post_image_url': post_image_url,
        'post_text': post_text,
    }
    if 'game_dates' in locals():
        parsed_post['game_dates'] = game_dates
    return parsed_post


def send_update(telegram_bot: telegram.Bot, parsed_post: dict) -> bool:
    """Отправляет полученные данные с ВК в телеграм."""
    output_text: str = ''
    for paragraph in parsed_post['post_text']:
        output_text += (paragraph + 2*'\n')
    try:
        telegram_bot.send_photo(
            chat_id=app_data.TELEGRAM_ME,
            photo=parsed_post['post_image_url'],
            caption=output_text)
        if 'game_dates' in parsed_post:
            output_text = ''
            for button in parsed_post['game_dates']:
                output_text += (button + '\n')
            telegram_bot.send_message(
                chat_id=app_data.TELEGRAM_ME,
                text=output_text
            )
    except TelegramError:
        text: str = ("Bot can't send the message")
        logger.error(text, exc_info=True)
        raise Exception
    return True


"""
Функционал на стороне TELEGRAM API.
"""


def main():
    """Основная логика работы бота."""
    logger.info('Program is running.')
    check_env(data=ALL_DATA)
    logger.debug('Data check succeed.')
    check_telegram_bot_response(token=app_data.TELEGRAM_BOT_TOKEN)
    logger.debug('Bot is available.')
    vk: vk_api.VkApi.method = check_vk_response(token=app_data.VK_TOKEN_ADMIN)
    logger.debug('VK is available.')
    telegram_bot: telegram.Bot = telegram.Bot(token=app_data.TELEGRAM_BOT_TOKEN)
    # Это надо получать из JSON
    last_vk_wall_id = 0
    logger.info('All check passed successfully! Start polling.')
    while 1:
        try:
            logger.debug('Try to receive data from VK group wall.')
            update = get_vk_wall_update(vk=vk, last_id=last_vk_wall_id)
            # update = vk_wall_json_example.photos
            if update:
                logger.debug('New post available!')
                topic = recognize_post_topic(post=update)
                parsed_post = parse_post(post=update, post_topic=topic)
                if parsed_post['post_text']:
                    send_update(telegram_bot=telegram_bot, parsed_post=parsed_post)
                    logger.info('Message sent!')
            else:
                logger.debug('No updates available.')
        except SystemExit:
            # Отправить сообщение
            sys.exit()
        except Exception:
            # Отправить сообщение
            pass
        logger.debug(f'Sleep for {app_data.API_UPDATE} sec.')
        sleep(app_data.API_UPDATE)
        # break


if __name__ == '__main__':
    main()
