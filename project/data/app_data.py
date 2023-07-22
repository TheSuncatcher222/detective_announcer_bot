from dotenv import load_dotenv
import os
from telegram import InlineKeyboardButton, ReplyKeyboardMarkup

load_dotenv()

"""Env data."""

TEAM_CAPITAN_PROP: str = os.getenv('TEAM_CAPITAN_PROP')
TEAM_NAME: str = os.getenv('TEAM_NAME')
TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_TEAM_CHAT: str = os.getenv('TELEGRAM_TEAM_CHAT')
TELEGRAM_USER: str = os.getenv('TELEGRAM_USER')
VK_TOKEN_ADMIN: str = os.getenv('VK_TOKEN_ADMIN')
VK_USER: str = os.getenv('VK_USER')

"""App settings."""

API_TELEGRAM_UPDATE_SEC: int = 1
API_VK_UPDATE_SEC: int = 60

LAST_API_ERR_DEL_SEC: int = 60 * 60

REPLY_FATHER_BUTTONS: list[list[str]] = [['/forward', '/forward_abort']]
REPLY_FATHER_MARKUP: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    REPLY_FATHER_BUTTONS, resize_keyboard=True)
REPLY_TO_FORWARD_TEXT: str = 'Я готов, что нужно переслать?'
REPLY_TO_FORWARD_ABORT_TEXT: str = 'Хорошо, ничего никуда не перешлю!'

# If true bot will send only posts in white list below
SKIP_IF_NOT_IMPORTANT: bool = False
SKIP_WHITE_LIST: list[str] = [
    'checkin', 'game_results', 'preview',
    'prize_results', 'stop-list', 'teams']

"""Groups main info data."""

ALIBI: str = 'Alibi'
ALIBI_GROUP_ID: int = 40914100
ALIBI_GROUP_LOGO: str = (
    'https://sun9-46.userapi.com/impg/LiT08C2tWC-QeeYRDjHqaHRFyXNOYyhxFacXQA/'
    'JpfUXhL2n2s.jpg?size=674x781&quality=95&sign='
    'e8310f98da4ff095adb5e46ba20eef2d&type=album')
ALIBI_POST_LINK: str = 'https://vk.com/alibigames?w=wall-'
ALIBI_TAG: str = '🟣 Alibi'
DETECTIT: str = 'Detectit'
DETECTIT_GROUP_ID: int = 219311078
DETECTIT_GROUP_LOGO: str = (
    'https://sun9-40.userapi.com/impg/frYTaWRpxfjOS8eVZayKsugTQILb9MM0uYggNQ/'
    'UhQlYUWdBh0.jpg?size=800x768&quality=95&sign='
    'bb10ce9b1e4f2328a2382faba0981c2c&type=album')
DETECTIT_POST_LINK: str = 'https://vk.com/detectitspb?w=wall-'
DETECTIT_TAG: str = '⚫️ Detectit'

PINNED_POST_ORDER: int = 0
NON_PINNED_POST_ORDER: int = 1

MAX_CAPTION_LENGTH: int = 1024
MAX_LINK_LENGTH: int = 100

"""Data to text parsing."""

EMOJI_SYMBOLS: dict[int, str] = {
    1: '1️⃣',
    2: '2️⃣',
    3: '3️⃣',
    4: '4️⃣',
    5: '5️⃣',
    6: '6️⃣',
    ALIBI: {
        'true': '✅',
        'false': '❌',
        'skip': '🚫',
        'pref': ALIBI},
    DETECTIT: {
        'true': '❇️',
        'false': '⭕️',
        'skip': '⛔️',
        'pref': DETECTIT}}

CALLBACK_DATA_NONE: str = 'None'


def _create_inline_buttons(
        group_name: str
        ) -> dict[int, list[list[InlineKeyboardButton]]]:
    """Create inline keyboard buttons for given group."""
    if group_name == ALIBI:
        but_true, but_false, but_deny, pref = EMOJI_SYMBOLS[ALIBI].values()
    else:
        but_true, but_false, but_deny, pref = EMOJI_SYMBOLS[DETECTIT].values()
    inline_buttons: dict[int, list[list[InlineKeyboardButton]]] = {}
    for game_num in range(1, 7):
        buttons_row: list[list[InlineKeyboardButton]] = []
        buttons: list[InlineKeyboardButton] = []
        for j in range(1, game_num+1):
            if j != 1 and j % 2 == 1:
                buttons_row.append(buttons)
                buttons: list[InlineKeyboardButton] = []
            for action in [[but_true, '+1'], [but_false, '-1']]:
                buttons.append(
                    InlineKeyboardButton(
                        text=f'{EMOJI_SYMBOLS[j]}{action[0]}',
                        callback_data=f'{j} {action[1]} {pref}'))
        if j % 2 == 1:
            buttons += [
                InlineKeyboardButton(
                    text=' ', callback_data=CALLBACK_DATA_NONE),
                InlineKeyboardButton(
                    text=but_deny, callback_data=f'0 +1 {pref}')]
        else:
            buttons_row.append(buttons)
            buttons: list[InlineKeyboardButton] = [
                InlineKeyboardButton(
                    text=' ', callback_data=CALLBACK_DATA_NONE),
                InlineKeyboardButton(
                    text=' ', callback_data=CALLBACK_DATA_NONE),
                InlineKeyboardButton(
                    text=' ', callback_data=CALLBACK_DATA_NONE),
                InlineKeyboardButton(
                    text=but_deny,
                    callback_data=f'0 +1 {pref}')]
        buttons_row.append(buttons)
        inline_buttons[game_num] = buttons_row
    return inline_buttons


BUTTONS_TEAM_CONFIG_ALIBI: dict[int, list[list[InlineKeyboardButton]]] = (
    _create_inline_buttons(group_name=ALIBI))
BUTTONS_TEAM_CONFIG_DETECTIT: dict[int, list[list[InlineKeyboardButton]]] = (
    _create_inline_buttons(group_name=DETECTIT))

DATE_HEADLIGHT: str = (
    '{number} {date_location}')

LOCATIONS: dict[str, str] = {
    'секретное место на Василеостровской':
        'ресторан Цинь (16-я лин. B.O., 83)',
    'секретное место на Горьковской':
        'ресторан Parkking (Александровский парк, 4)',
    'секретное место на Петроградской':
        'ресторан Unity на Петроградской (наб. Карповки, 5к17)',
    'секретное место на Площади Ленина':
        'Центр Kod (ул. Комсомола, 2)',
    'секретное место на Сенной':
        'ресторан Unity на Сенной (пер. Гривцова, 4)',
    'секретное место на Чернышевской':
        'Дворец Олимпия (Литейный пр., 14)'}

MEDALS: dict[str, list[str]] = {
    '1th': ['#medal #gold_medal'],
    '2th': ['#medal #silver_medal'],
    '3th': ['#medal #bronze_medal'],
    '4th': ['#medal #iron_medal'],
    '5th': ['#medal #wood_medal']}

POST_TOPICS: dict[str, str] = {
    'ГонорарДетектива': 'rating',
    'tasks': 'tasks',
    '📸': 'photos',
    'photos': 'photos',
    'results': 'game_results',
    'preview': 'preview',
    'стоп_лист': 'stop-list',
    'Stop-list': 'stop-list',
    'checkin': 'checkin',
    'teams': 'teams',
    'Итоги розыгрыша': 'prize_results',
    'Результаты розыгрыша': 'prize_results',
    'Отзыв от команды': 'feedback',
    'фото': 'photos'}

TEAM_GUEST: str = '(гость)'

GAME_REMINDER_LOOKUP: str = 'Напоминаем, что завтра'
TEAM_REGISTER_LOOKUP: str = f'Регистрация команды «{TEAM_NAME}»'

TEAM_REGISTER_TEXT: str = (
    'Для подтверждения брони необходимо в течении суток оплатить участие '
    'в игре. Оплата производится капитану команды по номеру '
    f'{TEAM_CAPITAN_PROP} в размере '
    '{money_amount} рублей.\n\n'

    'Если команда отменяет участие менее, чем за сутки, оплата '
    'не возвращается.\n\n'

    'Если в составе команды будут дополнительные игроки, оплатить участие '
    'возможно по цене:\n'
    '· 500 ₽ с человека — до дня игры,\n'
    '· 600 ₽ с человека — в день игры.')

"""JSON settings."""

API_ERROR_NAME: str = 'last_api_error.json'

DATA_FOLDER: str = 'project/data/'
SAVED_DATA_JSON_NAME: str = 'saved_data.json'
SAVED_DATA_JSON_DEFAULT: dict[str, int | dict[str, any]] = {
    'last_alibi_game': 'NoData',
    'last_detectit_game': 'NoData',
    'last_vk_message_id_alibi': 0,
    'last_vk_message_id_detectit': 0,
    'last_vk_wall_id_alibi': 0,
    'last_vk_wall_id_detectit': 0,
    'pinned_telegram_message_id_alibi': 0,
    'pinned_telegram_message_id_detectit': 0,
    'pinned_vk_message_id_alibi': 0,
    'pinned_vk_message_id_detectit': 0,
    'team_config_alibi': {},
    'team_config_detectit': {},
    'father_forward': False}

STOP_LIST_ACCEPT: str = (
    f"✅ Команда '{TEAM_NAME}' допущена к регистрации на серию игр!")
STOP_LIST_DENY: str = (
    f"⛔️ Команда '{TEAM_NAME}' уже была на представленной серии игр!")
