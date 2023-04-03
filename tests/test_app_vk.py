# Ничего не вводить
# Вводить некорректный тип данных
# Вводить невалидные данные
# Вводить неверное количество данных

from tests.vk_wall_examples import (
    EXAMPLE_CHECKIN, EXAMPLE_OTHER, EXAMPLE_PRIZE_RESULTS, EXAMPLE_PREVIEW,
    EXAMPLE_RATING, EXAMPLE_RESULTS, EXAMPLE_TEAMS)

from project.app_vk import define_post_topic, game_dates_add_weekday_place


def test_define_post_topic():
    post: dict[str] = EXAMPLE_CHECKIN
    assert define_post_topic(post) == 'checkin'
    post = EXAMPLE_OTHER
    assert define_post_topic(post) == 'other'
    post = EXAMPLE_PRIZE_RESULTS
    assert define_post_topic(post) == 'prize_results'
    post = EXAMPLE_PREVIEW
    assert define_post_topic(post) == 'preview'
    post = EXAMPLE_RATING
    assert define_post_topic(post) == 'rating'
    post = EXAMPLE_RESULTS
    assert define_post_topic(post) == 'results'
    post = EXAMPLE_TEAMS
    assert define_post_topic(post) == 'teams'

    print('test_json_data_read_write PASSED')
    return


def test_game_dates_add_weekday_place():
    NL = '\n'
    GAME_DATES_INPUT: list[str] = [
        '17 марта, 19:00 — секретное место на Чернышевской',
        '21 апреля, 19:00 — секретное место на Горьковской',
        '23 марта, 19:00 — секретное место на Василеостровской',
        '31 декабря, 23:59 — секретное место в нигде',
        '01 января, 00:00 — ']
    # Results are valid until December 31th 2023 23:59!
    GAME_DATES_OUTPUT: list[str] = [
        '17 марта (вс), 19:00 — Дворец «Олимпия» (Литейный пр., д. 14, ст.м. Чернышевская)',
        '21 апреля (пт), 19:00 — ParkKing (Александровский Парк, 4, ст.м. Горьковская)',
        '23 марта (сб), 19:00 — Цинь (16-я лин. B.O., 83, ст.м. Василеостровская)',
        '31 декабря (вс), 23:59 — секретное место в нигде',
        '01 января (пн), 00:00 — ']
    date_format = game_dates_add_weekday_place(GAME_DATES_INPUT)
    for date in range(len(GAME_DATES_INPUT)):
        assert date_format[date] == GAME_DATES_OUTPUT[date], (
            f'Format FAILED!{NL}INPUT: {GAME_DATES_INPUT[date]}{NL}'
            f'FORMAT: {date_format[date]}{NL}CORRECT: {GAME_DATES_OUTPUT[date]}')
    print('test_game_dates_add_weekday_place PASSED')
    return
