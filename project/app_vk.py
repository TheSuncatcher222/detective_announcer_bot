from datetime import datetime
from http import HTTPStatus
import os
from PyPDF2 import PdfReader
from re import findall
import requests
import vk_api
from vk_api.exceptions import ApiError

from project.data.app_data import (
    LOCATIONS, MEDALS, NON_PINNED_POST_ID, PINNED_POST_ID, POST_TOPICS,
    TEAM_NAME, VK_GROUP_TARGET, VK_GROUP_TARGET_HASHTAG, VK_GROUP_TARGET_LOGO,
    VK_POST_LINK)


def init_vk_bot(token: str, user_id: int) -> any:
    """Check VK API. Create a session."""
    session = vk_api.VkApi(token=token)
    vk = session.get_api()
    try:
        vk.status.get(user_id=user_id)
    except vk_api.exceptions.ApiError:
        raise SystemExit('VK token is invalid!')
    return vk


# ФУНКЦИЯ НЕ НУЖДАЕТСЯ В ТЕСТИРОВАНИИ
def get_vk_wall_update(
        last_vk_wall_id: int,
        vk_bot: vk_api.VkApi.method,
        vk_group_id: int) -> dict:
    """Check for a new post in VK group."""
    try:
        wall: dict = vk_bot.wall.get(
            owner_id=f'-{vk_group_id}', count=2)
    except ApiError:
        raise SystemExit('VK group ID is invalid!')
    update: dict = None
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


# ФУНКЦИЯ ПРОТЕСТИРОВАНА
def define_post_topic(post: dict) -> str:
    """Define the topic of the given post."""
    try:
        post_text: str = post['text']
    except KeyError:
        raise Exception(
            "Post's json from VK wall has unknown structure!"
            "Try ['items'][0]['text'].")
    for key_tag in POST_TOPICS:
        if key_tag in post_text:
            return POST_TOPICS[key_tag]
    return 'other'


# ФУНКЦИЯ ПРОТЕСТИРОВАНАs
def game_dates_add_weekday_place(game_dates: list) -> list:
    """Add day of the week to each date and formate location."""
    DAYS_WEEK: tuple[str] = ('пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс')
    MONTH_NUM: tuple[str] = (
        None, 'января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля',
        'августа', 'сентября', 'октября', 'ноября', 'декабря')
    today: datetime = datetime.now()
    today_month: int = today.month
    today_year: int = today.year
    game_dates_format: list[str] = []
    for date_location in game_dates:
        date_time, location = date_location.split(' — ')
        date, time = date_time.split(', ')
        day, month = date.split()
        month: int = MONTH_NUM.index(month)
        year: int = today_year
        if month < today_month:
            year += 1
        date_digits: str = f'{day} {month} {year}'
        date_obj: datetime = datetime.strptime(date_digits, "%d %m %Y")
        day_name: str = DAYS_WEEK[date_obj.weekday()]
        location = LOCATIONS.get(location, location)
        game_dates_format.append(f'{date} ({day_name}), {time} — {location}')
    return game_dates_format


def fix_post_text(text: str) -> list:
    """."""
    # Тут появились какие-то \u3000
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
    post_link = [f'{VK_POST_LINK}{VK_GROUP_TARGET}_{post_id}']
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
    post_link = [f'{VK_POST_LINK}{VK_GROUP_TARGET}_{post_id})']
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
