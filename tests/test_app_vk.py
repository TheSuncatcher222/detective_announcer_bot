import pytest
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from project.app_vk import (
    define_post_topic, make_link_to_post, parse_message, parse_post,
    _game_dates_add_weekday_place, _get_post_image_url, _get_vk_chat_update,
    _get_vk_wall_update, _parse_post_add_link, _parse_post_checkin,
    _parse_post_game_results, _parse_post_other, _parse_post_preview,
    _parse_post_prize_results, _parse_post_teams, _parse_post_stop_list,
    _split_paragraphs)

from project.data.app_data import TEAM_NAME, TEAM_CAPITAN_PROP

from vk_wall_examples import (
    A_EXAMPLE_CHECKIN, A_EXAMPLE_GAME_RESULTS, A_EXAMPLE_OTHER,
    A_EXAMPLE_PREVIEW, A_EXAMPLE_PRIZE_RESULTS,
    A_EXAMPLE_RATING, A_EXAMPLE_TASKS, A_EXAMPLE_TEAMS,

    D_EXAMPLE_CHECKIN, D_EXAMPLE_GAME_RESULTS,
    D_EXAMPLE_PHOTOS, D_EXAMPLE_PREVIEW, D_EXAMPLE_PRIZE_RESULTS,
    D_EXAMPLE_STOP_LIST, D_EXAMPLE_TEAMS)

NL: str = '\n'


@pytest.mark.dependency(name="test_split_paragraphs")
@pytest.mark.parametrize('group_name, text, splitted_text', [
    ('Alibi', 'One\nTwo\n\nThree\n\n\nFour\n\n\n\nEnd.',
     ['🟣 Alibi', 'One', 'Two', 'Three', 'Four', 'End.']),
    ('Detectit', 'One\nTwo\n\nThree\n\n\nFour\n\n\n\nEnd.',
     ['⚫️ Detectit', 'One', 'Two', 'Three', 'Four', 'End.'])])
def test_split_paragraphs(group_name, text, splitted_text):
    """Test test_split_paragraphs func from app_vk."""
    assert _split_paragraphs(group_name=group_name, text=text) == splitted_text


@pytest.mark.dependency(name="test_define_post_topic")
@pytest.mark.parametrize('post_example, expected_topic', [
    (A_EXAMPLE_CHECKIN, 'checkin'),
    (A_EXAMPLE_GAME_RESULTS, 'game_results'),
    (A_EXAMPLE_OTHER, 'other'),
    # (A_EXAMPLE_PHOTOS, TypeError),
    (A_EXAMPLE_PREVIEW, 'preview'),
    (A_EXAMPLE_PRIZE_RESULTS, 'prize_results'),
    (A_EXAMPLE_RATING, 'rating'),
    # (A_EXAMPLE_STOP_LIST, TypeError),
    (A_EXAMPLE_TASKS, 'tasks'),
    (A_EXAMPLE_TEAMS, 'teams'),
    (D_EXAMPLE_CHECKIN, 'checkin'),
    (D_EXAMPLE_GAME_RESULTS, 'game_results'),
    # (D_EXAMPLE_OTHER, TypeError),
    (D_EXAMPLE_PHOTOS, 'photos'),
    (D_EXAMPLE_PREVIEW, 'preview'),
    (D_EXAMPLE_PRIZE_RESULTS, 'prize_results'),
    # (D_EXAMPLE_RATING, TypeError),
    (D_EXAMPLE_STOP_LIST, 'stop-list'),
    # (D_EXAMPLE_TASKS, TypeError),
    (D_EXAMPLE_TEAMS, 'teams')])
def test_define_post_topic(post_example, expected_topic) -> None:
    """Test define_post_topic func from app_vk."""
    assert define_post_topic(post_example) == expected_topic


@pytest.mark.dependency(name="test_game_dates_add_weekday_place")
@pytest.mark.parametrize('game_date, expected', [
    ('1 июня, 19:00 — секретное место на Василеостровской',
     '1 июня (ЧТ), 19:00 — ресторан Цинь (16-я лин. B.O., 83)'),
    ('7 июля, 19:30 — секретное место на Горьковской',
     '7 июля (ПТ), 19:30 — ресторан Parkking (Александровский парк, 4)'),
    ('22 августа, 12:13 — секретное место на Петроградской',
     '22 августа (ВТ), 12:13 — ресторан Unity на Петроградской '
     '(наб. Карповки, 5к17)'),
    ('11 сентября, 00:00 — секретное место на Площади Ленина',
     '11 сентября (ПН), 00:00 — Центр Kod (ул. Комсомола, 2)'),
    ('18 октября, 23:59 — секретное место на Сенной',
     '18 октября (СР), 23:59 — ресторан Unity на Сенной (пер. Гривцова, 4)'),
    ('25 ноября, 11:11 — секретное место на Чернышевской',
     '25 ноября (СБ), 11:11 — Дворец Олимпия (Литейный пр., 14)'),
    ('31 декабря, 23:59 — секретное место в нигде',
     '31 декабря (ВС), 23:59 — секретное место в нигде')])
def test_game_dates_add_weekday_place(game_date, expected):
    """Test _game_dates_add_weekday_place func from app_vk."""
    assert _game_dates_add_weekday_place([game_date]) == [expected], (
        'In tested func datetime.datetime.now() is used! '
        'Due to this - if error caused by abbreviation for the day of the '
        'week - correct data according calendar in expected value or change '
        'date in game_date.')


@pytest.mark.dependency(name="test_get_post_image_url")
@pytest.mark.parametrize('block, group_name, post, expected_url', [
    # Correct case: photo
    ('photo',
     'Alibi',
     {'attachments': [{'photo': {'sizes': [0, 1, 2, 3, {
        'url': 'http://url_1/'}]}}]},
     'http://url_1/'),
    # Correct case: album
    ('album',
     'Alibi',
     {'attachments': [{'album': {'thumb': {'sizes': [0, 1, 2, 3, {
         'url': 'http://url_2/'}]}}}]},
     'http://url_2/'),
    # Incorrect case: AttributeError (Alibi default photo used)
    # post_image_url = '' - because 'block' has unexpected value
    ('unexpected_value',
     'Alibi',
     {'attachments': [{'album': {'thumb': {'sizes': [0, 1, 2, {
         'url': 'http://url_1/'}]}}}]},
     'https://sun9-46.userapi.com/impg/LiT08C2tWC-QeeYRDjHqaHRFyXNOYyhxFacXQA/'
     'JpfUXhL2n2s.jpg?size=674x781&quality=95&sign='
     'e8310f98da4ff095adb5e46ba20eef2d&type=album'),
    # Incorrect case: ValueError (Detectit default photo used)
    # post_image_url = '' - because URL doesn't start with "http"
    ('unexpected_value',
     'Detectit',
     {'attachments': [
         {'album': {'thumb': {'sizes': [0, 1, 2, {'url': 'not_http'}]}}}]},
     'https://sun9-40.userapi.com/impg/frYTaWRpxfjOS8eVZayKsugTQILb9MM0uYggNQ/'
     'UhQlYUWdBh0.jpg?size=800x768&quality=95&sign='
     'bb10ce9b1e4f2328a2382faba0981c2c&type=album')])
def test_get_post_image_url(block, group_name, post, expected_url):
    """Test _get_post_image_url func from app_vk."""
    assert _get_post_image_url(
        block=block, group_name=group_name, post=post) == expected_url


MESSAGE_GET_VK_CHAT_UPDATE: dict = {'items': [{'id': 2}]}


@pytest.mark.parametrize('last_message_id, expected', [
    (1, MESSAGE_GET_VK_CHAT_UPDATE),
    (2, None)])
def test_get_vk_chat_update(last_message_id, expected, mocker):
    """Test _get_vk_chat_update func from app_vk."""
    vk_bot_mock = mocker.Mock()
    vk_bot_mock.messages.getHistory.return_value = MESSAGE_GET_VK_CHAT_UPDATE
    assert _get_vk_chat_update(
        last_message_id=last_message_id,
        vk_bot=vk_bot_mock,
        vk_group_id=0) == expected


POSTS_GET_VK_WALL_UPDATE: dict[str, list] = {'items': [{'id': 3}, {'id': 2}]}


@pytest.mark.parametrize('last_wall_id, expected', [
    (1, POSTS_GET_VK_WALL_UPDATE['items'][1]),
    (2, POSTS_GET_VK_WALL_UPDATE['items'][0]),
    (3, None)])
def test_get_vk_wall_update(last_wall_id, expected, mocker):
    """Test _get_vk_wall_update func from app_vk."""
    vk_bot_mock = mocker.Mock()
    vk_bot_mock.wall.get.return_value = POSTS_GET_VK_WALL_UPDATE
    assert _get_vk_wall_update(
        last_wall_id=last_wall_id,
        vk_bot=vk_bot_mock,
        vk_group_id=0) == expected


@pytest.mark.parametrize('group_name, expected', [
    ('Alibi', 'https://vk.com/alibigames?w=wall-40914100_0'),
    ('Detectit', 'https://vk.com/detectitspb?w=wall-219311078_0')
])
def test_make_link_to_post(group_name, expected):
    """Test make_link_to_post func from app_vk."""
    assert make_link_to_post(group_name=group_name, post_id=0) == expected


MESSAGE_NO_LOOKUP: str = 'Просто сообщение.'
MESSAGE_GAME_REMINDER_LOOKUP: str = (
    'Здравствуйте, детектив!\n\n'

    'Напоминаем, что завтра, 27 апреля, пройдёт расследование где-нибудь.\n'
    'Сбор команд начинается в 19:00, в 19:30 начинается игра.')
MESSAGE_TEAM_REGISTER_LOOKUP: str = (
    'Здравствуйте, детектив!\n\n'

    f'Регистрация команды «{TEAM_NAME}» в составе 4 игроков на расследование '
    '17 мая, 19:30 где-нибудь прошла успешно!\n'
    'Чтобы подтвердить бронь, вам нужно оплатить участие в течение 24 часов. '
    'Если вы отменяете участие менее, чем за сутки, оплата не возвращается. '
    'Стоимость участия: 123 ₽ с человека.\n\n'

    'Оплатить можно переводом на номер: 8-888-888-88-8.\n'
    'Какой-нибудь банк, на имя Имя Ф.\n'
    '❗ комментариях к переводу ничего указывать не нужно.\n\n'

    'Пожалуйста, пришлите скрин/квитанцию перевода в этот диалог :)')
PARSED_MESSAGE_GAME_REMINDER: str = (
    'Напоминаем, что завтра, 27 апреля, пройдёт расследование где-нибудь.\n\n'

    'Сбор команд начинается в 19:00, в 19:30 начинается игра.')
PARSED_MESSAGE_TEAM_REGISTER: str = (
    f'Регистрация команды «{TEAM_NAME}» в составе 4 игроков на расследование '
    '17 мая, 19:30 где-нибудь прошла успешно!\n\n'

    'Для подтверждения брони необходимо в течении суток оплатить участие в '
    f'игре. Оплата производится капитану команды по номеру {TEAM_CAPITAN_PROP}'
    ' в размере 123 рублей.\n\n'

    'Если команда отменяет участие менее, чем за сутки, оплата не '
    'возвращается.\n\n'

    'Если в составе команды будут дополнительные игроки, оплатить участие '
    'возможно по цене:\n'
    '· 500 ₽ с человека — до дня игры,\n'
    '· 600 ₽ с человека — в день игры.')


@pytest.mark.dependency(depends=["test_split_paragraphs"])
@pytest.mark.parametrize('group_name, message, parsed_message', [
    ('Alibi', MESSAGE_NO_LOOKUP, None),
    ('Alibi', MESSAGE_GAME_REMINDER_LOOKUP,
     f"🟣 Alibi{NL*2}{PARSED_MESSAGE_GAME_REMINDER}"),
    ('Alibi', MESSAGE_TEAM_REGISTER_LOOKUP,
     f"🟣 Alibi{NL*2}{PARSED_MESSAGE_TEAM_REGISTER}"),
    ('Detectit', MESSAGE_NO_LOOKUP, None),
    ('Detectit', MESSAGE_GAME_REMINDER_LOOKUP,
     f"⚫️ Detectit{NL*2}{PARSED_MESSAGE_GAME_REMINDER}"),
    ('Detectit', MESSAGE_TEAM_REGISTER_LOOKUP,
     f"⚫️ Detectit{NL*2}{PARSED_MESSAGE_TEAM_REGISTER}")])
def test_parse_message(group_name, message, parsed_message):
    """Test parse_message func from app_vk."""
    assert parse_message(
        group_name=group_name,
        message={'items': [{'text': message}]}) == parsed_message


A_RATING_EXP: list[str] = [
    '🟣 Alibi',
    'Детективы, самая первая серия игр Alibi окончена! Спасибо, что остаетесь '
    'с нами. Рады видеть тех, кто с нами давно, и тех, кто впервые открыл с '
    'нами формат детективных расследований.',
    'И публикуем сводную таблицу рейтинга команд за все игровые дни. '
    'Ищите себя и гордитесь своими результатами — какими бы они ни были 😌',
    'https://vk.com/alibigames?w=wall-40914100_13243']
A_TASKS_EXP: list[str] = [
    '🟣 Alibi',
    'Детективы, продолжаем нашу рубрику #alibitasks и у нас для вас новое '
    'задание. ',
    'Ваша задача: угадать фильм по альтернативному ',
    'постеру. ',
    'Ждем ваши варианты в комментариях! ',
    'https://vk.com/alibigames?w=wall-40914100_13380']
D_PHOTOS_EXP: list[str] = [
    '⚫️ Detectit',
    'Иллюстрации к нашей детективной истории всегда получаются самыми яркими. '
    'Ведь главными героями являетесь вы!',
    'Фотокарточки с расследования дела Сюзен Блант 23 мая в Парккинге в '
    'альбомах группы😉',
    'https://vk.com/detectitspb?w=wall-219311078_391']


@pytest.mark.dependency(name="test_parse_post_add_link")
@pytest.mark.dependency(depends=["test_split_paragraphs"])
@pytest.mark.parametrize('group_name, post, expected', [
    ('Alibi', A_EXAMPLE_RATING, A_RATING_EXP),
    ('Alibi', A_EXAMPLE_TASKS, A_TASKS_EXP),
    ('Detectit', D_EXAMPLE_PHOTOS, D_PHOTOS_EXP)])
def test_parse_post_add_link(group_name, post, expected):
    """Test _parse_post_add_link func from app_vk."""
    assert _parse_post_add_link(
        group_name=group_name,
        post_id=post['id'],
        splitted_text=_split_paragraphs(
            group_name=group_name,
            text=post['text'])) == expected


A_CHECKIN_EXP: list[str] = [
    '🟣 Alibi',
    'Регистрация. India ',
    'Ссылка на регистрацию: ',
    'https://vk.com/app5619682_-40914100 ',
    'Действует розыгрыш бесплатного входа на всю команду! Чтобы принять в нем '
    'участие, нужно вступить в группу и сделать репост этой записи:',
    'https://vk.com/alibigames?w=wall-40914100_13233',
    'Результаты будут в ночь с 26 на 27 марта.']


@pytest.mark.dependency(name="test_parse_post_checkin")
@pytest.mark.dependency(depends=["test_split_paragraphs"])
@pytest.mark.parametrize('group_name, post, expected', [
    ('Alibi', A_EXAMPLE_CHECKIN, A_CHECKIN_EXP),])
def test_parse_post_checkin(group_name, post, expected):
    """Test _parse_post_checkin func from app_vk."""
    assert _parse_post_checkin(
        group_name=group_name,
        post_id=post['id'],
        splitted_text=_split_paragraphs(
            group_name=group_name,
            text=post['text'])) == expected


@pytest.mark.dependency(name="test_parse_post_game_results")
@pytest.mark.dependency(depends=["test_split_paragraphs"])
@pytest.mark.parametrize('team_name, expected_medals', [
    ('Речевые аутисты', '#medal #wood_medal'),
    ('Босс молокосос и компания', '#medal #iron_medal'),
    ('Котики Киану Ривза', '#medal #bronze_medal'),
    ('Мы так и думали', '#medal #silver_medal'),
    ('Винтажный газогенератор', '#medal #gold_medal')])
def test_parse_post_game_results(team_name, expected_medals):
    """Test _parse_post_game_results func from app_vk."""
    assert _parse_post_game_results(
        splitted_text=_split_paragraphs(
            group_name='Alibi',
            text=A_EXAMPLE_GAME_RESULTS['text']),
        team_name=team_name) == [
            '🟣 Alibi',
            'Новая неделя — новые игры! В понедельник, в секретном месте '
            'на Горьковской мы с вами начали серию India. И теперь готовы '
            'поделиться результатами первой игры.',
            '▪5 место: «Речевые аутисты»',
            'Ну, благо речь на игре нужна в последнюю очередь — все '
            'ответы принимаются в письменном виде. И с этим команда '
            'справилась отлично 🎉',
            '▪4 место: «Босс молокосос и компания»',
            'Ох уж этот пятый тур… Но наш опыт показывает: те, кто '
            'уверенно держался в течение всей игры, не особенно '
            'пострадают от неудачи в самом конце. Так и вышло 🎊',
            '▪3 место: «Котики Киану Ривза»',
            'Всем котикам — по медали. Бронзовой! 🐱',
            '▪2 место: «Мы так и думали»',
            'Думать — это хорошо. Хорошо думать — ещё лучше. От этого '
            'бывают первые места, награды и другие приятные штуки 😉',
            '▪1 место: «Винтажный газогенератор»',
            'Удивительная машина — генерирует умные мысли и '
            'правильные ответы 🥂',
            expected_medals]


A_OTHER_EXP: list[str] = [
    '🟣 Alibi',
    'Новый формат уже в следующей серии игр.']


@pytest.mark.dependency(name="test_parse_post_other")
@pytest.mark.dependency(depends=["test_split_paragraphs"])
@pytest.mark.parametrize('group_name, post_text, expected', [
    ('Alibi', A_EXAMPLE_OTHER['text'], A_OTHER_EXP),])
def test_parse_post_other(group_name, post_text, expected):
    """Test _parse_post_other func from app_vk."""
    assert _parse_post_other(
        splitted_text=_split_paragraphs(
            group_name=group_name,
            text=post_text)) == expected


A_PREVIEW_DATES_EXP: list[str] = [
    '27 марта (СР), 19:00 — ресторан Parkking (Александровский парк, 4)',
    '28 марта (ЧТ), 19:00 — ресторан Parkking (Александровский парк, 4)',
    '30 марта (СБ), 19:00 — Дворец Олимпия (Литейный пр., 14)',
    '2 апреля (ВТ), 19:00 — Дворец Олимпия (Литейный пр., 14)',
    '3 апреля (СР), 19:00 — ресторан Parkking (Александровский парк, 4)']
A_PREVIEW_TEXT_EXP: list[str] = [
    '🟣 Alibi',
    'Анонс. India ',
    'Индия, 2006 год. ',
    'Между сезонами монсунов, затяжных дождей, волна жестоких, кровавых '
    'преступлений захлестнула север Индии. Массовые убийства местных и '
    'туристов держали людей в ужасе в течение нескольких месяцев. '
    'Пара французов, турист из Бразилии, а жертвы среди местного населения '
    'и вовсе исчислялись десятками... ',
    'Все в порезах. Некоторые — без глаз. И с кулонами в форме '
    'полумесяца на шее. Что это было? Предстоит разобраться',
    'Старт регистрации 22 марта в 18:05. ']
D_PREVIEW_DATES_EXP: list[str] = [
    '29 мая (ПН), 19:30, ресторан Parkking (Александровский парк, 4)',
    '30 мая (ВТ), 19:30, ресторан Parkking (Александровский парк, 4)',
    '31 мая (СР), 19:30, ресторан Unity на Сенной (пер. Гривцова, 4). ',]
D_PREVIEW_TEXT_EXP: list[str] = [
    '⚫️ Detectit',
    '🖇Анонс. Colt🖇 ',
    'Америка двадцатых расцвела музыкой и литературой, театром и '
    'кинематографом. Кипела жизнь, под звуки джаза рушились прошлые ',
    'устои...',
    '...13 июня 1925 около полуночи несколько студентов обнаружили в парке '
    'два трупа. Суетливый Нью-Йорк не заметил бы двух жертв ',
    'кольта 45 калибра. Но в редакции городских газет стали приходить '
    'пугающие письма...',
    'Старт регистрации 25 мая в 12:05. ']


@pytest.mark.dependency(name="test_parse_post_preview")
@pytest.mark.dependency(depends=[
    "test_game_dates_add_weekday_place",
    "test_split_paragraphs"])
@pytest.mark.parametrize('group_name, post_text, expected', [
    ('Alibi', A_EXAMPLE_PREVIEW['text'],
     (A_PREVIEW_DATES_EXP, A_PREVIEW_TEXT_EXP)),
    ('Detectit', D_EXAMPLE_PREVIEW['text'],
     (D_PREVIEW_DATES_EXP, D_PREVIEW_TEXT_EXP))])
def test_parse_post_preview(group_name, post_text, expected):
    """Test _parse_post_preview func from app_vk."""
    assert _parse_post_preview(
        group_name=group_name,
        post_text=post_text,
        splitted_text=_split_paragraphs(
            group_name=group_name,
            text=post_text)) == expected


A_PRIZE_RESULTS_EXP: list[str] = [
    '🟣 Alibi',
    '▪Итоги розыгрыша▪',
    'Подведение итогов в ночь перед первой игрой серии. '
    'Кто же станет победителем сегодня? Перейдём же скорее к результатам.',
    'Сегодня победителем становится...',
    '[id118725724|Варя Халилова] 🕵\u200d♂',
    'Мы вас поздравляем и рекомендуем в ближайшее время написать нам в личные '
    'сообщения группы название своей команды! Участие для команды Вари будет '
    'бесплатным в этой серии игр.']
D_PRIZE_RESULTS_EXP: list[str] = [
    '⚫️ Detectit',
    '▪Результаты розыгрыша▪ ',
    'Наша традиция - радовать вас результатами розыгрыша.',
    'Готовы? Победителем сегодня становится [id661684853|Коля Фомин]. ',
    'Ваша команда выигрывает участие в деле "1998"!',
    'Поздравляем и ждём вас в личке группы: там расскажем, что делать с '
    'выигрышем!']


@pytest.mark.dependency(name="test_parse_post_prize_results")
@pytest.mark.dependency(depends=["test_split_paragraphs"])
@pytest.mark.parametrize('group_name, post_text, expected', [
    ('Alibi', A_EXAMPLE_PRIZE_RESULTS['text'], A_PRIZE_RESULTS_EXP),
    ('Detectit', D_EXAMPLE_PRIZE_RESULTS['text'], D_PRIZE_RESULTS_EXP)])
def test_parse_post_prize_results(group_name, post_text, expected):
    """Test _parse_post_prize_results func from app_vk."""
    assert _parse_post_prize_results(
        splitted_text=_split_paragraphs(
            group_name=group_name,
            text=post_text)) == expected


D_STOP_LIST_EXP: list[str] = [
    '⚫️ Detectit',
    f"✅ Команда '{TEAM_NAME}' допущена к регистрации на серию игр!"]


@pytest.mark.dependency(name="test_parse_post_stop_list")
@pytest.mark.dependency(depends=["test_split_paragraphs"])
def test_parse_post_stop_list():
    """Test _parse_post_stop_list func from app_vk."""
    assert _parse_post_stop_list(
        post=D_EXAMPLE_STOP_LIST,
        splitted_text=_split_paragraphs(
            group_name='Detectit',
            text=D_EXAMPLE_STOP_LIST['text'])) == D_STOP_LIST_EXP


A_TEAMS_EXP: list[str] = ['🟣 Alibi', '🖇Списки команд🖇 ']
D_TEAMS_EXP: list[str] = ['⚫️ Detectit', '🖇Списки команд🖇 ']


@pytest.mark.dependency(name="test_parse_post_teams")
@pytest.mark.dependency(depends=["test_split_paragraphs"])
@pytest.mark.parametrize('group_name, post_text, expected', [
    ('Alibi', A_EXAMPLE_TEAMS['text'], A_TEAMS_EXP),
    ('Detectit', D_EXAMPLE_TEAMS['text'], D_TEAMS_EXP)])
def test_parse_post_teams(group_name, post_text, expected):
    """Test _parse_post_teams func from app_vk."""
    assert _parse_post_teams(
        splitted_text=_split_paragraphs(
            group_name=group_name,
            text=post_text)) == expected


# For some reason tests with both @pytest.mark.dependency and
# @pytest.mark.parametrize cause tests to be skipped
@pytest.mark.dependency(depends=[
    "test_define_post_topic",
    "test_get_post_image_url",
    # "test_parse_post_add_link",
    # "test_parse_post_checkin",
    # "test_parse_post_game_results",
    # "test_parse_post_other",
    # "test_parse_post_preview",
    # "test_parse_post_prize_results",
    # "test_parse_post_stop_list",
    # "test_parse_post_teams"
    ])
@pytest.mark.parametrize('group_name, post, expected', [
    ('Alibi', A_EXAMPLE_CHECKIN, {
        'post_id': A_EXAMPLE_CHECKIN['id'],
        'post_image_url': _get_post_image_url(
            block='photo',
            group_name='Alibi',
            post=A_EXAMPLE_CHECKIN),
        'post_text': A_CHECKIN_EXP,
        'game_dates': None}),
    # Указанная в .env команда (team_name) отсутствует в списке победителей.
    ('Alibi', A_EXAMPLE_GAME_RESULTS, None),
    ('Alibi', A_EXAMPLE_OTHER, {
        'post_id': A_EXAMPLE_OTHER['id'],
        'post_image_url': _get_post_image_url(
            block='video',
            group_name='Alibi',
            post=A_EXAMPLE_OTHER),
        'post_text': A_OTHER_EXP + [
            'Запись содержит видеоролик:\n'
            + make_link_to_post(
                group_name='Alibi', post_id=A_EXAMPLE_OTHER['id'])],
        'game_dates': None}),
    ('Alibi', A_EXAMPLE_PRIZE_RESULTS, {
        'post_id': A_EXAMPLE_PRIZE_RESULTS['id'],
        'post_image_url': _get_post_image_url(
            block='video',
            group_name='Alibi',
            post=A_EXAMPLE_PRIZE_RESULTS),
        'post_text': A_PRIZE_RESULTS_EXP + [
            'Запись содержит видеоролик:\n'
            + make_link_to_post(
                group_name='Alibi', post_id=A_EXAMPLE_PRIZE_RESULTS['id'])],
        'game_dates': None}),
    ('Alibi', A_EXAMPLE_PREVIEW, {
        'post_id': A_EXAMPLE_PREVIEW['id'],
        'post_image_url': _get_post_image_url(
            block='photo',
            group_name='Alibi',
            post=A_EXAMPLE_PREVIEW),
        'post_text': A_PREVIEW_TEXT_EXP,
        'game_dates': A_PREVIEW_DATES_EXP}),
    ('Alibi', A_EXAMPLE_RATING, {
        'post_id': A_EXAMPLE_RATING['id'],
        'post_image_url': _get_post_image_url(
            block='photo',
            group_name='Alibi',
            post=A_EXAMPLE_RATING),
        'post_text': A_RATING_EXP,
        'game_dates': None}),
    ('Alibi', A_EXAMPLE_TASKS, {
        'post_id': A_EXAMPLE_TASKS['id'],
        'post_image_url': _get_post_image_url(
            block='photo',
            group_name='Alibi',
            post=A_EXAMPLE_TASKS),
        'post_text': A_TASKS_EXP,
        'game_dates': None}),
    # The team TEAM_NAME is not in the top five
    ('Detectit', D_EXAMPLE_GAME_RESULTS, None),
    ('Detectit', D_EXAMPLE_PHOTOS, {
        'post_id': D_EXAMPLE_PHOTOS['id'],
        'post_image_url': _get_post_image_url(
            block='album',
            group_name='Detectit',
            post=D_EXAMPLE_PHOTOS),
        'post_text': D_PHOTOS_EXP,
        'game_dates': None}),
    ('Detectit', D_EXAMPLE_PREVIEW, {
        'post_id': D_EXAMPLE_PREVIEW['id'],
        'post_image_url': _get_post_image_url(
            block='photo',
            group_name='Detectit',
            post=D_EXAMPLE_PREVIEW),
        'post_text': D_PREVIEW_TEXT_EXP,
        'game_dates': D_PREVIEW_DATES_EXP}),
    ('Detectit', D_EXAMPLE_PRIZE_RESULTS, {
        'post_id': D_EXAMPLE_PRIZE_RESULTS['id'],
        'post_image_url': _get_post_image_url(
            block='video',
            group_name='Detectit',
            post=D_EXAMPLE_PRIZE_RESULTS),
        'post_text': D_PRIZE_RESULTS_EXP + [
            'Запись содержит видеоролик:\n'
            + make_link_to_post(
                group_name='Detectit', post_id=D_EXAMPLE_PRIZE_RESULTS['id'])],
        'game_dates': None}),
    ('Detectit', D_EXAMPLE_STOP_LIST, {
        'post_id': D_EXAMPLE_STOP_LIST['id'],
        'post_image_url': _get_post_image_url(
            block='photo',
            group_name='Detectit',
            post=D_EXAMPLE_STOP_LIST),
        'post_text': D_STOP_LIST_EXP,
        'game_dates': None}),
    ('Detectit', D_EXAMPLE_TEAMS, {
        'post_id': D_EXAMPLE_TEAMS['id'],
        'post_image_url': _get_post_image_url(
            block='photo',
            group_name='Detectit',
            post=D_EXAMPLE_TEAMS),
        'post_text': D_TEAMS_EXP,
        'game_dates': None})])
def test_parse_post(group_name, post, expected):
    """Test parse_post func from app_vk."""
    assert parse_post(
        group_name=group_name,
        post=post,
        post_topic=define_post_topic(post=post)) == expected


"""
Skipped tests.
The tested functions call other functions that use the VkApi.method.
"""

SKIP_REASON_VK_API: str = (
    'Currently no way to test it: '
    'call other function that use the VkApi.method!')


@pytest.mark.skip(reason=SKIP_REASON_VK_API)
def test_init_vk_bot() -> None:
    """Test init_vk_bot func from app_vk."""
    pass


@pytest.mark.skip(reason=SKIP_REASON_VK_API)
def test_get_vk_chat_update_groups():
    """Test get_vk_chat_update_groups func from app_vk."""
    pass


@pytest.mark.skip(reason=SKIP_REASON_VK_API)
def test_get_vk_wall_update_groups():
    """Test get_vk_wall_update_groups func from app_vk."""
    pass
