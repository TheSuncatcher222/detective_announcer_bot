from project.app_telegram import form_game_dates_text, rebuild_team_config

from project.data.app_data import TEAM_CONFIG

from tests.test_main import GAP, GAP_DASH, GREEN_PASSED, NL, RED_FAILED


def test_form_game_dates_text():
    game_dates = {
        0: {
                'date_location': 'Не смогу быть',
                'teammates_count': 0,
                'teammates': {}},
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
                    'user_10': 1}}}
    result = form_game_dates_text(game_dates)
    expected: str = (
        '————————————\n'
        '1️⃣ Какая-та локация №1 | 4\n'
        '————————————\n'
        'user_1: 2\n'
        'user_2: 1\n'
        'user_3: 1\n'
        '————————————\n'
        '2️⃣ Другая локация в 18:00 | 5\n'
        '————————————\n'
        'user_1: 4\n'
        'user_10: 1\n'
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
                f"Expected: {NL}{expected}{NL}"
                f"Got: {NL}{result}")
    return


def test_rebuild_team_config():
    team_config = TEAM_CONFIG
    game_dates = ['Игра № 2', 'Игра № 1', 'Игра № 3']
    rebuild_team_config(
        create_new=True, team_config=team_config, game_dates=game_dates)
    expected_dict = {
        'last_message_id': None,
        'game_dates': {
            0: {
                'date_location': 'Не смогу быть',
                'teammates_count': 0,
                'teammates': {}},
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
                'teammates': {}}}}
    errors: list = []
    for num in expected_dict['game_dates']:
        try:
            result = team_config['game_dates'][num]
            expected = expected_dict['game_dates'][num]
            assert result == expected
        except AssertionError:
            errors.append((num, result, expected))
    if not errors:
        print(f'test_rebuild_team_config {GREEN_PASSED}')
    else:
        print(f'test_rebuild_team_config {RED_FAILED}')
        for num, result, expected in errors:
            print(
                f"{GAP_DASH}For {num} position in game_dates:{NL}"
                f"{GAP}Expected: '{expected}'{NL}"
                f"{GAP}     Got: '{result}'")
    return
