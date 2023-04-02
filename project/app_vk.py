from datetime import datetime
from http import HTTPStatus
import os
from PyPDF2 import PdfReader
from re import findall
import requests
from telegram import TelegramError
import vk_api
from vk_api.exceptions import ApiError

from data.app_data import(
    LOCATIONS,
    MEDALS,
    MONTHS,
    NON_PINNED_POST_ID,
    PINNED_POST_ID,
    POST_TOPICS,
    TEAM_NAME,
    TELEGRAM_USER,
    VK_GROUP_TARGET,
    VK_GROUP_TARGET_HASHTAG,
    VK_GROUP_TARGET_LOGO,
    VK_POST_LINK,
    WEEKDAYS)

# import json
# from json.decoder import JSONDecodeError

# import sys
# 
# 
# from telegram.ext import CommandHandler
# from telegram.ext import MessageHandler
# from telegram.ext import Updater


def init_vk_bot(token: str, user_id: int) -> any:
    """Check VK API. Create a session."""
    session = vk_api.VkApi(token=token)
    vk = session.get_api()
    try:
        vk.status.get(user_id=user_id)
    except vk_api.exceptions.ApiError:
        raise SystemExit('VK token is invalid!')
    return vk


def get_vk_wall_update(
        vk_bot: vk_api.VkApi.method,
        vk_group_id: int,
        last_vk_wall_id: int) -> dict:
    """Check for a new post in VK group."""
    try:
        wall: dict = vk_bot.wall.get(
            owner_id=f'-{vk_group_id}', count=2)
    except ApiError:
        raise SystemExit('VK group ID is invalid!')
    update: dict = {}
    for num in (NON_PINNED_POST_ID, PINNED_POST_ID):
        try:
            if wall['items'][num]['id'] > last_vk_wall_id:
                update = wall['items'][num]
                break
        except IndexError:
            pass
        except KeyError:
            raise Exception(
                "Post's json from VK wall has unknown structure!"
                f"Try ['items'][{num}]['id'].")
    # Может сразу убрать из поста лишнее, чтобы не гонять туда-сюда?
    return update


def define_post_topic(post: dict) -> str:
    """Define the topic of the given post."""
    # Возможно стоит прямо тут текст и разобрать на составные части?
    try:
        post_text: str = post['text']
    except KeyError:
        raise Exception(
            "Post's json from VK wall has unknown structure!"
            "Try ['items'][0]['text'].")
    # оптимизация: нам же не весь текст нужен?
    for key_tag in POST_TOPICS:
        if key_tag in post_text:
            return POST_TOPICS[key_tag]
    return 'other'


def game_dates_add_weekday(game_dates: list) -> list:
    """Добавляет к входящим датам день недели."""
    now = datetime.now()
    now_month = now.month
    now_year = now.year
    dates_with_weekday = []
    for date in game_dates:
        date_split = date.split(' — ')
        date_time, location = date_split[0], LOCATIONS[date_split[1]]
        date_time_split = date_time.split(', ')
        date = date_time_split[0].split(' ')  # Возможно я тут сломал, скобки были пустые
        month = MONTHS[date[1]]
        if month >= now_month:
            year = now_year
        else:
            year = now_year + 1
        weekday = datetime(year, month, int(date[0])).weekday()
        dates_with_weekday.append(
            f'{date_time} ({WEEKDAYS[weekday]}) — {location}')
    return dates_with_weekday


def fix_post_text(text: str) -> list:
    """."""
    unfixed_text: str = text
    fixed_text: str = unfixed_text.replace('\n \n', '\n\n')
    fixed_text = fixed_text.replace('\n', '\n\n')
    splitted_text: list = fixed_text.split('\n\n')
    try:
        while 1:
            splitted_text.remove('')
    except ValueError:
        pass
    return fixed_text, splitted_text


def get_post_image_url(post: dict, block: str):
    """."""
    try:
        if block == 'photo':
            post_image_url = (
                post['attachments'][0]['photo']['sizes'][4]['url'])
        elif block == 'album':
            post_image_url = (
                post['attachments'][0]['album']['thumb']['sizes'][3]['url'])
        if 'http' not in post_image_url:
            raise ValueError
    except ValueError:
        raise Exception(
            "Post's json from VK wall has unknown structure!"
            "Try ['items'][0]['attachments'][0]['photo']['sizes'][4]"
            "['url']: data does not contain 'http' link.")
    return post_image_url


def parse_post_stop_list(post: dict):
    """."""
    try:
        response = requests.get(post['attachments'][1]['doc']['url'])
    except Exception:
        raise Exception(
            "Post's json from VK wall has unknown structure!"
            "Try ['items'][0]['attachments'][1]['doc']['url'].")
    filename = 'stop-list.pdf'
    open(filename, 'wb').write(response.content)
    reader = PdfReader(filename)
    for i in range(len(reader.pages)):
        if TEAM_NAME in reader.pages[i].extract_text():
            return ['Команда уже была на представленной серии игр!']
    os.remove(filename)
    return ['Команда допущена к регистрации на представленную серию игр!']


def parse_post_preview(fixed_text: str, splitted_text: list):
    """."""
    post_text = splitted_text[:3]
    game_dates: list = findall(
        r'\d+\s\w+,\s\d+\:\d+\s\—\s\w+\s\w+\s\w+\s\w+',
        fixed_text)
    game_dates = game_dates_add_weekday(game_dates=game_dates)
    post_text += splitted_text[len(splitted_text)-3:len(splitted_text)-2]
    return post_text


def parse_post_checkin(splitted_text: str, post_id: int):
    """."""
    post_text_1 = splitted_text[:1]
    post_text_2 = splitted_text[len(splitted_text)-5:len(splitted_text)-3]
    post_text_3 = [
        'Действует розыгрыш бесплатного входа на всю команду! '
        'Чтобы принять в нем участие, нужно вступить в группу и сделать '
        'репост этой записи:']
    post_link = [VK_POST_LINK.format(VK_GROUP_TARGET, post_id)]
    post_text = post_text_1 + post_text_2 + post_text_3 + post_link
    return post_text


def parse_post_game_results(splitted_text: str):
    """."""
    post_text = splitted_text[:2]
    post_text += (splitted_text[len(splitted_text)-7:len(splitted_text)-1])
    for paragraph, medal in MEDALS.items():
        if TEAM_NAME in post_text[paragraph]:
            post_text += medal
            break
    return post_text


def parse_post_photos(splitted_text: list, post_id: int):
    """."""
    post_text_1 = ['📷 Фотографии 📷']
    post_text_2 = splitted_text[:len(splitted_text)-2]
    post_link = [VK_POST_LINK.format(VK_GROUP_TARGET, post_id)]
    post_text = post_text_1 + post_text_2 + post_link
    return post_text


def parse_post_other(splitted_text):
    """."""
    if VK_GROUP_TARGET_HASHTAG in splitted_text[len(splitted_text)-1]:
        post_text = splitted_text[:len(splitted_text)-1]
    else:
        post_text = splitted_text
    return post_text


def parse_post(post: dict, post_topic: str) -> dict:
    """Производит структурный анализ и разделяет пост на составные части."""
    post_id: int = post['id']
    post_text: str = None
    post_image_url: str = None
    game_dates: list = None
    if post_topic == 'stop-list':
        post_text = parse_post_stop_list(post=post, post_id=post_id)
    else:
        fixed_text, splitted_text = fix_post_text(text=post['text'])
    if post_topic == 'preview':
        post_text = parse_post_preview(
            fixed_text=fixed_text, splitted_text=splitted_text)
    elif post_topic == 'checkin':
        post_text = parse_post_checkin(splitted_text=splitted_text)
    elif post_topic == 'teams':
        post_text = ['Списки команд']
    elif post_topic == 'game_results' and TEAM_NAME in fixed_text:
        post_text = parse_post_game_results(splitted_text=splitted_text)
    elif post_topic == 'prize_results':
        post_text = splitted_text[:len(splitted_text)-1]
    elif post_topic == 'photos':
        post_text = parse_post_photos(
            splitted_text=splitted_text, post_id=post_id)
    elif post_topic == 'other':
        post_text = parse_post_other(splitted_text=splitted_text)
    if post_topic == 'prize_results':
        response = requests.get(VK_GROUP_TARGET_LOGO)
        if response.status_code != HTTPStatus.OK:
            raise Exception(
                'Group main picture URL is unavaliable with '
                f'status: {response.status_code}!')
        else:
            post_image_url = VK_GROUP_TARGET_LOGO
    elif post_topic == 'photos':
        post_image_url = get_post_image_url(post=post, block='album')
    else:
        post_image_url = get_post_image_url(post=post, block='photo')
    parsed_post: dict[str, any] = {
        'post_id': post_id,
        'post_image_url': post_image_url,
        'post_text': post_text}
    if 'game_dates':
        parsed_post['game_dates'] = game_dates
    return parsed_post


def send_message(bot, message: str) -> None:
    """Отправляет сообщение в Telegram."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_USER,
            text=message)
    except TelegramError:
        raise Exception("Bot can't send the message!")
    return


def send_update(telegram_bot, parsed_post: dict) -> True:
    """Отправляет полученные данные с ВК в телеграм чат."""
    if not parsed_post['post_text']:
        return True
    output_text: str = ''
    for paragraph in parsed_post['post_text']:
        output_text += (paragraph + 2*'\n')
    try:
        telegram_bot.send_photo(
            chat_id=TELEGRAM_USER,
            photo=parsed_post['post_image_url'],
            caption=output_text)
        if 'game_dates' in parsed_post:
            game_dates = rebuild_game_dates_json(
                new_game=parsed_post['game_dates'])
            game_dates_message = get_game_dates_json(data=game_dates)
            send_message(
                bot=telegram_bot, message=game_dates_message)
    except TelegramError as err:
        raise Exception(f"Bot can't send the message! Error message: {err}")
    return True


# def get_game_dates_json(data: dict) -> str:
#     """Преобразует записи из game_dates.json в текстовое сообщение."""
#     message: str = ''
#     for game in data['games'].values():
#         message += (game['date'] + str(game['total_teammates']) + '\n')
#         for teammate in game['teammates']:
#             message += 'teammate' + '\n'
#             i = 1
#             while i != game['teammates']['teammate']:
#                 message += f'{teammate} (гость)' + '\n'
#     return message
            

# def rebuild_game_dates_json(
#     game_num: int = None,
#     teammate: int = None,
#     teammate_action: int = None,
#     message_id: int = None,
#     new_game = None) -> dict:
#     """Направляет запрос на перезапись данных в game_dates.json.
#     При получении номера игры и id участника или получении id сообщения:
#     перезапись существующих данных. При получении данных о новой игре:
#     формирование новых данных (количество и описание доступных игровых дней).
#     """
#     if new_game is None:
#         file_name = 'game_dates.json'
#         data = json_data_read(file_name=file_name)
#         if data is None:
#             raise SystemExit(
#                 f'{file_name} is damaged and must be checked!')
#     if all((game_num, teammate, teammate_action)):
#         if teammate_action not in (-1, 1):
#             raise SystemExit(
#                 f"Teammate action has wrong data! Got '{teammate_action}', but"
#                 "'-1' or '1' expected.")
#         selected_game = data['games'][str(game_num)]
#         if str(teammate) not in selected_game['teammates']:
#             if teammate_action == -1:
#                 return
#             elif teammate_action == 1:
#                 selected_game['teammates'][str(teammate)] = 1
#                 selected_game['total_teammates'] += 1
#         else:
#             if teammate_action == 1:
#                 selected_game['teammates'][str(teammate)] += 1
#                 selected_game['total_teammates'] += 1
#             else:
#                 teammate_current = selected_game['teammates'][str(teammate)]
#                 if teammate_current <= 1:
#                     del selected_game['teammates'][str(teammate)]
#                     selected_game['total_teammates'] -= 1
#                 else:
#                     selected_game['teammates'][str(teammate)] -= 1
#                     selected_game['total_teammates'] -= 1
#         data['games'][str(game_num)] = selected_game
#     elif message_id:
#         data['message_id'] = message_id
#     elif new_game:
#         count: str = 0
#         data = {
#             'message_id': None,
#             'games': {}}
#         for date in new_game:
#             count += 1
#             date_split = date.split(' — ')
#             date = app_data.DATE_HEADLIGHT.format(
#                 number=app_data.EMOJI_NUMBERS[count],
#                 date=date_split[0],
#                 location=date_split[1],
#                 count=0)
#             data['games'][count] = {
#                 'total_teammates': 0,
#                 'date': date,
#                 'teammates': {}}
#     else:
#         raise SystemExit(
#             'Something is wrong with input data in rebuild_game_dates_json!'
#             f'Got: game_num = {game_num}, teammate = {teammate}, '
#             f'teammate_action = {teammate_action}, message_id = {message_id}, '
#             f'new_game = {new_game}')
#     return data





# def check_telegram_bot_response(token: str) -> None:
#     """Проверяет ответ telegram BOT API."""
#     response: requests.Response = requests.get(
#         f'https://api.telegram.org/bot{token}/getMe')
#     status: int = response.status_code
#     if status == HTTPStatus.OK:
#         return
#     if status == HTTPStatus.UNAUTHORIZED:
#         raise SystemExit('Telegram bot token is invalid!')
#     else:
#         logger.warning(
#             f'Telegram API is unavailable with status {status}! '
#             'Try to reconnect in 5 minutes.')
#         sleep(300)
#         check_telegram_bot_response(token=token)


# def game_dates_json_update(telegram_id: int):
#     pass



    #####################################################
    # updater = Updater(token=app_data.TELEGRAM_BOT_TOKEN)
    # dispatcher = updater.dispatcher
    # dispatcher.add_handler(CommandHandler('start', send_message(bot=telegram_bot, message='Привет!')))

    # while 1:
    #     try:
    #         
    #         if update:
    #             

    #             
    #             

#                 logger.info('Sending update complete!')
#                 last_vk_wall_id = parsed_post['post_id']
#                 json_data_write(
#                     file_name='last_vk_wall_id.json',
#                     data={'last_vk_wall_id': last_vk_wall_id})
    #         else:
    #             logger.debug('No updates available.')
    #         updater.start_polling(poll_interval=1.0)
    #         updater.idle()

    #     logger.debug(f'Sleep for {app_data.API_UPDATE} sec.')
    #     updater.start_polling(poll_interval=1.0)
    #     updater.idle()

