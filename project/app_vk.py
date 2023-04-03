from datetime import datetime
from http import HTTPStatus
import os
from PyPDF2 import PdfReader
from re import findall
import requests
import vk_api
from vk_api.exceptions import ApiError

from data.app_data import (
    LOCATIONS, MEDALS, MONTHS, NON_PINNED_POST_ID, PINNED_POST_ID, POST_TOPICS,
    TEAM_NAME, VK_GROUP_TARGET, VK_GROUP_TARGET_HASHTAG, VK_GROUP_TARGET_LOGO,
    VK_POST_LINK, WEEKDAYS)


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
        # Возможно я тут сломал, скобки были пустые
        date = date_time_split[0].split(' ')
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
