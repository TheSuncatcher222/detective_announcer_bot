from datetime import datetime
import os
from PyPDF2 import PdfReader
from re import findall, search, sub
import requests
import vk_api
from vk_api.exceptions import ApiError

from project.data.app_data import (
    APP_JSON_FOLDER, LOCATIONS, MEDALS, NON_PINNED_POST_ID, PINNED_POST_ID,
    POST_TOPICS, TEAM_NAME, TEAM_REGISTER_LOOKUP, TEAM_REGISTER_TEXT,
    VK_GROUP_TARGET, VK_GROUP_TARGET_LOGO, VK_POST_LINK)


def init_vk_bot(token: str, user_id: int) -> vk_api.VkApi.method:
    """Check VK API. Create a session."""
    try:
        session: vk_api.VkApi = vk_api.VkApi(token=token)
        vk: vk_api.VkApi.method = session.get_api()
        vk.status.get(user_id=user_id)
        return vk
    except vk_api.exceptions.ApiError:
        raise SystemExit('VK token is invalid!')


def get_vk_chat_update(
        last_vk_message_id: dict[str, int], vk_bot: vk_api.VkApi.method
        ) -> str | None:
    """Check for new message from target VK chat.
    Looking only for 'Team successfully registered' message subject."""
    try:
        message: dict = vk_bot.messages.getHistory(
            count=1, peer_id=-VK_GROUP_TARGET)
        message_id: int = message['items'][0]['id']
        if message_id > last_vk_message_id['last_vk_message_id']:
            message_text: str = message['items'][0]['text']
            if TEAM_REGISTER_LOOKUP in message_text:
                message_text: list[str] = _split_post_text(message_text)[1:2]
                message_text.append(TEAM_REGISTER_TEXT)
                last_vk_message_id['last_vk_message_id'] = message_id
                return '\n'.join(message_text)
            last_vk_message_id['last_vk_message_id'] = message_id
        return
    except ApiError:
        raise SystemExit('VK group ID is invalid!')


def get_vk_wall_update(
        last_vk_wall_id: int, vk_bot: vk_api.VkApi.method, vk_group_id: int
        ) -> dict[str, any] | None:
    """Check for a new post in VK group."""
    try:
        wall: dict[str, any] = vk_bot.wall.get(
            owner_id=f'-{vk_group_id}', count=2)
    except ApiError:
        raise SystemExit('VK group ID is invalid!')
    for num in (NON_PINNED_POST_ID, PINNED_POST_ID):
        try:
            if wall['items'][num]['id'] > last_vk_wall_id:
                return wall['items'][num]
        except IndexError:
            pass
        except KeyError:
            raise Exception(
                "Post's json from VK wall has unknown structure!"
                f"Try ['items'][{num}]['id'].")
    return None


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


def _game_dates_add_weekday_place(game_dates: list[str]) -> list[str]:
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
        location: str = LOCATIONS.get(location, location)
        game_dates_format.append(f'{date} ({day_name}), {time} — {location}')
    return game_dates_format


def _split_post_text(post_text: str) -> list[str]:
    """Split text into paragraphs."""
    fixed_text: str = sub(r'(\n\s*\n)+', '\n', post_text.strip())
    return fixed_text.split('\n')[:-1]


def _get_post_image_url(block: str, post: dict[str, any]) -> str:
    """Get image URL from the given post."""
    try:
        if block == 'photo':
            post_image_url: str = (
                post['attachments'][0]['photo']['sizes'][4]['url'])
        elif block == 'album':
            post_image_url: str = (
                post['attachments'][0]['album']['thumb']['sizes'][3]['url'])
        if not post_image_url.startswith('http'):
            raise ValueError
        return post_image_url
    except (KeyError, IndexError):
        f"Post's json for {block} from VK wall has unknown structure!"
    except ValueError:
        f"['url'] for {block}: data does not contain 'http' link."
    return VK_GROUP_TARGET_LOGO


def _parse_post_checkin(post_id: int, split_text: str) -> list[str]:
    """Parse post's text if the topic is 'checkin'."""
    return [
        split_text[0],
        *split_text[-4:-2],
        'Действует розыгрыш бесплатного входа на всю команду! '
        'Чтобы принять в нем участие, нужно вступить в группу и сделать '
        'репост этой записи:\n\n'
        f'{VK_POST_LINK}{VK_GROUP_TARGET}_{post_id}']


def _parse_post_game_results(
        split_text: str, team_name: str = TEAM_NAME) -> str:
    """Parse post's text if the topic is 'game_results'."""
    reg_exp: str = fr'\d\sместо: «{team_name}»'
    for paragraph in split_text:
        reg_search = search(reg_exp, paragraph)
        if reg_search:
            split_text += MEDALS[f'{reg_search.group(0)[0]}th']
            break
    return split_text


def _parse_post_preview(post_text: str, split_text: list) -> tuple[list[str]]:
    """Parse post's text if the topic is 'preview'.
    Separately return list with game dates and text."""
    game_dates: list[str] = _game_dates_add_weekday_place(
        game_dates=findall(
            r'\d+\s\w+,\s\d+\:\d+\s\—\s\w+\s\w+\s\w+\s\w+',
            post_text))
    post_text: list[str] = split_text[0:4] + split_text[-2:-1]
    return game_dates, post_text


def _parse_post_stop_list(
        post: dict[str, any], split_text: list[str], team_name: str = TEAM_NAME
        ) -> list[str]:
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


def parse_post(post: dict[str, any], post_topic: str) -> dict[str, any] | None:
    """Manage post parsing."""
    post_id: int = post['id']
    post_text: list[str] = None
    post_image_url: str = None
    game_dates: list[str] = None
    split_text: list[str] = _split_post_text(post_text=post['text'])
    if post_topic == 'checkin':
        post_text = _parse_post_checkin(post_id=post_id, split_text=split_text)
    elif post_topic == 'game_results' and TEAM_NAME in post['text']:
        post_text = _parse_post_game_results(split_text=split_text)
    elif post_topic == 'other':
        post_text = split_text
    elif post_topic == 'photos' or post_topic == 'rating':
        post_text = split_text + [f'{VK_POST_LINK}{VK_GROUP_TARGET}_{post_id}']
    elif post_topic == 'preview':
        game_dates, post_text = _parse_post_preview(
            post_text=post['text'], split_text=split_text)
    elif post_topic == 'prize_results':
        post_text = split_text
    elif post_topic == 'stop-list':
        post_text = _parse_post_stop_list(post=post, split_text=split_text)
    elif post_topic == 'teams':
        post_text = split_text[:2]
    if not post_text:
        return None
    if post_topic == 'photos':
        block: str = 'album'
    else:
        block: str = 'photo'
    post_image_url: str = _get_post_image_url(post=post, block=block)
    parsed_post: dict[str, any] = {
        'post_id': post_id,
        'post_image_url': post_image_url,
        'post_text': post_text}
    if 'game_dates':
        parsed_post['game_dates'] = game_dates
    return parsed_post
