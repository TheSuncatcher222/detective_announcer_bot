from project.app_telegram import (
    create_new_team_config_game_dates, form_game_dates_text)

from project.data.app_data import TEAM_CONFIG, TEAM_GUEST

from tests.test_main import GAP, GAP_DASH, GREEN_PASSED, NL, RED_FAILED


def test_form_game_dates_text():
    game_dates = {
        1: {
                'date_location': 'Какая-та локация №1',
                'teammates_count': 4,
                'teammates': {
                    'user_1': 2,
                    'user_2': 1,
                    'user_3': 1}},
        2: {
                'date_location': 'Другая локация в 18:00',
                'teammates_count': 5,
                'teammates': {
                    'user_1': 4,
                    'user_10': 1}},
        0: {
                'date_location': 'Не смогу быть',
                'teammates_count': 0,
                'teammates': {}}}
    result = form_game_dates_text(game_dates)
    expected: str = (
        '————————————\n'
        '1️⃣ Какая-та локация №1 | 4\n'
        '————————————\n'
        'user_1\n'
        f'user_1 {TEAM_GUEST}\n'
        'user_2\n'
        'user_3\n'
        '————————————\n'
        '2️⃣ Другая локация в 18:00 | 5\n'
        '————————————\n'
        'user_1\n'
        f'user_1 {TEAM_GUEST}\n'
        f'user_1 {TEAM_GUEST}\n'
        f'user_1 {TEAM_GUEST}\n'
        'user_10\n'
        '————————————\n'
        '🚫 Не смогу быть | 0\n'
        '————————————')
    errors = []
    try:
        assert result == expected
    except AssertionError:
        errors.append((result, expected))
    if not errors:
        print(f'test_form_game_dates_text {GREEN_PASSED}')
    else:
        print(f'test_form_game_dates_text {RED_FAILED}')
        for result, expected in errors:
            print(
                f"{GAP}Expected: {NL}{expected}{NL}"
                f"{GAP}Got: {NL}{result}")
    return


def test_create_new_team_config_game_dates():
    team_config = TEAM_CONFIG
    game_dates = ['Игра № 2', 'Игра № 1', 'Игра № 3']
    create_new_team_config_game_dates(
        game_dates=game_dates, team_config=team_config)
    expected_dict = {
        'last_message_id': None,
        'game_count': 3,
        'game_dates': {
            1: {
                'date_location': 'Игра № 2',
                'teammates_count': 0,
                'teammates': {}},
            2: {
                'date_location': 'Игра № 1',
                'teammates_count': 0,
                'teammates': {}},
            3: {
                'date_location': 'Игра № 3',
                'teammates_count': 0,
                'teammates': {}}},
            0: {
                'date_location': 'Не смогу быть',
                'teammates_count': 0,
                'teammates': {}}}
    errors: list = []
    errors_len: str = None
    try:
        assert team_config['game_count'] == expected_dict['game_count']
    except AssertionError:
        errors_len = (
            f"{GAP_DASH}Error in count 'game_count' value:{NL}"
            f"{GAP}Expected: {expected_dict['game_count']}{NL}"
            f"{GAP}     Got: {team_config['game_count']}")
    for num in expected_dict['game_dates']:
        try:
            result = team_config['game_dates'][num]
            expected = expected_dict['game_dates'][num]
            assert result == expected
        except AssertionError:
            errors.append((num, result, expected))
    if not errors and not errors_len:
        print(f'test_rebuild_team_config_game_dates {GREEN_PASSED}')
        return
    print(f'test_rebuild_team_config_game_dates {RED_FAILED}')
    if errors:
        for num, result, expected in errors:
            print(
                f"{GAP_DASH}For {num}th position in game_dates:{NL}"
                f"{GAP}Expected: '{expected}'{NL}"
                f"{GAP}     Got: '{result}'")
    if errors_len:
        print(errors_len)
    return
