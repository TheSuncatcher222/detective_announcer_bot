import pytest
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from project.app_vk import (
    define_post_topic, parse_message)

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
    (D_EXAMPLE_TEAMS, 'teams'),
])
def test_define_post_topic(post_example, expected_topic) -> None:
    """Test define_post_topic func from app_vk."""
    assert define_post_topic(post_example) == expected_topic


@pytest.mark.skip(reason='Currently no way to test it: uses VkApi.method!')
def test_init_vk_bot() -> None:
    """Test init_vk_bot func from app_vk."""
    pass


@pytest.mark.skip(reason='Currently no way to test it: uses VkApi.method!')
def test_get_vk_chat_update_groups():
    pass


@pytest.mark.skip(reason='Currently no way to test it: uses VkApi.method!')
def test_get_vk_wall_update_groups():
    pass


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
