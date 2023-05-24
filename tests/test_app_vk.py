import pytest
from pytest_mock import mocker
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from project.app_vk import (
    define_post_topic, parse_message, _game_dates_add_weekday_place,
    _get_post_image_url, _get_vk_chat_update, _split_abstracts)

from project.data.app_data import TEAM_NAME, TEAM_CAPITAN_PROP

from vk_wall_examples import (
    A_EXAMPLE_CHECKIN, A_EXAMPLE_GAME_RESULTS, A_EXAMPLE_OTHER,
    A_EXAMPLE_PHOTOS, A_EXAMPLE_PREVIEW, A_EXAMPLE_PRIZE_RESULTS,
    A_EXAMPLE_RATING, A_EXAMPLE_STOP_LIST, A_EXAMPLE_TASKS, A_EXAMPLE_TEAMS,

    D_EXAMPLE_CHECKIN, D_EXAMPLE_GAME_RESULTS, D_EXAMPLE_OTHER,
    D_EXAMPLE_PHOTOS, D_EXAMPLE_PREVIEW, D_EXAMPLE_PRIZE_RESULTS,
    D_EXAMPLE_RATING, D_EXAMPLE_STOP_LIST, D_EXAMPLE_TASKS, D_EXAMPLE_TEAMS)

NL = '\n'


@pytest.mark.parametrize('post_example, expected_topic', [
    (A_EXAMPLE_CHECKIN, 'checkin'),
    (A_EXAMPLE_GAME_RESULTS, 'game_results'),
    (A_EXAMPLE_OTHER, 'other'),
    # (A_EXAMPLE_PHOTOS, TypeError),
    (A_EXAMPLE_PREVIEW, 'preview'),
    (A_EXAMPLE_PRIZE_RESULTS, 'prize_results'),
    (A_EXAMPLE_RATING, 'rating'),
    # (A_EXAMPLE_STOP_LIST, TypeError),
    (A_EXAMPLE_TASKS, 'tasks'),
    (A_EXAMPLE_TEAMS, 'teams'),
    (D_EXAMPLE_CHECKIN, 'checkin'),
    (D_EXAMPLE_GAME_RESULTS, 'game_results'),
    # (D_EXAMPLE_OTHER, TypeError),
    (D_EXAMPLE_PHOTOS, 'photos'),
    (D_EXAMPLE_PREVIEW, 'preview'),
    (D_EXAMPLE_PRIZE_RESULTS, 'prize_results'),
    # (D_EXAMPLE_RATING, TypeError),
    (D_EXAMPLE_STOP_LIST, 'stop-list'),
    # (D_EXAMPLE_TASKS, TypeError),
    (D_EXAMPLE_TEAMS, 'teams')])
def test_define_post_topic(post_example, expected_topic) -> None:
    """Test define_post_topic func from app_vk."""
    assert define_post_topic(post_example) == expected_topic


@pytest.mark.skip(reason='Currently no way to test it: uses VkApi.method!')
def test_init_vk_bot() -> None:
    """Test init_vk_bot func from app_vk."""
    pass


MESSAGE_GET_VK_CHAT_UPDATE: dict = {'items': [{'id': 2}]}


@pytest.mark.parametrize('last_message_id, expected', [
    (1, MESSAGE_GET_VK_CHAT_UPDATE),
    (2, None)])
def test_get_vk_chat_update(last_message_id, expected, mocker):
    vk_bot_mock = mocker.Mock()
    vk_bot_mock.messages.getHistory.return_value = MESSAGE_GET_VK_CHAT_UPDATE
    result = _get_vk_chat_update(
        last_message_id=last_message_id,
        vk_bot=vk_bot_mock,
        vk_group_id=0)
    assert result == expected


@pytest.mark.skip(reason='Currently no way to test it: uses VkApi.method!')
def test_get_vk_chat_update_groups():
    pass


@pytest.mark.skip(reason='Currently no way to test it: uses VkApi.method!')
def test_get_vk_wall_update_groups():
    pass


@pytest.mark.parametrize('group_name, text, splitted_text', [
    ('Alibi', 'One\nTwo\n\nThree\n\n\nFour\n\n\n\nEnd.',
     ['🟣 Alibi', 'One', 'Two', 'Three', 'Four', 'End.']),
    ('Detectit', 'One\nTwo\n\nThree\n\n\nFour\n\n\n\nEnd.',
     ['⚫️ Detectit', 'One', 'Two', 'Three', 'Four', 'End.'])])
def test_split_abstracts(group_name, text, splitted_text):
    assert _split_abstracts(group_name=group_name, text=text) == splitted_text


MESSAGE_NO_LOOKUP: str = 'Просто сообщение.'
MESSAGE_GAME_REMINDER_LOOKUP: str = (
    'Здравствуйте, детектив!\n\n'

    'Напоминаем, что завтра, 27 апреля, пройдёт расследование где-нибудь.\n'
    'Сбор команд начинается в 19:00, в 19:30 начинается игра.')
MESSAGE_TEAM_REGISTER_LOOKUP: str = (
    'Здравствуйте, детектив!\n\n'

    f'Регистрация команды «{TEAM_NAME}» в составе 4 игроков на расследование '
    '17 мая, 19:30 где-нибудь прошла успешно!\n'
    'Чтобы подтвердить бронь, вам нужно оплатить участие в течение 24 часов. '
    'Если вы отменяете участие менее, чем за сутки, оплата не возвращается. '
    'Стоимость участия: 123 ₽ с человека.\n\n'

    'Оплатить можно переводом на номер: 8-888-888-88-8.\n'
    'Какой-нибудь банк, на имя Имя Ф.\n'
    '❗ комментариях к переводу ничего указывать не нужно.\n\n'

    'Пожалуйста, пришлите скрин/квитанцию перевода в этот диалог :)')
PARSED_MESSAGE_GAME_REMINDER: str = (
    'Напоминаем, что завтра, 27 апреля, пройдёт расследование где-нибудь.\n\n'

    'Сбор команд начинается в 19:00, в 19:30 начинается игра.')
PARSED_MESSAGE_TEAM_REGISTER: str = (
    f'Регистрация команды «{TEAM_NAME}» в составе 4 игроков на расследование '
    '17 мая, 19:30 где-нибудь прошла успешно!\n\n'

    'Для подтверждения брони необходимо в течении суток оплатить участие в '
    f'игре. Оплата производится капитану команды по номеру {TEAM_CAPITAN_PROP}'
    ' в размере 123 рублей.\n\n'

    'Если команда отменяет участие менее, чем за сутки, оплата не '
    'возвращается.\n\n'

    'Если в составе команды будут дополнительные игроки, оплатить участие '
    'возможно по цене:\n'
    '· 500 ₽ с человека — до дня игры,\n'
    '· 600 ₽ с человека — в день игры.')


@pytest.mark.parametrize('group_name, message, parsed_message', [
    ('Alibi', MESSAGE_NO_LOOKUP, None),
    ('Alibi', MESSAGE_GAME_REMINDER_LOOKUP,
     f"🟣 Alibi{NL*2}{PARSED_MESSAGE_GAME_REMINDER}"),
    ('Alibi', MESSAGE_TEAM_REGISTER_LOOKUP,
     f"🟣 Alibi{NL*2}{PARSED_MESSAGE_TEAM_REGISTER}"),
    ('Detectit', MESSAGE_NO_LOOKUP, None),
    ('Detectit', MESSAGE_GAME_REMINDER_LOOKUP,
     f"⚫️ Detectit{NL*2}{PARSED_MESSAGE_GAME_REMINDER}"),
    ('Detectit', MESSAGE_TEAM_REGISTER_LOOKUP,
     f"⚫️ Detectit{NL*2}{PARSED_MESSAGE_TEAM_REGISTER}")])
def test_parse_message(group_name, message, parsed_message):
    assert parse_message(
        group_name=group_name,
        message={'items': [{'text': message}]}) == parsed_message


@pytest.mark.parametrize('game_date, expected', [
    ('1 июня, 19:00 — секретное место на Василеостровской',
     '1 июня (ЧТ), 19:00 — ресторан Цинь (16-я лин. B.O., 83)'),
    ('7 июля, 19:30 — секретное место на Горьковской',
     '7 июля (ПТ), 19:30 — ресторан Parkking (Александровский парк, 4)'),
    ('22 августа, 12:13 — секретное место на Петроградской',
     '22 августа (ВТ), 12:13 — ресторан Unity на Петроградской '
     '(наб. Карповки, 5к17)'),
    ('11 сентября, 00:00 — секретное место на Площади Ленина',
     '11 сентября (ПН), 00:00 — Центр Kod (ул. Комсомола, 2)'),
    ('18 октября, 23:59 — секретное место на Сенной',
     '18 октября (СР), 23:59 — ресторан Unity на Сенной (пер. Гривцова, 4)'),
    ('25 ноября, 11:11 — секретное место на Чернышевской',
     '25 ноября (СБ), 11:11 — Дворец Олимпия (Литейный пр., 14)'),
    ('31 декабря, 23:59 — секретное место в нигде',
     '31 декабря (ВС), 23:59 — секретное место в нигде')])
def test_game_dates_add_weekday_place(game_date, expected):
    assert _game_dates_add_weekday_place([game_date]) == [expected], (
        'In tested func datetime.datetime.now() is used! '
        'Due to this - if error caused by abbreviation for the day of the '
        'week - correct data according calendar in expected value or change '
        'date in game_date.')


@pytest.mark.parametrize('block, group_name, post, expected_url', [
    # Correct case: photo
    ('photo',
    'Alibi',
    {'attachments': [{'photo': {'sizes': [0, 1, 2, 3, {
        'url': 'http://url_1/'}]}}]},
    'http://url_1/'),
    # Correct case: album
    ('album',
    'Alibi',
    {'attachments':[{'album': {'thumb': {'sizes': [0, 1, 2, {
        'url': 'http://url_2/'}]}}}]},
    'http://url_2/'),
    # Incorrect case: AttributeError (Alibi default photo used)
    # post_image_url = '' - because 'block' has unexpected value
    ('unexpected_value',
    'Alibi',
    {'attachments':[{'album': {'thumb': {'sizes': [0, 1, 2, {
        'url': 'http://url_1/'}]}}}]},
    'https://sun9-46.userapi.com/impg/LiT08C2tWC-QeeYRDjHqaHRFyXNOYyhxFacXQA/'
    'JpfUXhL2n2s.jpg?size=674x781&quality=95&sign='
    'e8310f98da4ff095adb5e46ba20eef2d&type=album'),
    # Incorrect case: ValueError (Detectit default photo used)
    # post_image_url = '' - because URL doesn't start with "http"
    ('unexpected_value',
    'Detectit',
    {'attachments':[{'album': {'thumb': {'sizes': [0, 1, 2, {
        'url': 'not_http'}]}}}]},
    'https://sun9-40.userapi.com/impg/frYTaWRpxfjOS8eVZayKsugTQILb9MM0uYggNQ/'
    'UhQlYUWdBh0.jpg?size=800x768&quality=95&sign='
    'bb10ce9b1e4f2328a2382faba0981c2c&type=album')])
def test_get_post_image_url(block, group_name, post, expected_url):
    assert _get_post_image_url(
        block=block, group_name=group_name, post=post) == expected_url


@pytest.mark.skip(reason='Currently no way to test it: uses VkApi.method!')
def test_get_vk_wall_update():
    pass
