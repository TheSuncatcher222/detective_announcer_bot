from project.data.app_data import (
    MEDALS, TEAM_NAME, VK_POST_LINK, VK_GROUP_TARGET, VK_GROUP_TARGET_LOGO)

from tests.test_main import (
    GAP, GAP_DASH, GREEN_PASSED, NL, RED_FAILED, YELLOW_SKIPPED)

from tests.vk_wall_examples import (
    DETECTIT_STOP_LIST,
    EXAMPLE_CHECKIN, EXAMPLE_GAME_RESULTS, EXAMPLE_OTHER,
    EXAMPLE_PRIZE_RESULTS, EXAMPLE_PREVIEW, EXAMPLE_RATING,
    EXAMPLE_TASKS, EXAMPLE_TEAMS)

from project.app_vk import (
    findall, define_post_topic, _game_dates_add_weekday_place,
    _get_post_image_url, parse_post, _parse_post_checkin,
    _parse_post_game_results, _parse_post_preview, _parse_post_stop_list,
    _split_post_text)


def test_define_post_topic():
    post_topic_pairs: dict[dict, str] = [
        (EXAMPLE_CHECKIN, 'checkin'),
        (EXAMPLE_GAME_RESULTS, 'game_results'),
        (EXAMPLE_OTHER, 'other'),
        (EXAMPLE_PRIZE_RESULTS, 'prize_results'),
        (EXAMPLE_PREVIEW, 'preview'),
        (EXAMPLE_RATING, 'rating'),
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
                f"{GAP}Expected: '{expected}'{NL}"
                f"{GAP}     Got: '{result}'")
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
    date_format: list = _game_dates_add_weekday_place(
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
                f"{GAP}Expected: '{expected}'{NL}"
                f"{GAP}     Got: '{result}'")
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
            'expected': VK_GROUP_TARGET_LOGO},
        'uncorrect_key_post_photo': {
            'input': {'no_attachments': []},
            'input_type': 'photo',
            'expected': VK_GROUP_TARGET_LOGO},
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
            'expected': VK_GROUP_TARGET_LOGO},
        'uncorrect_key_post_album': {
            'input': {'no_attachments': []},
            'input_type': 'album',
            'expected': VK_GROUP_TARGET_LOGO}}
    errors: list = []
    for test_name in post_photo_urls:
        try:
            test_data: dict = post_photo_urls[test_name]
            result: str = _get_post_image_url(
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
                f"{GAP_DASH}In test data: '{test_name}'{NL}"
                f"{GAP}Expected: '{expected}'{NL}"
                f"{GAP}     Got: '{result}'")
    return


def test_parse_post():
    expected_results: dict = {
        'CHECKIN': {
            'post': EXAMPLE_CHECKIN,
            'post_topic': 'checkin',
            'expected_results': {
                'post_id': EXAMPLE_CHECKIN['id'],
                'post_image_url': _get_post_image_url(
                    post=EXAMPLE_CHECKIN, block='photo'),
                'post_text': _parse_post_checkin(
                    pinned_post_id=0,
                    split_text=_split_post_text(EXAMPLE_CHECKIN['text'])),
                'game_dates': None}},
        'GAME_RESULTS': {
            'post': EXAMPLE_GAME_RESULTS,
            'post_topic': 'game_results',
            'expected_results': {
                'post_id': EXAMPLE_GAME_RESULTS['id'],
                'post_image_url': _get_post_image_url(
                    post=EXAMPLE_GAME_RESULTS, block='photo'),
                'post_text': _parse_post_game_results(
                    split_text=_split_post_text(EXAMPLE_GAME_RESULTS['text']),
                    team_name=TEAM_NAME),
                'game_dates': None}},
        'OTHER': {
            'post': EXAMPLE_OTHER,
            'post_topic': 'other',
            'expected_results': {
                'post_id': EXAMPLE_OTHER['id'],
                'post_image_url': _get_post_image_url(
                    post=EXAMPLE_OTHER, block='album'),
                'post_text': _split_post_text(post_text=EXAMPLE_OTHER['text']),
                'game_dates': None}},
        'PRIZE_RESULTS': {
            'post': EXAMPLE_PRIZE_RESULTS,
            'post_topic': 'prize_results',
            'expected_results': {
                'post_id': EXAMPLE_PRIZE_RESULTS['id'],
                'post_image_url': VK_GROUP_TARGET_LOGO,
                'post_text': _split_post_text(
                    post_text=EXAMPLE_PRIZE_RESULTS['text']),
                'game_dates': None}},
        'PREVIEW': {
            'post': EXAMPLE_PREVIEW,
            'post_topic': 'preview',
            'expected_results': {
                'post_id': EXAMPLE_PREVIEW['id'],
                'post_image_url': _get_post_image_url(
                    post=EXAMPLE_PREVIEW, block='photo'),
                'post_text': _parse_post_preview(
                    post_text=EXAMPLE_PREVIEW['text'],
                    split_text=_split_post_text(EXAMPLE_PREVIEW['text']))[1],
                'game_dates': _game_dates_add_weekday_place(
                    game_dates=findall(
                        r'\d+\s\w+,\s\d+\:\d+\s\—\s\w+\s\w+\s\w+\s\w+',
                        EXAMPLE_PREVIEW['text']))}},
        'RATING': {
            'post': EXAMPLE_RATING,
            'post_topic': 'rating',
            'expected_results': {
                'post_id': EXAMPLE_RATING['id'],
                'post_image_url': _get_post_image_url(
                    post=EXAMPLE_RATING, block='photo'),
                'post_text': (
                    _split_post_text(EXAMPLE_RATING['text'])
                    + [f"{VK_POST_LINK}{VK_GROUP_TARGET}_"
                       f"{EXAMPLE_RATING['id']}"]),
                'game_dates': None}},
        'TASKS': {
            'post': EXAMPLE_TASKS,
            'post_topic': 'tasks',
            'expected_results': {
                'post_id': EXAMPLE_TASKS['id'],
                'post_image_url': _get_post_image_url(
                    post=EXAMPLE_TASKS, block='photo'),
                'post_text': (
                    _split_post_text(EXAMPLE_TASKS['text'])
                    + ['https://vk.com/alibigames?w=wall-40914100_13380']),
                'game_dates': None}},
        'TEAMS': {
            'post': EXAMPLE_TEAMS,
            'post_topic': 'teams',
            'expected_results': {
                'post_id': EXAMPLE_TEAMS['id'],
                'post_image_url': _get_post_image_url(
                    post=EXAMPLE_TEAMS, block='photo'),
                'post_text': _split_post_text(EXAMPLE_TEAMS['text'])[1:2],
                'game_dates': None}},
        'STOP_LIST': {
            'post': DETECTIT_STOP_LIST,
            'post_topic': 'stop-list',
            'expected_results': {
                'post_id': DETECTIT_STOP_LIST['id'],
                'post_image_url': _get_post_image_url(
                    post=DETECTIT_STOP_LIST, block='photo'),
                'post_text': _parse_post_stop_list(
                    post=DETECTIT_STOP_LIST,
                    split_text=_split_post_text(DETECTIT_STOP_LIST['text']),
                    team_name=TEAM_NAME),
                'game_dates': None}}}
    errors: list = []
    errors_extra: list = []
    for post_type in expected_results:
        post_data: dict = expected_results[post_type]
        result_post: dict = parse_post(
            pinned_post_id=0,
            post=post_data['post'],
            post_topic=post_data['post_topic'])
        for expected_key in post_data['expected_results']:
            try:
                result: any = result_post.get(expected_key, None)
                expected: any = post_data['expected_results'][expected_key]
                assert result == expected
            except AssertionError:
                if (post_type == 'GAME_RESULTS' 
                    and TEAM_NAME not in EXAMPLE_GAME_RESULTS['text']):
                    errors_extra.append(
                        f"    - test for {post_type} {YELLOW_SKIPPED} due to "
                        "TEAM_NAME not in post's test! Change TEAM_NAME in "
                        ".env to 'Винтажный газогенератор'")
                    break
                errors.append((post_type, expected_key, result, expected))
    if not errors:
        print(f'test_parse_post {GREEN_PASSED}')
    else:
        print(f'test_parse_post {RED_FAILED}')
        for post_type, expected_key, result, expected in errors:
            print(
                f"{GAP_DASH}For '{post_type}' and key {expected_key}{NL}"
                f"{GAP}Expected: '{expected}'{NL}"
                f"{GAP}     Got: '{result}'")
    if errors_extra:
        for error in errors_extra:
            print(error)
    return


def test_parse_post_checkin():
    post_id: int = 100500
    split_text: list[str] = _split_post_text(EXAMPLE_CHECKIN['text'])
    expected_text: list[str] = [
        'Регистрация. India',
        'Ссылка на регистрацию:',
        'https://vk.com/app5619682_-40914100',
        'Действует розыгрыш бесплатного входа на всю команду! '
        'Чтобы принять в нем участие, нужно вступить в группу и сделать '
        'репост этой записи:',
        f"{VK_POST_LINK}{VK_GROUP_TARGET}_{post_id}",
        'Результаты будут в ночь с 26 на 27 марта.']
    errors: list = []
    result_text = _parse_post_checkin(
        split_text=split_text, pinned_post_id=post_id)
    try:
        assert len(result_text) == len(expected_text)
    except AssertionError:
        print(
            f'test_parse_post_checkin {RED_FAILED}{NL}'
            f"{GAP}Expected: {len(expected_text)} abstracts{NL}"
            f"{GAP}     Got: {len(result_text)} abstracts")
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
                f"{GAP}Expected: '{expected}'{NL}"
                f"{GAP}     Got: '{result}'")
    return


def test_parse_post_game_results():
    expected_text_base: list[str] = [
        'Новая неделя — новые игры! В понедельник, в секретном месте на '
        'Горьковской мы с вами начали серию India. И теперь готовы поделиться '
        'результатами первой игры.',
        '▪5 место: «Речевые аутисты»',
        'Ну, благо речь на игре нужна в последнюю очередь — все ответы '
        'принимаются в письменном виде. И с этим команда справилась '
        'отлично 🎉',
        '▪4 место: «Босс молокосос и компания»',
        'Ох уж этот пятый тур… Но наш опыт показывает: те, кто уверенно '
        'держался в течение всей игры, не особенно пострадают от неудачи в '
        'самом конце. Так и вышло 🎊',
        '▪3 место: «Котики Киану Ривза»',
        'Всем котикам — по медали. Бронзовой! 🐱',
        '▪2 место: «Мы так и думали»',
        'Думать — это хорошо. Хорошо думать — ещё лучше. От этого бывают '
        'первые места, награды и другие приятные штуки 😉',
        '▪1 место: «Винтажный газогенератор»',
        'Удивительная машина — генерирует умные мысли и правильные ответы 🥂',
        'А впереди ещё четыре игры! Посмотрим, как справятся другие '
        'детективные агентства.']
    expected_text_base_len = len(expected_text_base)
    expected_dict = {
        'team_out': {
            'team_name': '13sda112fdssf3',
            'expected_text_last': expected_text_base[-1],
            'expected_len': expected_text_base_len},
        'team_5th': {
            'team_name': 'Речевые аутисты',
            'expected_text_last': MEDALS['5th'][0],
            'expected_len': expected_text_base_len + 1},
        'team_4th': {
            'team_name': 'Босс молокосос и компания',
            'expected_text_last': MEDALS['4th'][0],
            'expected_len': expected_text_base_len + 1},
        'team_3th': {
            'team_name': 'Котики Киану Ривза',
            'expected_text_last': MEDALS['3th'][0],
            'expected_len': expected_text_base_len + 1},
        'team_2th': {
            'team_name': 'Мы так и думали',
            'expected_text_last': MEDALS['2th'][0],
            'expected_len': expected_text_base_len + 1},
        'team_1th': {
            'team_name': 'Винтажный газогенератор',
            'expected_text_last': MEDALS['1th'][0],
            'expected_len': expected_text_base_len + 1}}
    errors: list = []
    for team in expected_dict:
        try:
            split_text: list[str] = _split_post_text(
                EXAMPLE_GAME_RESULTS['text'])
            data: dict[str] = expected_dict[team]
            result_text: list = _parse_post_game_results(
                split_text=split_text, team_name=data['team_name'])
            result: int = len(result_text)
            expected: int = data['expected_len']
            assert result == expected
            result = result_text[-1]
            expected = data['expected_text_last']
            assert result == expected
        except AssertionError:
            errors.append((team, result, expected))
    if not errors:
        print(f'parse_post_game_results {GREEN_PASSED}')
    else:
        print(f'parse_post_game_results {RED_FAILED}')
        for team, result, expected in errors:
            print(
                f"{GAP_DASH}For team: {team}{NL}"
                f"{GAP}Expected: '{expected}'{NL}"
                f"{GAP}     Got: '{result}'")
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
    result_game_dates, result_text = _parse_post_preview(
        post_text=EXAMPLE_PREVIEW['text'],
        split_text=_split_post_text(post_text=EXAMPLE_PREVIEW['text']))
    errors: list = []
    for result, expected in zip(
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
                f"{GAP}Expected: '{expected}'{NL}"
                f"{GAP}     Got: '{result}'")
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
            result: list = _parse_post_stop_list(
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
                f"{GAP}Expected: '{expected}'{NL}"
                f"{GAP}     Got: '{result}'")
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
        'https://vk.com/app5619682_-40914100']
    errors: list = []
    result_text = _split_post_text(post_text=post_text)
    try:
        assert len(result_text) == len(expected_text)
    except AssertionError:
        print(
            f'test_split_post_text {RED_FAILED}{NL}'
            f"{GAP}Expected: {len(expected_text)} abstracts{NL}"
            f"{GAP}     Got: {len(result_text)} abstracts")
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
                f"{GAP}Expected: '{expected}'{NL}"
                f"{GAP}     Got: '{result}'")
    return False
