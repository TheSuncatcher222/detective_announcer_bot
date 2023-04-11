from project.app_telegram import (
    create_new_team_config_game_dates,
    form_game_dates_text, rebuild_team_config_game_dates)

from project.data.app_data import TEAM_CONFIG, TEAM_GUEST

from tests.test_main import GAP, GAP_DASH, GREEN_PASSED, NL, RED_FAILED


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
                'teammates': {}},
            2: {
                'date_location': 'Игра № 1',
                'teammates': {}},
            3: {
                'date_location': 'Игра № 3',
                'teammates': {}},
            0: {
                'date_location': 'Не смогу быть',
                'teammates': {}}}}
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


def test_form_game_dates_text():
    game_dates = {
        1: {
                'date_location': 'Какая-та локация №1',
                'teammates': {
                    'user_1': 2,
                    'user_2': 1,
                    'user_3': 1}},
        2: {
                'date_location': 'Другая локация в 18:00',
                'teammates': {
                    'user_1': 4,
                    'user_10': 1}},
        0: {
                'date_location': 'Не смогу быть',
                'teammates': {}}}
    result = form_game_dates_text(game_dates)
    expected: str = (
        '1️⃣ Какая-та локация №1\n'
        '• user_1\n'
        f'• user_1 {TEAM_GUEST}\n'
        '• user_2\n'
        '• user_3\n'
        '\n'
        '2️⃣ Другая локация в 18:00\n'
        '• user_1\n'
        f'• user_1 {TEAM_GUEST}\n'
        f'• user_1 {TEAM_GUEST}\n'
        f'• user_1 {TEAM_GUEST}\n'
        '• user_10\n'
        '\n'
        '🚫 Не смогу быть\n')
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


def test_rebuild_team_config_game_dates():
    team_config: dict = {
        'last_message_id': None,
        'game_count': 3,
        'game_dates': {
            1: {
                'date_location': 'Игра № 2',
                'teammates': {
                    'user_1': 2,
                    'user_2': 1,
                    'user_3': 1}},
            2: {
                'date_location': 'Игра № 1',
                'teammates': {
                    'user_1': 2,
                    'user_2': 2,
                    'user_4': 1}},
            3: {
                'date_location': 'Игра № 3',
                'teammates': {
                    'user_2': 2,
                    'user_5': 1}},
            0: {
                'date_location': 'Не смогу быть',
                'teammates': {
                    'user_6': 1,
                    'user_7': 1}}}}
    decision_1: dict = {
        'teammate': 'user_6',
        'game_num': 0,
        'decision': 1}
    expected_1: dict = {
        'last_message_id': None,
        'game_count': 3,
        'game_dates': {
            1: {
                'date_location': 'Игра № 2',
                'teammates': {
                    'user_1': 2,
                    'user_2': 1,
                    'user_3': 1}},
            2: {
                'date_location': 'Игра № 1',
                'teammates': {
                    'user_1': 2,
                    'user_2': 2,
                    'user_4': 1}},
            3: {
                'date_location': 'Игра № 3',
                'teammates': {
                    'user_2': 2,
                    'user_5': 1}},
            0: {
                'date_location': 'Не смогу быть',
                'teammates': {
                    'user_6': 1,
                    'user_7': 1}}}}
    decision_2: dict = {
        'teammate': 'user_1',
        'game_num': 0,
        'decision': 1}
    expected_2: dict = {
        'last_message_id': None,
        'game_count': 3,
        'game_dates': {
            1: {
                'date_location': 'Игра № 2',
                'teammates': {
                    'user_2': 1,
                    'user_3': 1}},
            2: {
                'date_location': 'Игра № 1',
                'teammates': {
                    'user_2': 2,
                    'user_4': 1}},
            3: {
                'date_location': 'Игра № 3',
                'teammates': {
                    'user_2': 2,
                    'user_5': 1}},
            0: {
                'date_location': 'Не смогу быть',
                'teammates': {
                    'user_6': 1,
                    'user_7': 1,
                    'user_1': 1}}}}
    decision_3: dict = {
        'teammate': 'user_2',
        'game_num': 2,
        'decision': 1}
    expected_3: dict = {
        'last_message_id': None,
        'game_count': 3,
        'game_dates': {
            1: {
                'date_location': 'Игра № 2',
                'teammates': {
                    'user_2': 1,
                    'user_3': 1}},
            2: {
                'date_location': 'Игра № 1',
                'teammates': {
                    'user_2': 3,
                    'user_4': 1}},
            3: {
                'date_location': 'Игра № 3',
                'teammates': {
                    'user_2': 2,
                    'user_5': 1}},
            0: {
                'date_location': 'Не смогу быть',
                'teammates': {
                    'user_6': 1,
                    'user_7': 1,
                    'user_1': 1}}}}
    decision_4: dict = {
        'teammate': 'user_7',
        'game_num': 1,
        'decision': 1}
    expected_4: dict = {
        'last_message_id': None,
        'game_count': 3,
        'game_dates': {
            1: {
                'date_location': 'Игра № 2',
                'teammates': {
                    'user_2': 1,
                    'user_3': 1,
                    'user_7': 1}},
            2: {
                'date_location': 'Игра № 1',
                'teammates': {
                    'user_2': 3,
                    'user_4': 1}},
            3: {
                'date_location': 'Игра № 3',
                'teammates': {
                    'user_2': 2,
                    'user_5': 1}},
            0: {
                'date_location': 'Не смогу быть',
                'teammates': {
                    'user_6': 1,
                    'user_1': 1}}}}
    decision_5: dict = {
        'teammate': 'user_7',
        'game_num': 2,
        'decision': -1}
    expected_5: dict = {
        'last_message_id': None,
        'game_count': 3,
        'game_dates': {
            1: {
                'date_location': 'Игра № 2',
                'teammates': {
                    'user_2': 1,
                    'user_3': 1,
                    'user_7': 1}},
            2: {
                'date_location': 'Игра № 1',
                'teammates': {
                    'user_2': 3,
                    'user_4': 1}},
            3: {
                'date_location': 'Игра № 3',
                'teammates': {
                    'user_2': 2,
                    'user_5': 1}},
            0: {
                'date_location': 'Не смогу быть',
                'teammates': {
                    'user_6': 1,
                    'user_1': 1}}}}
    decision_6: dict = {
        'teammate': 'user_2',
        'game_num': 3,
        'decision': -1}
    expected_6: dict = {
        'last_message_id': None,
        'game_count': 3,
        'game_dates': {
            1: {
                'date_location': 'Игра № 2',
                'teammates': {
                    'user_2': 1,
                    'user_3': 1,
                    'user_7': 1}},
            2: {
                'date_location': 'Игра № 1',
                'teammates': {
                    'user_2': 3,
                    'user_4': 1}},
            3: {
                'date_location': 'Игра № 3',
                'teammates': {
                    'user_2': 1,
                    'user_5': 1}},
            0: {
                'date_location': 'Не смогу быть',
                'teammates': {
                    'user_6': 1,
                    'user_1': 1}}}}
    decision_7: dict = {
        'teammate': 'user_5',
        'game_num': 3,
        'decision': -1}
    expected_7: dict = {
        'last_message_id': None,
        'game_count': 3,
        'game_dates': {
            1: {
                'date_location': 'Игра № 2',
                'teammates': {
                    'user_2': 1,
                    'user_3': 1,
                    'user_7': 1}},
            2: {
                'date_location': 'Игра № 1',
                'teammates': {
                    'user_2': 3,
                    'user_4': 1}},
            3: {
                'date_location': 'Игра № 3',
                'teammates': {
                    'user_2': 1}},
            0: {
                'date_location': 'Не смогу быть',
                'teammates': {
                    'user_6': 1,
                    'user_1': 1}}}}
    tests: dict = {
        'test_1': (decision_1, expected_1),
        'test_2': (decision_2, expected_2),
        'test_3': (decision_3, expected_3),
        'test_4': (decision_4, expected_4),
        'test_5': (decision_5, expected_5),
        'test_6': (decision_6, expected_6),
        'test_7': (decision_7, expected_7)}
    errors: list = []
    for test, test_data in tests.items():
        try:
            rebuild_team_config_game_dates(
                team_config=team_config, teammate_decision=test_data[0])
            assert team_config == test_data[1]
        except AssertionError:
            errors.append((test, team_config, test_data[1]))
    if not errors:
        print(f'test_rebuild_team_config_game_dates {GREEN_PASSED}')
    else:
        print(f'test_rebuild_team_config_game_dates {RED_FAILED}')
        for test, result, expected in errors:
            print(
                f"{GAP_DASH}For {test}:{NL}"
                f"{GAP}Expected: {NL}{expected}{NL}"
                f"{GAP}Got: {NL}{result}")
    return
