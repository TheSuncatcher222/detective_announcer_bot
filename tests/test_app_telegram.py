import pytest
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from project.app_telegram import (
    form_game_dates_text, rebuild_team_config,
    _create_new_team_config_game_dates)

from project.data.app_data import (
    ALIBI, DETECTIT)

GAME_DATES: list[str] = ['Игра №1', 'Игра №2', 'Игра №3']
TEAM_CONFIG_NEW_EXP: dict[int, dict] = {
    1: {
        'date_location': 'Игра №1',
        'teammates': {}},
    2: {
        'date_location': 'Игра №2',
        'teammates': {}},
    3: {
        'date_location': 'Игра №3',
        'teammates': {}},
    0: {
        'date_location': 'Не смогу быть',
        'teammates': {}}}


def test_create_new_team_config_game_dates():
    """Test _create_new_team_config_game_dates func from app_telegram."""
    assert _create_new_team_config_game_dates(
        game_dates=GAME_DATES) == TEAM_CONFIG_NEW_EXP


TEAM_CONFIG_INITIAL: dict[int, dict] = {
    1: {
        'date_location': 'Игра №1',
        'teammates': {
            'Teammate_1': 2}},
    2: {
        'date_location': 'Игра №2',
        'teammates': {}},
    3: {
        'date_location': 'Игра №3',
        'teammates': {
            'Teammate_1': 1,
            'Teammate_2': 1,
            'Teammate_4': 1}},
    4: {
        'date_location': 'Игра №4',
        'teammates': {
            'Teammate_2': 3,
            'Teammate_4': 1}},
    0: {
        'date_location': 'Не смогу быть',
        'teammates': {
            'Teammate_3': 1}}}
A_GAME_DATES_TEXT_EXP: str = (
    '🟣 Alibi\n'
    '\n'
    '1️⃣ Игра №1\n'
    '• Teammate_1\n'
    '• Teammate_1 (гость)\n'
    '\n'
    '2️⃣ Игра №2\n'
    '\n'
    '3️⃣ Игра №3\n'
    '• Teammate_1\n'
    '• Teammate_2\n'
    '• Teammate_4\n'
    '\n'
    '4️⃣ Игра №4\n'
    '• Teammate_2\n'
    '• Teammate_2 (гость)\n'
    '• Teammate_2 (гость)\n'
    '• Teammate_4\n'
    '\n'
    '🚫 Не смогу быть\n'
    '• Teammate_3\n')
D_GAME_DATES_TEXT_EXP: str = (
    '⚫️ Detectit\n'
    '\n'
    '1️⃣ Игра №1\n'
    '• Teammate_1\n'
    '• Teammate_1 (гость)\n'
    '\n'
    '2️⃣ Игра №2\n'
    '\n'
    '3️⃣ Игра №3\n'
    '• Teammate_1\n'
    '• Teammate_2\n'
    '• Teammate_4\n'
    '\n'
    '4️⃣ Игра №4\n'
    '• Teammate_2\n'
    '• Teammate_2 (гость)\n'
    '• Teammate_2 (гость)\n'
    '• Teammate_4\n'
    '\n'
    '⛔️ Не смогу быть\n'
    '• Teammate_3\n')


@pytest.mark.parametrize('group_name, expected', [
    (ALIBI, A_GAME_DATES_TEXT_EXP),
    (DETECTIT, D_GAME_DATES_TEXT_EXP)])
def test_form_game_dates_text(group_name, expected):
    """Test form_game_dates_text func from app_telegram."""
    assert form_game_dates_text(
        group_name=group_name, team_config=TEAM_CONFIG_INITIAL) == expected


# Teammate (1) chose new game date (2)
TEAMMATE_DECISION_1: dict[str, str | int] = {
    'teammate': 'Teammate_1',
    'game_num': 2,
    'decision': 1}
TEAM_CONFIG_EXP_1: dict[int, dict] = {
    1: {
        'date_location': 'Игра №1',
        'teammates': {
            'Teammate_1': 2}},
    2: {
        'date_location': 'Игра №2',
        'teammates': {
            'Teammate_1': 1}},
    3: {
        'date_location': 'Игра №3',
        'teammates': {
            'Teammate_1': 1,
            'Teammate_2': 1,
            'Teammate_4': 1}},
    4: {
        'date_location': 'Игра №4',
        'teammates': {
            'Teammate_2': 3,
            'Teammate_4': 1}},
    0: {
        'date_location': 'Не смогу быть',
        'teammates': {
            'Teammate_3': 1}}}
# Teammate (2) chose game date where has already marked (4)
TEAMMATE_DECISION_2: dict[str, str | int] = {
    'teammate': 'Teammate_2',
    'game_num': 4,
    'decision': 1}
TEAM_CONFIG_EXP_2: dict[int, dict] = {
    1: {
        'date_location': 'Игра №1',
        'teammates': {
            'Teammate_1': 2}},
    2: {
        'date_location': 'Игра №2',
        'teammates': {}},
    3: {
        'date_location': 'Игра №3',
        'teammates': {
            'Teammate_1': 1,
            'Teammate_2': 1,
            'Teammate_4': 1}},
    4: {
        'date_location': 'Игра №4',
        'teammates': {
            'Teammate_2': 4,
            'Teammate_4': 1}},
    0: {
        'date_location': 'Не смогу быть',
        'teammates': {
            'Teammate_3': 1}}}
# Teammate (1) chose delete from game date where has already marked more
# than 1 times (1)
TEAMMATE_DECISION_3: dict[str, str | int] = {
    'teammate': 'Teammate_1',
    'game_num': 1,
    'decision': -1}
TEAM_CONFIG_EXP_3: dict[int, dict] = {
    1: {
        'date_location': 'Игра №1',
        'teammates': {
            'Teammate_1': 1}},
    2: {
        'date_location': 'Игра №2',
        'teammates': {}},
    3: {
        'date_location': 'Игра №3',
        'teammates': {
            'Teammate_1': 1,
            'Teammate_2': 1,
            'Teammate_4': 1}},
    4: {
        'date_location': 'Игра №4',
        'teammates': {
            'Teammate_2': 3,
            'Teammate_4': 1}},
    0: {
        'date_location': 'Не смогу быть',
        'teammates': {
            'Teammate_3': 1}}}
# Teammate (2) chose delete from game date where has already marked exactly
# 1 times (1)
TEAMMATE_DECISION_4: dict[str, str | int] = {
    'teammate': 'Teammate_2',
    'game_num': 3,
    'decision': -1}
TEAM_CONFIG_EXP_4: dict[int, dict] = {
    1: {
        'date_location': 'Игра №1',
        'teammates': {
            'Teammate_1': 2}},
    2: {
        'date_location': 'Игра №2',
        'teammates': {}},
    3: {
        'date_location': 'Игра №3',
        'teammates': {
            'Teammate_1': 1,
            'Teammate_4': 1}},
    4: {
        'date_location': 'Игра №4',
        'teammates': {
            'Teammate_2': 3,
            'Teammate_4': 1}},
    0: {
        'date_location': 'Не смогу быть',
        'teammates': {
            'Teammate_3': 1}}}
# Teammate (3) chose delete from game date where has not marked (1)
TEAMMATE_DECISION_5: dict[str, str | int] = {
    'teammate': 'Teammate_3',
    'game_num': 1,
    'decision': -1}
TEAM_CONFIG_EXP_5: dict[int, dict] = {
    1: {
        'date_location': 'Игра №1',
        'teammates': {
            'Teammate_1': 2}},
    2: {
        'date_location': 'Игра №2',
        'teammates': {}},
    3: {
        'date_location': 'Игра №3',
        'teammates': {
            'Teammate_1': 1,
            'Teammate_2': 1,
            'Teammate_4': 1}},
    4: {
        'date_location': 'Игра №4',
        'teammates': {
            'Teammate_2': 3,
            'Teammate_4': 1}},
    0: {
        'date_location': 'Не смогу быть',
        'teammates': {
            'Teammate_3': 1}}}
# Teammate (2) chose skip games (0) but has already marked other game_dates
TEAMMATE_DECISION_6: dict[str, str | int] = {
    'teammate': 'Teammate_2',
    'game_num': 0,
    'decision': 1}
TEAM_CONFIG_EXP_6: dict[int, dict] = {
    1: {
        'date_location': 'Игра №1',
        'teammates': {
            'Teammate_1': 2}},
    2: {
        'date_location': 'Игра №2',
        'teammates': {}},
    3: {
        'date_location': 'Игра №3',
        'teammates': {
            'Teammate_1': 1,
            'Teammate_4': 1}},
    4: {
        'date_location': 'Игра №4',
        'teammates': {
            'Teammate_4': 1}},
    0: {
        'date_location': 'Не смогу быть',
        'teammates': {
            'Teammate_3': 1,
            'Teammate_2': 1}}}
# Teammate (3) chose skip games (0) but has already marked skip
TEAMMATE_DECISION_7: dict[str, str | int] = {
    'teammate': 'Teammate_3',
    'game_num': 0,
    'decision': 1}
TEAM_CONFIG_EXP_7: dict[int, dict] = {
    1: {
        'date_location': 'Игра №1',
        'teammates': {
            'Teammate_1': 2}},
    2: {
        'date_location': 'Игра №2',
        'teammates': {}},
    3: {
        'date_location': 'Игра №3',
        'teammates': {
            'Teammate_1': 1,
            'Teammate_2': 1,
            'Teammate_4': 1}},
    4: {
        'date_location': 'Игра №4',
        'teammates': {
            'Teammate_2': 3,
            'Teammate_4': 1}},
    0: {
        'date_location': 'Не смогу быть',
        'teammates': {
            'Teammate_3': 1}}}
# Teammate (3) chose new game date (2) but has already marked 0
TEAMMATE_DECISION_8: dict[str, str | int] = {
    'teammate': 'Teammate_3',
    'game_num': 2,
    'decision': 1}
TEAM_CONFIG_EXP_8: dict[int, dict] = {
    1: {
        'date_location': 'Игра №1',
        'teammates': {
            'Teammate_1': 2}},
    2: {
        'date_location': 'Игра №2',
        'teammates': {
            'Teammate_3': 1}},
    3: {
        'date_location': 'Игра №3',
        'teammates': {
            'Teammate_1': 1,
            'Teammate_2': 1,
            'Teammate_4': 1}},
    4: {
        'date_location': 'Игра №4',
        'teammates': {
            'Teammate_2': 3,
            'Teammate_4': 1}},
    0: {
        'date_location': 'Не смогу быть',
        'teammates': {}}}


@pytest.mark.parametrize('teammate_decision, expected', [
    (TEAMMATE_DECISION_1, TEAM_CONFIG_EXP_1),
    (TEAMMATE_DECISION_2, TEAM_CONFIG_EXP_2),
    (TEAMMATE_DECISION_3, TEAM_CONFIG_EXP_3),
    (TEAMMATE_DECISION_4, TEAM_CONFIG_EXP_4),
    (TEAMMATE_DECISION_5, TEAM_CONFIG_EXP_5),
    (TEAMMATE_DECISION_6, TEAM_CONFIG_EXP_6),
    (TEAMMATE_DECISION_7, TEAM_CONFIG_EXP_7),
    (TEAMMATE_DECISION_8, TEAM_CONFIG_EXP_8),
])
def test_rebuild_team_config(teammate_decision, expected):
    """Test rebuild_team_config func from app_telegram."""
    # For unknown reasons in that case TEAM_CONFIG_INITIAL is changed too
    # with test_team_config.
    # test_team_config: dict[int, dict] = TEAM_CONFIG_INITIAL.copy()
    test_team_config: dict[int, dict] = {
        1: {
            'date_location': 'Игра №1',
            'teammates': {
                'Teammate_1': 2}},
        2: {
            'date_location': 'Игра №2',
            'teammates': {}},
        3: {
            'date_location': 'Игра №3',
            'teammates': {
                'Teammate_1': 1,
                'Teammate_2': 1,
                'Teammate_4': 1}},
        4: {
            'date_location': 'Игра №4',
            'teammates': {
                'Teammate_2': 3,
                'Teammate_4': 1}},
        0: {
            'date_location': 'Не смогу быть',
            'teammates': {
                'Teammate_3': 1}}}
    assert rebuild_team_config(
        team_config=test_team_config,
        teammate_decision=teammate_decision) == expected


"""
Skipped tests.
The tested functions call other functions that use the VkApi.method.
"""

SKIP_REASON_VERIFY_BOT: str = (
    'Currently no way to test it: '
    'init/verify bot with api.telegram.org!')

SKIP_REASON_WORK_WITH_MESSAGE: str = (
    'Currently no way to test it: '
    'use api.telegram "message"/"photo" methods!')


@pytest.mark.skip(reason=SKIP_REASON_VERIFY_BOT)
def test_check_telegram_bot_response():
    """Test check_telegram_bot_response func from app_telegram."""
    pass


@pytest.mark.skip(reason=SKIP_REASON_WORK_WITH_MESSAGE)
def test_edit_message():
    """Test edit_message func from app_telegram."""
    pass


@pytest.mark.skip(reason=SKIP_REASON_VERIFY_BOT)
def test_init_telegram_bot():
    """Test init_telegram_bot func from app_telegram."""
    pass


@pytest.mark.skip(reason=SKIP_REASON_WORK_WITH_MESSAGE)
def test_send_message():
    """Test send_message func from app_telegram."""
    pass


@pytest.mark.skip(reason=SKIP_REASON_WORK_WITH_MESSAGE)
def test_send_update_message():
    """Test send_update_message func from app_telegram."""
    pass


@pytest.mark.skip(reason=SKIP_REASON_WORK_WITH_MESSAGE)
def test_send_update_wall():
    """Test send_update_wall func from app_telegram."""
    pass


@pytest.mark.skip(reason=SKIP_REASON_WORK_WITH_MESSAGE)
def test_pin_message():
    """Test _pin_message func from app_telegram."""
    pass


@pytest.mark.skip(reason=SKIP_REASON_WORK_WITH_MESSAGE)
def test_send_message_for_game_dates():
    """Test _send_message_for_game_dates func from app_telegram."""
    pass


@pytest.mark.skip(reason=SKIP_REASON_WORK_WITH_MESSAGE)
def test_send_photo():
    """Test _send_photo func from app_telegram."""
    pass
