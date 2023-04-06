from project.app_telegram import rebuild_team_config

from project.data.app_data import TEAM_CONFIG

from tests.test_main import GAP, GAP_DASH, GREEN_PASSED, NL, RED_FAILED


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
        print(f'test_define_post_topic {GREEN_PASSED}')
    else:
        print(f'test_define_post_topic {RED_FAILED}')
        for num, result, expected in errors:
            print(
                f"{GAP_DASH}For {num} position in game_dates:{NL}"
                f"{GAP}Expected: '{expected}'{NL}"
                f"{GAP}     Got: '{result}'")
    return
