from datetime import datetime
import os
from PyPDF2 import PdfReader
from re import findall, search, sub
import requests
from vk_api import VkApi
from vk_api.exceptions import ApiError

from project.data.app_data import (
    ALIBI, ALIBI_GROUP_ID, ALIBI_GROUP_LOGO, ALIBI_POST_LINK, ALIBI_TAG,
    DETECTIT, DETECTIT_GROUP_ID, DETECTIT_GROUP_LOGO, DETECTIT_POST_LINK,
    DETECTIT_TAG,

    GAME_REMINDER_LOOKUP, TEAM_REGISTER_LOOKUP, TEAM_REGISTER_TEXT,
    STOP_LIST_ACCEPT, STOP_LIST_DENY,

    LOCATIONS, MEDALS, TEAM_NAME,

    DATA_FOLDER, POST_TOPICS, PINNED_POST_ORDER, NON_PINNED_POST_ORDER)


def define_post_topic(post: dict) -> str:
    """Define the topic of the given post."""
    try:
        post_text: str = post['text']
    except KeyError:
        raise Exception(
            "Post's json from VK wall has unknown structure!"
            "Try 'text' key.")
    for key_tag in POST_TOPICS:
        if key_tag in post_text:
            return POST_TOPICS[key_tag]
    return 'other'


def init_vk_bot(token: str, user_id: int) -> VkApi.method:
    """Check VK API. Create a session."""
    try:
        session: VkApi = VkApi(token=token)
        vk: VkApi.method = session.get_api()
        vk.status.get(user_id=user_id)
        return vk
    except ApiError:
        raise SystemExit('VK token is invalid!')


def get_vk_chat_update_groups(
        last_message_id_alibi: int,
        last_message_id_detectit: int,
        vk_bot: VkApi.method) -> tuple[str, dict[str, any] | None]:
    """Manage get_vk_chat_update function: search vk groups for a new private
    message and return the first one or None if there are no
    updates or the message does not match to lookup."""
    group_name: str = ALIBI
    message_update: dict[str, any] | None = _get_vk_chat_update(
        last_message_id=last_message_id_alibi,
        vk_bot=vk_bot,
        vk_group_id=ALIBI_GROUP_ID)
    if message_update is None:
        group_name: str = DETECTIT
        message_update: dict[str, any] | None = _get_vk_chat_update(
            last_message_id=last_message_id_detectit,
            vk_bot=vk_bot,
            vk_group_id=DETECTIT_GROUP_ID)
    return group_name, message_update


def get_vk_wall_update_groups(
        last_wall_id_alibi: int,
        last_wall_id_detectit: int,
        vk_bot: VkApi.method) -> tuple[str, dict[str, any] | None]:
    """Manage get_vk_wall_update function: search vk groups for a new post and
    return the first one or None if there are no updates."""
    group_name: str = ALIBI
    update_wall: dict[str, any] | None = _get_vk_wall_update(
            last_wall_id=last_wall_id_alibi,
            vk_bot=vk_bot,
            vk_group_id=ALIBI_GROUP_ID)
    if update_wall is None:
        group_name: str = DETECTIT
        update_wall: dict[str, any] | None = _get_vk_wall_update(
            last_wall_id=last_wall_id_detectit,
            vk_bot=vk_bot,
            vk_group_id=DETECTIT_GROUP_ID)
    return group_name, update_wall


def parse_message(group_name: str, message: dict[any]) -> str | None:
    """Check if lookup in message text. If true return complete message text to
    send to the telegram chat. If not return None."""
    message_text: str = message['items'][0]['text']
    if TEAM_REGISTER_LOOKUP in message_text:
        money_amount: str = search(
            r'Стоимость участия:(\s)?\d+', message_text).group(0)[-3:]
        splitted_text: list[str] = _split_paragraphs(
            group_name=group_name, text=message_text)[0:3]
        message_text: list[str] = (
            splitted_text[:1]
            + splitted_text[2:3]
            + [TEAM_REGISTER_TEXT.format(money_amount=money_amount)])
        return '\n\n'.join(message_text)
    elif GAME_REMINDER_LOOKUP in message_text:
        splitted_text: list[str] = _split_paragraphs(
            group_name=group_name, text=message_text)
        message_text: list[str] = splitted_text[:1] + splitted_text[2:]
        return '\n\n'.join(message_text)
    return


def parse_post(
        group_name: str,
        post: dict[str, any],
        post_topic: str) -> dict[str, any] | None:
    """Manage post parsing."""
    post_id: int = post['id']
    post_text: list[str] = None
    post_image_url: str = None
    game_dates: list[str] = None
    splitted_text: list[str] = _split_paragraphs(
        group_name=group_name,
        text=post['text'])
    get_post_text: dict[str, function] = {
        'checkin': _parse_post_checkin,
        'game_results': _parse_post_game_results,
        'other': _parse_post_other,
        'prize_results': _parse_post_prize_results,
        'photos': _parse_post_add_link,
        'rating': _parse_post_add_link,
        'stop-list': _parse_post_stop_list,
        'tasks': _parse_post_add_link,
        'teams': _parse_post_teams}
    if post_topic in get_post_text:
        post_text: list[str] = get_post_text[post_topic](
            group_name=group_name,
            post_id=post_id,
            splitted_text=splitted_text)
    elif post_topic == 'preview':
        game_dates, post_text = _parse_post_preview(
            post_text=post['text'], splitted_text=splitted_text)
    if post_text is None:
        """Nothing to send to telegram chat. Exit."""
        return None
    # if video in: # Или в _get_post_image_url это
    #     block: str = 'video'
    # https://vk.com/detectitspb?w=wall-219311078_373
    if post_topic == 'photos':
        block: str = 'album'
    else:
        block: str = 'photo'
    post_image_url: str = _get_post_image_url(
        block=block, group_name=group_name, post=post)
    parsed_post: dict[str, any] = {
        'post_id': post_id,
        'post_image_url': post_image_url,
        'post_text': post_text}
    if 'game_dates':
        parsed_post['game_dates'] = game_dates
    return parsed_post


def _game_dates_add_weekday_place(game_dates: list[str]) -> list[str]:
    """Add day of the week to each date and formate location."""
    DAYS_WEEK: tuple[str] = ('ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС')
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


def _get_post_image_url(
        block: str, group_name: str, post: dict[str, any]) -> str:
    """Get image URL from the given post."""
    try:
        post_image_url = ''
        if block == 'photo':
            post_image_url: str = (
                post['attachments'][0]['photo']['sizes'][4]['url'])
        elif block == 'album':
            post_image_url: str = (
                post['attachments'][0]['photo']['sizes'][3]['url'])
        else:
            raise ValueError
        if not post_image_url.startswith('http'):
            raise ValueError
        return post_image_url
    except (AttributeError, KeyError, IndexError, ValueError):
        """
        AttributeError for 'NoneType' object has no attribute 'startswith'
        """
        if group_name == ALIBI:
            return ALIBI_GROUP_LOGO
        return DETECTIT_GROUP_LOGO


def _get_vk_chat_update(
        last_message_id: int,
        vk_bot: VkApi.method,
        vk_group_id: int) -> dict[any] | None:
    """Check for new message from target VK chat.
    Looking only for 'Team successfully registered' message subject
    or 'Game reminder'."""
    try:
        message: dict[any] = vk_bot.messages.getHistory(
            count=1, peer_id=-vk_group_id)
        message_id: int = message['items'][0]['id']
        if message_id > last_message_id:
            return message
        return
    except ApiError:
        raise SystemExit('VK group ID is invalid!')


def _get_vk_wall_update(
        last_wall_id: int,
        vk_bot: VkApi.method,
        vk_group_id: int) -> dict[str, any] | None:
    """Check for a new post in VK group."""
    try:
        wall: dict[str, any] = vk_bot.wall.get(
            owner_id=f'-{vk_group_id}', count=2)
    except ApiError:
        raise SystemExit('VK group ID is invalid!')
    for num in [NON_PINNED_POST_ORDER, PINNED_POST_ORDER]:
        try:
            if wall['items'][num]['id'] > last_wall_id:
                return wall['items'][num]
        except IndexError:
            pass
        except KeyError:
            raise Exception(
                "Post's json from VK wall has unknown structure!"
                f"Try ['items'][{num}]['id'].")
    return None


def _make_link_to_post(group_name: str, post_id: int) -> str:
    """Return link to the vk post with given post_id of target group."""
    if group_name == ALIBI:
        group_id: str = ALIBI_GROUP_ID
        group_post_link: str = ALIBI_POST_LINK
    else:
        group_id: str = DETECTIT_GROUP_ID
        group_post_link: str = DETECTIT_POST_LINK
    return f'{group_post_link}{group_id}_{post_id}'


def _parse_post_add_link(
        group_name: str,
        post_id: int,
        splitted_text: list[str]) -> list[str]:
    """Parse post's text if the topic is 'photos' or 'rating' or 'tasks'."""
    return (splitted_text[-1:]
            + [_make_link_to_post(group_name=group_name, post_id=post_id)])


def _parse_post_checkin(
        group_name: str, post_id: int, splitted_text: str) -> list[str]:
    """Parse post's text if the topic is 'checkin'."""
    return [
        *splitted_text[:2],
        *splitted_text[-5:-3],
        'Действует розыгрыш бесплатного входа на всю команду! '
        'Чтобы принять в нем участие, нужно вступить в группу и сделать '
        'репост этой записи:',
        _make_link_to_post(group_name=group_name, post_id=post_id),
        search(
            r'Результаты будут в ночь с \d+ на \d+ \w+\.',
            splitted_text[-2]).group(0)]


def _parse_post_game_results(
        splitted_text: str, team_name: str = TEAM_NAME) -> list[str] | None:
    """Parse post's text if the topic is 'game_results'.
    If TEAM_NAME not in text - return None."""
    for paragraph in splitted_text:
        reg_search = search(fr'\d\sместо: «{team_name}»', paragraph)
        if reg_search:
            medals: list[str] = MEDALS[f'{reg_search.group(0)[0]}th']
            return splitted_text[:-2] + medals
    return None


def _parse_post_other(splitted_text: list[str]) -> list[str]:
    """Parse post's text if the topic is 'other'."""
    return splitted_text[-1:]


def _parse_post_preview(
        group_name: str,
        post_text: str,
        splitted_text: list) -> tuple[list[str]]:
    """Parse post's text if the topic is 'preview'.
    Separately return list with game dates and text."""
    if group_name == ALIBI:
        game_dates: list[str] = _game_dates_add_weekday_place(
            game_dates=findall(
                r'\d{1,2} \w+, \d{2}\:\d{2} \— \w+ \w+ \w+ \w+(?:\s\w+)?',
                post_text))
    else:
        game_dates = findall(
            r'(\d{1,2} \w+ \(\w+\), \d{2}:\d{2}, [^\n\;]+)',
            post_text)
    post_text: list[str] = (
        splitted_text[0:len(splitted_text)-(4+len(game_dates))]
        + splitted_text[-3:-2])
    return game_dates, post_text


def _parse_post_prize_results(splitted_text: list[str]) -> list[str]:
    """Parse post's text if the topic is 'prize_results'."""
    return splitted_text[-1:]


def _parse_post_teams(splitted_text: list[str]) -> list[str]:
    """Parse post's text if the topic is 'teams'."""
    return splitted_text[:2]


def _parse_post_stop_list(
        post: dict[str, any],
        splitted_text: list[str]) -> list[str]:
    """Parse post's text if the topic is 'stop-list'.
    Read attached PDF with stop-list and search team."""
    try:
        response: requests = requests.get(post['attachments'][1]['doc']['url'])
    except (KeyError, IndexError):
        raise Exception(
            "Post's json from VK wall has unknown structure!"
            "Try ['items'][0]['attachments'][1]['doc']['url'].")
    filename: str = f'{DATA_FOLDER}stop-list.pdf'
    with open(filename, 'wb') as write_file:
        write_file.write(response.content)
    reader: PdfReader = PdfReader(filename)
    text_verdict: str = STOP_LIST_ACCEPT
    for i in range(len(reader.pages)):
        if TEAM_NAME in reader.pages[i].extract_text():
            text_verdict = STOP_LIST_DENY
            break
    os.remove(filename)
    return splitted_text[:1] + [text_verdict] + splitted_text[1:3]


def _split_paragraphs(group_name: str, text: str) -> list[str]:
    """Split text into paragraphs and add group tag to the top."""
    fixed_text: str = sub(r'(\n\s*\n)+', '\n', text.strip())
    if group_name == ALIBI:
        tag: str = ALIBI_TAG
    else:
        tag: str = DETECTIT_TAG
    return [tag] + fixed_text.split('\n')
