from dotenv import load_dotenv
import os
from telegram import InlineKeyboardButton

load_dotenv()

TEAM_NAME: str = os.getenv('TEAM_NAME')
TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_TEAM_CHAT: str = os.getenv('TELEGRAM_TEAM_CHAT')
TELEGRAM_USER: str = os.getenv('TELEGRAM_USER')
VK_TOKEN_ADMIN: str = os.getenv('VK_TOKEN_ADMIN')
VK_USER: str = os.getenv('VK_USER')
VK_GROUP_TARGET: int = 40914100
VK_GROUP_TARGET_LOGO: str = (
    'https://sun9-46.userapi.com/impg/LiT08C2tWC-QeeYRDjHqaHRFyXNOYyhxFacXQA/'
    'JpfUXhL2n2s.jpg?size=674x781&quality=95&sign='
    'e8310f98da4ff095adb5e46ba20eef2d&type=album')

API_TELEGRAM_UPDATE_SEC: int = 0.5
API_VK_UPDATE_SEC: int = 10

APP_JSON_FOLDER: str = 'project/data/'

DATE_HEADLIGHT: str = (
    '————————————\n{number} {date_location} | {teammates_count}\n————————————')

EMOJI_SYMBOLS: dict[int, str] = {
    0: '🚫',
    1: '1️⃣',
    2: '2️⃣',
    3: '3️⃣',
    4: '4️⃣',
    5: '5️⃣',
    6: '6️⃣'}

LOCATIONS: dict[str, str] = {
    'секретное место на Горьковской':
        'ParkKing (Александровский Парк, 4, ст.м. Горьковская)',
    'секретное место на Чернышевской':
        'Дворец «Олимпия» (Литейный пр., д. 14, ст.м. Чернышевская)',
    'секретное место на Василеостровской':
        'Цинь (16-я лин. B.O., 83, ст.м. Василеостровская)'}

MEDALS: dict[str, list[str]] = {
    '1th': ['#medal #gold_medal'],
    '2th': ['#medal #silver_medal'],
    '3th': ['#medal #bronze_medal'],
    '4th': ['#medal #iron_medal'],
    '5th': ['#medal #wood_medal']}


PINNED_POST_ID: int = 0
NON_PINNED_POST_ID: int = 1

POST_TOPICS: dict[str, str] = {
    '#alibi_checkin': 'checkin',
    '#alibispb_results': 'game_results',
    'Итоги розыгрыша': 'prize_results',
    '#alibi_preview': 'preview',
    '#ГонорарДетектива': 'rating',
    '#detectit_teams': 'teams'}
"""
Нет данных для категорий:
    None: 'stop-list'
    None: 'photos'
"""

TEAM_CONFIG: dict[dict[any]] = {
        'last_message_id': None,
        'game_count': 0,
        'game_dates': {}}
TEAM_CONFIG_BUTTONS: dict[str, list[list[InlineKeyboardButton]]] = {
    1: [
        [
            InlineKeyboardButton(text='1️⃣✅', callback_data='1 +1'),
            InlineKeyboardButton(text='1️⃣❌', callback_data='1 -1'),
            InlineKeyboardButton(text='🚫', callback_data='0 +1')]],
    2: [
        [
            InlineKeyboardButton(text='1️⃣✅', callback_data='1 +1'),
            InlineKeyboardButton(text='1️⃣❌', callback_data='1 -1'),
            InlineKeyboardButton(text='2️⃣✅', callback_data='2 +1'),
            InlineKeyboardButton(text='2️⃣❌', callback_data='2 -1')],
        [
            InlineKeyboardButton(text='🚫', callback_data='0 +1')]],
    5: [
        [
            InlineKeyboardButton(text='1️⃣✅', callback_data='1 +1'),
            InlineKeyboardButton(text='1️⃣❌', callback_data='1 -1'),
            InlineKeyboardButton(text='2️⃣✅', callback_data='2 +1'),
            InlineKeyboardButton(text='2️⃣❌', callback_data='2 -1')],
        [
            InlineKeyboardButton(text='3️⃣✅', callback_data='3 +1'),
            InlineKeyboardButton(text='3️⃣❌', callback_data='3 -1'),
            InlineKeyboardButton(text=' ', callback_data='1 0'),
            InlineKeyboardButton(text='🚫', callback_data='0 +1')]],
    4: [
        [
            InlineKeyboardButton(text='1️⃣✅', callback_data='1 +1'),
            InlineKeyboardButton(text='1️⃣❌', callback_data='1 -1'),
            InlineKeyboardButton(text='2️⃣✅', callback_data='2 +1'),
            InlineKeyboardButton(text='2️⃣❌', callback_data='2 -1')],
        [
            InlineKeyboardButton(text='3️⃣✅', callback_data='3 +1'),
            InlineKeyboardButton(text='3️⃣❌', callback_data='3 -1'),
            InlineKeyboardButton(text='4️⃣✅', callback_data='4 +1'),
            InlineKeyboardButton(text='4️⃣❌', callback_data='4 -1')],
        [
            InlineKeyboardButton(text='🚫', callback_data='0 +1')]],
    6: [
        [
            InlineKeyboardButton(text='1️⃣✅', callback_data='1 +1'),
            InlineKeyboardButton(text='1️⃣❌', callback_data='1 -1'),
            InlineKeyboardButton(text='2️⃣✅', callback_data='2 +1'),
            InlineKeyboardButton(text='2️⃣❌', callback_data='2 -1')],
        [
            InlineKeyboardButton(text='3️⃣✅', callback_data='3 +1'),
            InlineKeyboardButton(text='3️⃣❌', callback_data='3 -1'),
            InlineKeyboardButton(text='4️⃣✅', callback_data='4 +1'),
            InlineKeyboardButton(text='4️⃣❌', callback_data='4 -1')],
        [
            InlineKeyboardButton(text='5️⃣✅', callback_data='5 +1'),
            InlineKeyboardButton(text='5️⃣❌', callback_data='5 -1'),
            InlineKeyboardButton(text=' ', callback_data='1 0'),
            InlineKeyboardButton(text='🚫', callback_data='0 +1')]],
    6: [
        [
            InlineKeyboardButton(text='1️⃣✅', callback_data='1 +1'),
            InlineKeyboardButton(text='1️⃣❌', callback_data='1 -1'),
            InlineKeyboardButton(text='2️⃣✅', callback_data='2 +1'),
            InlineKeyboardButton(text='2️⃣❌', callback_data='2 -1')
        ],
        [
            InlineKeyboardButton(text='3️⃣✅', callback_data='3 +1'),
            InlineKeyboardButton(text='3️⃣❌', callback_data='3 -1'),
            InlineKeyboardButton(text='4️⃣✅', callback_data='4 +1'),
            InlineKeyboardButton(text='4️⃣❌', callback_data='4 -1')],
        [
            InlineKeyboardButton(text='5️⃣✅', callback_data='5 +1'),
            InlineKeyboardButton(text='5️⃣❌', callback_data='5 -1'),
            InlineKeyboardButton(text='6️⃣✅', callback_data='6 +1'),
            InlineKeyboardButton(text='6️⃣❌', callback_data='6 -1')],
        [
            InlineKeyboardButton(text='🚫', callback_data='0 +1')]]}

TEAM_GUEST: str = '(приглашенный гость)'

VK_POST_LINK: str = 'https://vk.com/alibigames?w=wall-'

{
    'update_id': 625267228,
    'callback_query': {
        'chat_instance': '-8206862260693408859',
        'id': '1524654326679682664',
        'message': {
            'group_chat_created': False,
            'reply_markup': {
                'inline_keyboard': [[{'text': 'adsdas', 'callback_data': '-100310fasfasd'}]]},
            'new_chat_photo': [],
            'caption_entities': [],
            'channel_chat_created': False,
            'new_chat_members': [],
            'message_id': 548,
            'supergroup_chat_created': False,
            'entities': [],
            'delete_chat_photo': False,
            'text': '————————————\n1️⃣ 27 марта (ср), 1 19:00 — ParkKing (Александровский Парк, 4, ст.м. Горьковская) | 0\n————————————\n————————————\n2️⃣ 28 марта (чт), 19:00 — Pa arkKing (Александровский Парк, 4, ст.м. Горьковская) | 0\n————————————\n————————————\n3️⃣ 30 марта (сб), 19:00 — Дворец «Оли импия» (Литейный пр., д. 14, ст.м. Чернышевская) | 0\n————————————\n————————————\n4️⃣ 2 апреля (вс), 19:00 — Дворец «Олимпия я» (Литейный пр., д. 14, ст.м. Чернышевская) | 0\n————————————\n————————————\n5️⃣ 3 апреля (пн), 19:00 — ParkKing (Александр ровский Парк, 4, ст.м. Горьковская) | 0\n————————————\n————————————\n🚫 Не смогу быть | 0\n————————————',
            'photo': [],
            'date': 1681033974,
            'chat': {
                'type': 'group',
                'title': 'Bot detectit test',
                'id': -818816020,
                'all_members_are_administrators': True},
            'from': {
                'id': 5854517727,
                'username': 'Detectit_Announcer_Bot',
                'is_bot': True,
                'first_name': '@Alibi_Announcer_Bot'}},
        'data': '-100310fasfasd',
        'from': {
            'id': 354986248,
            'language_code': 'ru',
            'last_name': 'Свидунович',
            'username': 'suncatcher222',
            'is_bot': False,
            'first_name': 'Кирилл'}}}