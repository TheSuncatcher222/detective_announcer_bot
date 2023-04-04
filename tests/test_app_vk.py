# Ничего не вводить
# Вводить некорректный тип данных
# Вводить невалидные данные
# Вводить неверное количество данных

from tests.test_main import GREEN_PASSED, NL, RED_FAILED

from tests.vk_wall_examples import (
    DETECTIT_STOP_LIST,
    EXAMPLE_CHECKIN, EXAMPLE_OTHER, EXAMPLE_PRIZE_RESULTS, EXAMPLE_PREVIEW,
    EXAMPLE_RATING, EXAMPLE_RESULTS, EXAMPLE_TEAMS)

from project.app_vk import (
    define_post_topic, game_dates_add_weekday_place, get_post_image_url,
    parse_post_preview, parse_post_stop_list, split_post_text)


def test_define_post_topic():
    post: dict[str] = EXAMPLE_CHECKIN
    assert define_post_topic(post=post) == 'checkin'
    post = EXAMPLE_OTHER
    assert define_post_topic(post=post) == 'other'
    post = EXAMPLE_PRIZE_RESULTS
    assert define_post_topic(post=post) == 'prize_results'
    post = EXAMPLE_PREVIEW
    assert define_post_topic(post=post) == 'preview'
    post = EXAMPLE_RATING
    assert define_post_topic(post=post) == 'rating'
    post = EXAMPLE_RESULTS
    assert define_post_topic(post=post) == 'results'
    post = EXAMPLE_TEAMS
    assert define_post_topic(post=post) == 'teams'

    print(f'test_define_post_topic {GREEN_PASSED}')
    return


def test_game_dates_add_weekday_place():
    GAME_DATES_INPUT: list[str] = [
        '17 марта, 19:00 — секретное место на Чернышевской',
        '21 апреля, 19:00 — секретное место на Горьковской',
        '23 марта, 19:00 — секретное место на Василеостровской',
        '31 декабря, 23:59 — секретное место в нигде',
        '01 января, 00:00 — ']
    # Results are valid until December 31th 2023 23:59!
    GAME_DATES_OUTPUT: list[str] = [
        '17 марта (вс), 19:00 — Дворец «Олимпия» '
        '(Литейный пр., д. 14, ст.м. Чернышевская)',
        '21 апреля (пт), 19:00 — ParkKing '
        '(Александровский Парк, 4, ст.м. Горьковская)',
        '23 марта (сб), 19:00 — Цинь '
        '(16-я лин. B.O., 83, ст.м. Василеостровская)',
        '31 декабря (вс), 23:59 — секретное место в нигде',
        '01 января (пн), 00:00 — ']
    date_format = game_dates_add_weekday_place(game_dates=GAME_DATES_INPUT)
    for date in range(len(GAME_DATES_INPUT)):
        assert date_format[date] == GAME_DATES_OUTPUT[date], (
            f'Format {RED_FAILED}!{NL}'
            f'Input:   {GAME_DATES_INPUT[date]}{NL}'
            f'Result:  {date_format[date]}{NL}'
            f'Correct: {GAME_DATES_OUTPUT[date]}')
    print(f'test_game_dates_add_weekday_place {GREEN_PASSED}')
    return


def test_get_post_image_url():
    correct_post_photo = {
        'attachments': [
            {'photo': {
                'sizes': [
                    None,
                    None,
                    None,
                    None,
                    {'url': 'http://some-url.com'}]}}]}
    result = get_post_image_url(post=correct_post_photo, block='photo')
    correct = 'http://some-url.com'
    assert result == correct, (
        f'Get media URL with correct_post_photo {RED_FAILED}{NL}'
        f'Result:  {result}{NL}Correct: {correct}')

    uncorrect_url_post_photo = {
        'attachments': [
            {'photo': {
                'sizes': [
                    None,
                    None,
                    None,
                    None,
                    {'url': 'some-url.com'}]}}]}
    result = get_post_image_url(post=uncorrect_url_post_photo, block='photo')
    assert result is None, (
        f'Get media URL with uncorrect_url_post_photo {RED_FAILED}{NL}'
        f'Result:  {result}{NL}Correct: None')

    uncorrect_key_post_photo = {'no_attachments': []}
    result = get_post_image_url(post=uncorrect_key_post_photo, block='photo')
    assert result is None, (
        f'Get media URL with uncorrect_key_post_photo {RED_FAILED}{NL}'
        f'Result:  {result}{NL}Correct: None')

    correct_post_album = {
        'attachments': [
            {'album': {
                'thumb': {
                    'sizes': [
                        None,
                        None,
                        None,
                        {'url': 'http://some-url.com'}]}}}]}
    result = get_post_image_url(post=correct_post_album, block='album')
    correct = 'http://some-url.com'
    assert result == correct, (
        f'Get media URL with correct_post_album {RED_FAILED}{NL}'
        f'Result:  {result}{NL}Correct: {correct}')

    uncorrect_url_post_album = {
        'attachments': [
            {'album': {
                'thumb': {
                    'sizes': [
                        None,
                        None,
                        None,
                        {'url': 'some-url.com'}]}}}]}
    result = get_post_image_url(post=uncorrect_url_post_album, block='album')
    assert result is None, (
        f'Get media URL with uncorrect_url_post_album {RED_FAILED}{NL}'
        f'Result:  {result}{NL}Correct: None')

    uncorrect_key_post_album = {'no_attachments': []}
    result = get_post_image_url(post=uncorrect_key_post_album, block='album')
    assert result is None, (
        f'Get media URL with uncorrect_key_post_album {RED_FAILED}{NL}'
        f'Result:  {result}{NL}Correct: None')

    print(f'test_get_post_image_url {GREEN_PASSED}')
    return


def test_parse_post_preview():
    correct_game_dates = [
        '27 марта (ср), 19:00 — ParkKing '
        '(Александровский Парк, 4, ст.м. Горьковская)',
        '28 марта (чт), 19:00 — ParkKing '
        '(Александровский Парк, 4, ст.м. Горьковская)',
        '30 марта (сб), 19:00 — Дворец «Олимпия» '
        '(Литейный пр., д. 14, ст.м. Чернышевская)',
        '2 апреля (вс), 19:00 — Дворец «Олимпия» '
        '(Литейный пр., д. 14, ст.м. Чернышевская)',
        '3 апреля (пн), 19:00 — ParkKing '
        '(Александровский Парк, 4, ст.м. Горьковская)'
    ]
    correct_text = [
        'Анонс. India',         
        'Индия, 2006 год.',
        'Между сезонами монсунов, затяжных дождей, волна жестоких, кровавых '
        'преступлений захлестнула север Индии. Массовые убийства местных и '
        'туристов держали людей в ужасе в течение нескольких месяцев. Пара '
        'французов, турист из Бразилии, а жертвы среди местного населения и '
        'вовсе исчислялись десятками...',
        'Все в порезах. Некоторые — без глаз. И с кулонами в форме '
         'полумесяца на шее. Что это было? Предстоит разобраться',
         #  'Детективы, мы отправляемся в Индию, самое время выбрать '
         #  'даты расследования:',
         #  '— 27 марта, 19:00 — секретное место на Горьковской;',
         #  '— 28 марта, 19:00 — секретное место на Горьковской;',
         #  '— 30 марта, 19:00 — секретное место на Чернышевской;',
         #  '— 2 апреля, 19:00 — секретное место на Чернышевской;',
         #  '— 3 апреля, 19:00 — секретное место на Горьковской.',
         'Старт регистрации 22 марта в 18:05.',
         # 'Первые 5 зарегистрировавшихся команд играют по специальной '
         # 'цене — 400 рублей с детектива! Рекомендуем подписаться '
         # 'на обновления группы.,
         # '#alibispb #alibi_preview #новыйпроект #СообщениеоПреступлении'
    ]
    result_game_dates, result_text = parse_post_preview(
        post_text=EXAMPLE_PREVIEW['text'],
        split_text=split_post_text(post_text=EXAMPLE_PREVIEW['text']))
    for i in range(len(correct_game_dates)):
        assert result_game_dates[i].strip() == correct_game_dates[i], (
            f"Parse 'preview' (game dates) {RED_FAILED}!{NL}"
            f'Current paragraph: "{result_game_dates[i].strip()}"{NL}'
            f'Valid paragraph:   "{correct_game_dates[i]}"')
    for i in range(len(correct_text)):
        assert result_text[i].strip() == correct_text[i], (
            f"Parse 'preview' (text) {RED_FAILED}!{NL}"
            f'Current paragraph: "{result_text[i].strip()}"{NL}'
            f'Valid paragraph:   "{correct_text[i]}"')
    print(f'test_parse_post_preview {GREEN_PASSED}')
    return


def test_parse_post_stop_list():
    split_text: list = ['Тек №1', 'Тек №2', 'Тек удалить']
    result = parse_post_stop_list(
        post=DETECTIT_STOP_LIST,
        split_text=split_text,
        team_name='Пингвиннннннннннннннннннн')
    correct = [
        'Команда допущена к регистрации на серию игр!', 'Тек №1', 'Тек №2']
    assert result == correct, (
            f"Parse 'stop-list' with non exists team {RED_FAILED}!{NL}"
            f'Result:  {result}{NL}Correct: {correct}')

    result = parse_post_stop_list(
        post=DETECTIT_STOP_LIST,
        split_text=split_text,
        team_name='Пингвины')
    correct = [
        'Команда уже была на представленной серии игр!', 'Тек №1', 'Тек №2']
    assert result == correct, (
            f"Parse 'stop-list' with exists team {RED_FAILED}!{NL}"
            f'Result:  {result}{NL}Correct: {correct}')

    print(f'test_parse_post_stop_list {GREEN_PASSED}')
    return


def test_split_post_text():
    post_text: str = (
        'Регистрация. India\n'
        'Индия, 2006 год.\n\n'
        'Между сезонами монсунов, волна преступлений захлестнула север Индии. '
        'Что это было? Предстоит разобраться\n \n'
        'Ссылка на регистрацию: \n'
        'https://vk.com/app5619682_-40914100\n    \n'
        '#alibispb #alibi_checkin #новыйпроект #СообщениеоПреступлении\n')
    correct: list[str] = [
        'Регистрация. India',
        'Индия, 2006 год.',
        'Между сезонами монсунов, волна преступлений захлестнула север Индии. '
        'Что это было? Предстоит разобраться',
        'Ссылка на регистрацию: ',
        'https://vk.com/app5619682_-40914100',
        '#alibispb #alibi_checkin #новыйпроект #СообщениеоПреступлении']
    result = split_post_text(post_text=post_text)
    for i in range(len(result)):
        assert result[i] == correct[i], (
            f'Text fixed {RED_FAILED}{NL}'
            f'Current paragraph: "{result[i]}"{NL}'
            f'Valid paragraph:   "{correct[i]}"')
    print(f'test_fix_post_text {GREEN_PASSED}')
    return
