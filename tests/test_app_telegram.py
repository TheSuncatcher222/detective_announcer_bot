import pytest
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from project.app_telegram import (
    form_game_dates_text, rebuild_team_config,
    _create_new_team_config_game_dates)

from project.data.app_data import (
    ALIBI, ALIBI_TAG, DETECTIT, DETECTIT_TAG, EMOJI_SYMBOLS)

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


GAME_DATES_TEAM_CONFIG = {
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
GAME_DATES_TEXT_EXP: str = (
    '{tag}\n'
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
    '{skip_symbol} Не смогу быть\n'
    '• Teammate_3\n')


@pytest.mark.parametrize('group_name, tag, skip_symbol', [
    (ALIBI, ALIBI_TAG, EMOJI_SYMBOLS[ALIBI]['skip']),
    (DETECTIT, DETECTIT_TAG, EMOJI_SYMBOLS[DETECTIT]['skip'])])
def test_form_game_dates_text(group_name, tag, skip_symbol):
    """Test form_game_dates_text func from app_telegram."""
    assert form_game_dates_text(
        group_name=group_name,
        game_dates=GAME_DATES_TEAM_CONFIG
        ) == GAME_DATES_TEXT_EXP.format(tag=tag, skip_symbol=skip_symbol)


def test_rebuild_team_config():
    """Test rebuild_team_config func from app_telegram."""
    pass


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
