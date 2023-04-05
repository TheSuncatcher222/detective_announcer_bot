from datetime import datetime
from http import HTTPStatus
import os
from PyPDF2 import PdfReader
from re import findall, sub
import requests
import vk_api
from vk_api.exceptions import ApiError

from project.data.app_data import (
    APP_JSON_FOLDER, LOCATIONS, MEDALS, NON_PINNED_POST_ID, PINNED_POST_ID,
    POST_TOPICS, TEAM_NAME, VK_GROUP_TARGET, VK_GROUP_TARGET_LOGO,
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


def split_post_text(post_text: str) -> list:
    """Split text into paragraphs."""
    fixed_text: str = sub(r'(\n\s*\n)+', '\n', post_text.strip())
    return fixed_text.split('\n')[:-1]


def get_post_image_url(post: dict, block: str) -> str:
    """Get image URL from the given post."""
    try:
        if block == 'photo':
            post_image_url = (
                post['attachments'][0]['photo']['sizes'][4]['url'])
        elif block == 'album':
            post_image_url = (
                post['attachments'][0]['album']['thumb']['sizes'][3]['url'])
        if not post_image_url.startswith('http'):
            raise ValueError
        return post_image_url
    except (KeyError, IndexError):
        f"Post's json for {block} from VK wall has unknown structure!"
    except ValueError:
        f"['url'] for {block}: data does not contain 'http' link."
    return None


def parse_post_stop_list(
        post: dict, split_text: list, team_name=TEAM_NAME) -> list:
    """Parse post's text if the topic is 'stop-list'.
    Read attached PDF with stop-list and search team."""
    try:
        response: requests = requests.get(post['attachments'][1]['doc']['url'])
    except (KeyError, IndexError):
        raise Exception(
            "Post's json from VK wall has unknown structure!"
            "Try ['items'][0]['attachments'][1]['doc']['url'].")
    filename: str = f'{APP_JSON_FOLDER}stop-list.pdf'
    with open(filename, 'wb') as write_file:
        write_file.write(response.content)
    reader: PdfReader = PdfReader(filename)
    text_verdict: str = 'Команда допущена к регистрации на серию игр!'
    for i in range(len(reader.pages)):
        if team_name in reader.pages[i].extract_text():
            text_verdict = 'Команда уже была на представленной серии игр!'
            break
    os.remove(filename)
    return [text_verdict] + split_text[:len(split_text)-1]


def parse_post_preview(post_text: str, split_text: list) -> tuple[list[str]]:
    """Parse post's text if the topic is 'preview'.
    Separately return list with game dates and text."""
    game_dates: list[str] = game_dates_add_weekday_place(
        game_dates=findall(
            r'\d+\s\w+,\s\d+\:\d+\s\—\s\w+\s\w+\s\w+\s\w+',
            post_text))
    post_text: list[str] = split_text[0:4] + split_text[-2:-1]
    return game_dates, post_text


def parse_post_checkin(split_text: str, post_id: int) -> list[str]:
    """Parse post's text if the topic is 'checkin'."""
    return [
        split_text[0],
        *split_text[-4:-2],
        'Действует розыгрыш бесплатного входа на всю команду! '
        'Чтобы принять в нем участие, нужно вступить в группу и сделать '
        'репост этой записи:\n'
        f'{VK_POST_LINK}{VK_GROUP_TARGET}_{post_id}']


def parse_post_game_results(split_text: str):
    """Parse post's text if the topic is 'game_results'."""
    post_text = split_text[:2]
    post_text += (split_text[-7:-1])
    for paragraph, medal in MEDALS.items():
        if TEAM_NAME in post_text[paragraph]:
            post_text += medal
            break
    return post_text


def parse_post_photos(split_text: list, post_id: int):
    """."""
    post_text_1 = ['📷 Фотографии 📷']
    post_text_2 = split_text[:len(split_text)-2]
    post_link = [f'{VK_POST_LINK}{VK_GROUP_TARGET}_{post_id})']
    post_text = post_text_1 + post_text_2 + post_link
    return post_text


def parse_post_other(split_text: list):
    """."""
    if '#' in split_text[-1]:
        split_text = split_text[:-1]
    return split_text


def parse_post(post: dict, post_topic: str) -> dict:
    """Производит структурный анализ и разделяет пост на составные части."""
    post_id: int = post['id']
    post_text: str = None
    post_image_url: str = None
    game_dates: list = None
    split_text = split_post_text(post_text=post['text'])
    if post_topic == 'stop-list':
        post_text = parse_post_stop_list(
            post_text=post['text'], split_text=split_text)
    elif post_topic == 'preview':
        game_dates, post_text = parse_post_preview(
            post=post, split_text=split_text)
    elif post_topic == 'checkin':
        post_text = parse_post_checkin(split_text=split_text)
    elif post_topic == 'teams':
        post_text = ['Списки команд']
    elif post_topic == 'game_results' and TEAM_NAME in post['text']:
        post_text = parse_post_game_results(split_text=split_text)
    elif post_topic == 'prize_results':
        post_text = split_text[:len(split_text)-1]
    elif post_topic == 'photos':
        post_text = parse_post_photos(
            split_text=split_text, post_id=post_id)
    elif post_topic == 'other':
        post_text = parse_post_other(split_text=split_text)
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
