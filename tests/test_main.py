import pytest
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from main import (
    check_env, file_read, file_write, file_remove, saved_data_check, )


@pytest.mark.parametrize('data, expected', [
    ((True, 13, 'adasd'), None),
    ((True, False, '1'), 'SystemExit'),
    ('', 'SystemExit'),
    ('13', 'SystemExit'),
    (None, 'SystemExit'),
    ((None, None, None, True), 'SystemExit')])
def test_check_env(data, expected):
    """Test check_env func from main."""
    try:
        result = check_env(data)
    except SystemExit:
        result = 'SystemExit'
    assert result == expected


def test_file_read():
    """Test file_read func from main."""
    pass


def test_file_write():
    """Test file_write func from main."""
    pass


def test_file_remove():
    """Test file_remove func from main."""
    pass


SAVED_DATA_1: dict = {}
EXPECTED_1: dict = {
    'last_vk_message_id_alibi': 0,
    'last_vk_message_id_detectit': 0,
    'last_vk_wall_id_alibi': 0,
    'last_vk_wall_id_detectit': 0,
    'pinned_telegram_message_id_alibi': 0,
    'pinned_telegram_message_id_detectit': 0,
    'pinned_vk_message_id_alibi': 0,
    'pinned_vk_message_id_detectit': 0,
    'team_config_alibi': {},
    'team_config_detectit': {}}
SAVED_DATA_2: dict = {
    'last_vk_message_id_alibi': 1,
    'last_vk_wall_id_detectit': 25,
    'pinned_telegram_message_id_alibi': -3,
    'pinned_telegram_message_id_detectit': 40,
    'team_config_detectit': {}}
EXPECTED_2: dict = {
    'last_vk_message_id_alibi': 1,
    'last_vk_message_id_detectit': 0,
    'last_vk_wall_id_alibi': 0,
    'last_vk_wall_id_detectit': 25,
    'pinned_telegram_message_id_alibi': -3,
    'pinned_telegram_message_id_detectit': 40,
    'pinned_vk_message_id_alibi': 0,
    'pinned_vk_message_id_detectit': 0,
    'team_config_alibi': {},
    'team_config_detectit': {}}
SAVED_DATA_3: dict = {
    'last_vk_message_id_alibi': 465345,
    'last_vk_message_id_detectit': 2313,
    'last_vk_wall_id_alibi': 241515,
    'last_vk_wall_id_detectit': 124654,
    'pinned_telegram_message_id_alibi': 15774,
    'pinned_telegram_message_id_detectit': 1210,
    'pinned_vk_message_id_alibi': 7657568,
    'pinned_vk_message_id_detectit': 9999999999999999,
    'team_config_alibi': {
        '1': {
            'date_location': 'Игра №1',
            'teammates': {
                'Teammate_1': 2}},
        '2': {
            'date_location': 'Игра №2',
            'teammates': {
                'Teammate_1': 1}},
        '0': {
            'date_location': 'Не смогу быть',
            'teammates': {
                'Teammate_3': 1}}},
    'team_config_detectit': {
        '1': {
            'date_location': 'Игра №1',
            'teammates': {
                'Teammate_1': 4}},
        '2': {
            'date_location': 'Игра №2',
            'teammates': {
                'Teammate_2': 1}},
        '3': {
            'date_location': 'Игра №3',
            'teammates': {
                'Teammate_1': 2,
                'Teammate_3': 1,
                'Teammate_4': 1}},
        '4': {
            'date_location': 'Игра №4',
            'teammates': {
                'Teammate_4': 1,
                'Teammate_4': 1}},
        '0': {
            'date_location': 'Не смогу быть',
            'teammates': {
                'Teammate_5': 1,
                'Teammate_2': 1}}}}
EXPECTED_3: dict = {
    'last_vk_message_id_alibi': 465345,
    'last_vk_message_id_detectit': 2313,
    'last_vk_wall_id_alibi': 241515,
    'last_vk_wall_id_detectit': 124654,
    'pinned_telegram_message_id_alibi': 15774,
    'pinned_telegram_message_id_detectit': 1210,
    'pinned_vk_message_id_alibi': 7657568,
    'pinned_vk_message_id_detectit': 9999999999999999,
    'team_config_alibi': {
        1: {
            'date_location': 'Игра №1',
            'teammates': {
                'Teammate_1': 2}},
        2: {
            'date_location': 'Игра №2',
            'teammates': {
                'Teammate_1': 1}},
        0: {
            'date_location': 'Не смогу быть',
            'teammates': {
                'Teammate_3': 1}}},
    'team_config_detectit': {
        1: {
            'date_location': 'Игра №1',
            'teammates': {
                'Teammate_1': 4}},
        2: {
            'date_location': 'Игра №2',
            'teammates': {
                'Teammate_2': 1}},
        3: {
            'date_location': 'Игра №3',
            'teammates': {
                'Teammate_1': 2,
                'Teammate_3': 1,
                'Teammate_4': 1}},
        4: {
            'date_location': 'Игра №4',
            'teammates': {
                'Teammate_4': 1,
                'Teammate_4': 1}},
        0: {
            'date_location': 'Не смогу быть',
            'teammates': {
                'Teammate_5': 1,
                'Teammate_2': 1}}}}


@pytest.mark.parametrize('saved_data, expected', [
    (SAVED_DATA_1, EXPECTED_1),
    (SAVED_DATA_2, EXPECTED_2),
    (SAVED_DATA_3, EXPECTED_3)])
def test_saved_data_check(saved_data, expected):
    """Test saved_data_check func from main."""
    assert saved_data_check(saved_data=saved_data) == expected


"""
Skipped tests.
The tested functions call other functions that use the VkApi.method.
"""

SKIP_REASON_ASYNC_FUNC: str = (
    'Currently no way to test it: '
    'function is async func!')
SKIP_REASON_COMPLEX_FUNCTION: str = (
    'Currently no way to test it: '
    'uses both api.telegram and vk.api!')


@pytest.mark.skip(reason=SKIP_REASON_COMPLEX_FUNCTION)
def test_vk_listen_message():
    """Test vk_listen_message func from main."""
    pass


@pytest.mark.skip(reason=SKIP_REASON_COMPLEX_FUNCTION)
def test_vk_listen_wall():
    """Test vk_listen_wall func from main."""
    pass


@pytest.mark.skip(reason=SKIP_REASON_ASYNC_FUNC)
def test_last_api_error_delete():
    """Test last_api_error_delete func from main."""
    pass


@pytest.mark.skip(reason=SKIP_REASON_ASYNC_FUNC)
def test_telegram_listener():
    """Test telegram_listener func from main."""
    pass


@pytest.mark.skip(reason=SKIP_REASON_ASYNC_FUNC)
def test_vk_listener():
    """Test vk_listener func from main."""
    pass


@pytest.mark.skip(reason=SKIP_REASON_ASYNC_FUNC)
def test_main():
    """Test main func from main."""
    pass
