# Ничего не вводить
# Вводить некорректный тип данных
# Вводить невалидные данные
# Вводить неверное количество данных

from project.data.app_data import VK_POST_LINK, VK_GROUP_TARGET

from tests.test_main import GREEN_PASSED, NL, RED_FAILED

from tests.vk_wall_examples import (
    DETECTIT_STOP_LIST,
    EXAMPLE_CHECKIN, EXAMPLE_OTHER, EXAMPLE_PRIZE_RESULTS, EXAMPLE_PREVIEW,
    EXAMPLE_RATING, EXAMPLE_RESULTS, EXAMPLE_TEAMS)

from project.app_vk import (
    define_post_topic, game_dates_add_weekday_place, get_post_image_url,
    parse_post_checkin, parse_post_preview, parse_post_stop_list,
    split_post_text)


def test_define_post_topic():
    post_topic_pairs: dict[dict, str] = [
        (EXAMPLE_CHECKIN, 'checkin'),
        (EXAMPLE_OTHER, 'other'),
        (EXAMPLE_PRIZE_RESULTS, 'prize_results'),
        (EXAMPLE_PREVIEW, 'preview'),
        (EXAMPLE_RATING, 'rating'),
        (EXAMPLE_RESULTS, 'results'),
        (EXAMPLE_TEAMS, 'teams')]
    errors: list = []
    for post, expected in post_topic_pairs:
        try:
            result: str = define_post_topic(post=post)
            assert result == expected
        except AssertionError:
            errors.append((result, expected))
    if not errors:
        print(f'test_define_post_topic {GREEN_PASSED}')
    else:
        print(f'test_define_post_topic {RED_FAILED}')
        for result, expected in errors:
            print(
                f"Expected: '{expected}'{NL}"
                f"     Got: '{result}'")
    return


def test_game_dates_add_weekday_place():
    game_dates_input: list[str] = [
        '17 марта, 19:00 — секретное место на Чернышевской',
        '21 апреля, 19:00 — секретное место на Горьковской',
        '23 марта, 19:00 — секретное место на Василеостровской',
        '31 декабря, 23:59 — секретное место в нигде',
        '01 января, 00:00 — ']
    # Results are valid until December 31th 2023 23:59!
    game_dates_expected: list[str] = [
        '17 марта (вс), 19:00 — Дворец «Олимпия» '
        '(Литейный пр., д. 14, ст.м. Чернышевская)',
        '21 апреля (пт), 19:00 — ParkKing '
        '(Александровский Парк, 4, ст.м. Горьковская)',
        '23 марта (сб), 19:00 — Цинь '
        '(16-я лин. B.O., 83, ст.м. Василеостровская)',
        '31 декабря (вс), 23:59 — секретное место в нигде',
        '01 января (пн), 00:00 — ']
    date_format: list = game_dates_add_weekday_place(
        game_dates=game_dates_input)
    errors: list = []
    for date in range(len(game_dates_expected)):
        try:
            result: str = date_format[date]
            expected: str = game_dates_expected[date]
            assert result == expected
        except AssertionError:
            errors.append((result, expected))
    if not errors:
        print(f'test_game_dates_add_weekday_place {GREEN_PASSED}')
    else:
        print(f'test_game_dates_add_weekday_place {RED_FAILED}')
        for result, expected in errors:
            print(
                f"Expected: '{expected}'{NL}"
                f"     Got: '{result}'")
    return


def test_get_post_image_url():
    post_photo_urls: dict = {
        'correct_post_photo': {
            'input': {
                'attachments': [
                    {'photo': {
                        'sizes': [
                            None,
                            None,
                            None,
                            None,
                            {'url': 'http://some-url.com'}]}}]},
            'input_type': 'photo',
            'expected': 'http://some-url.com'},
        'uncorrect_url_post_photo': {
            'input': {
                'attachments': [
                    {'photo': {
                        'sizes': [
                            None,
                            None,
                            None,
                            None,
                            {'url': 'some-url.com'}]}}]},
            'input_type': 'photo',
            'expected': None},
        'uncorrect_key_post_photo': {
            'input': {'no_attachments': []},
            'input_type': 'photo',
            'expected': None},
        'correct_post_album': {
            'input': {
                'attachments': [
                    {'album': {
                        'thumb': {
                            'sizes': [
                                None,
                                None,
                                None,
                                {'url': 'http://some-url.com'}]}}}]},
            'input_type': 'album',
            'expected': 'http://some-url.com'},
        'uncorrect_url_post_album': {
            'input': {
                'attachments': [
                    {'album': {
                        'thumb': {
                            'sizes': [
                                None,
                                None,
                                None,
                                {'url': 'some-url.com'}]}}}]},
            'input_type': 'album',
            'expected': None},
        'uncorrect_key_post_album': {
            'input': {'no_attachments': []},
            'input_type': 'album',
            'expected': None}}
    errors: list = []
    for test_name in post_photo_urls:
        try:
            test_data: dict = post_photo_urls[test_name]
            result: str = get_post_image_url(
                post=test_data['input'], block=test_data['input_type'])
            expected: str = test_data['expected']
            assert result == expected
        except AssertionError:
            errors.append((test_name, result, expected))
    if not errors:
        print(f'test_get_post_image_url {GREEN_PASSED}')
    else:
        print(f'test_get_post_image_url {RED_FAILED}')
        for test_name, result, expected in errors:
            print(
                f"in test data: '{test_name}'{NL}"
                f"Expected: '{expected}'{NL}"
                f"     Got: '{result}'")
    return


def test_parse_post_checkin():
    post_id: int = EXAMPLE_CHECKIN['id']
    split_text: list[str] = split_post_text(EXAMPLE_CHECKIN['text'])
    expected_text: list[str] = [
        'Регистрация. India',
        'Ссылка на регистрацию:',
        'https://vk.com/app5619682_-40914100',
        'Действует розыгрыш бесплатного входа на всю команду! '
        'Чтобы принять в нем участие, нужно вступить в группу и сделать '
        'репост этой записи:\n'
        f"{VK_POST_LINK}{VK_GROUP_TARGET}_{post_id}"]
    errors: list = []
    result_text = parse_post_checkin(split_text=split_text, post_id=post_id)
    try:
        assert len(result_text) == len(expected_text)
    except AssertionError:
        print(
            f'test_parse_post_checkin {RED_FAILED}{NL}'
            f"Expected: {len(expected_text)} abstracts{NL}"
            f"     Got: {len(result_text)} abstracts")
        return
    for result, expected in zip(result_text, expected_text):
        try:
            assert result.strip() == expected
        except AssertionError:
            errors.append((result, expected))
    if not errors:
        print(f'test_parse_post_checkin {GREEN_PASSED}')
    else:
        print(f'test_parse_post_checkin {RED_FAILED}')
        for result, expected in errors:
            print(
                f"Expected: '{expected}'{NL}"
                f"     Got: '{result}'")
    return



def test_parse_post_preview():
    # Results are valid until March 27th 2023 23:59!
    expected_game_dates = [
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
    expected_text = [
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
    errors: list = []
    for (result, expected) in zip(
            result_game_dates + result_text,
            expected_game_dates + expected_text):
        try:
            result = result.strip()
            assert result == expected
        except AssertionError:
            errors.append((result, expected))
    if not errors:
        print(f'test_parse_post_preview {GREEN_PASSED}')
    else:
        print(f'test_parse_post_preview {RED_FAILED}')
        for result, expected in errors:
            print(
                f"Expected: '{expected}'{NL}"
                f"     Got: '{result}'")
    return


def test_parse_post_stop_list():
    split_text: list = ['Тек №1', 'Тек №2', 'Тек удалить']
    teams: dict = {
        'exists_team': [
            'Пингвиныssssssssssss',
            ['Команда допущена к регистрации на серию игр!',
             'Тек №1',
             'Тек №2']],
        'non_exists_team': [
            'Пингвины',
            ['Команда уже была на представленной серии игр!',
             'Тек №1',
             'Тек №2']]}
    errors: list = []
    for team in teams:
        try:
            data: list = teams[team]
            result: list = parse_post_stop_list(
                post=DETECTIT_STOP_LIST,
                split_text=split_text,
                team_name=data[0])
            expected: list = data[1]
            assert result == expected
        except AssertionError:
            errors.append((result, expected))
    if not errors:
        print(f'test_parse_post_stop_list {GREEN_PASSED}')
    else:
        print(f'test_parse_post_stop_list {RED_FAILED}')
        for result, expected in errors:
            print(
                f"Expected: '{expected}'{NL}"
                f"     Got: '{result}'")
    return


def test_split_post_text() -> bool:
    post_text: str = (
        'Регистрация. India\n'
        'Индия, 2006 год.\n\n'
        'Между сезонами монсунов, волна преступлений захлестнула север Индии. '
        'Что это было? Предстоит разобраться\n \n'
        'Ссылка на регистрацию: \n'
        'https://vk.com/app5619682_-40914100\n    \n'
        '#alibispb #alibi_checkin #новыйпроект #СообщениеоПреступлении\n')
    expected_text: list[str] = [
        'Регистрация. India',
        'Индия, 2006 год.',
        'Между сезонами монсунов, волна преступлений захлестнула север Индии. '
        'Что это было? Предстоит разобраться',
        'Ссылка на регистрацию:',
        'https://vk.com/app5619682_-40914100',
        '#alibispb #alibi_checkin #новыйпроект #СообщениеоПреступлении']
    errors: list = []
    result_text = split_post_text(post_text=post_text)
    try:
        assert len(result_text) == len(expected_text)
    except AssertionError:
        print(
            f'test_split_post_text {RED_FAILED}{NL}'
            f"Expected: {len(expected_text)} abstracts{NL}"
            f"     Got: {len(result_text)} abstracts")
        return
    for i in range(len(result_text)-1):
        try:
            result = result_text[i].strip()
            expected = expected_text[i]
            assert result == expected
        except AssertionError:
            errors.append((result, expected))
    if not errors:
        print(f'test_split_post_text {GREEN_PASSED}')
        return True
    else:
        print(f'test_split_post_text {RED_FAILED}')
        for result, expected in errors:
            print(
                f"Expected: '{expected}'{NL}"
                f"     Got: '{result}'")
    return False
