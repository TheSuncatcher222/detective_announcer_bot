import pytest
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from project.app_telegram import (
    form_game_dates_text, rebuild_team_config,
    _create_new_team_config_game_dates)


def test_create_new_team_config_game_dates():
    """Test _create_new_team_config_game_dates func from app_telegram."""
    pass


def test_form_game_dates_text():
    """Test form_game_dates_text func from app_telegram."""
    pass


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
