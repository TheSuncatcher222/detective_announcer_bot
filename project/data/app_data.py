from dotenv import load_dotenv
import os

load_dotenv()

TEAM_NAME: str = os.getenv('TEAM_NAME')
TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_ME: str = os.getenv('TELEGRAM_ME')
TELEGRAM_TEAM_CHAT: str = os.getenv('TELEGRAM_TEAM_CHAT')
VK_TOKEN_ADMIN: str = os.getenv('VK_TOKEN_ADMIN')
VK_USER: str = os.getenv('VK_USER')
VK_GROUP_TARGET: int = 40914100
VK_GROUP_TARGET_LOGO: str = (
    'https://sun9-46.userapi.com/impg/LiT08C2tWC-QeeYRDjHqaHRFyXNOYyhxFacXQA/'
    'JpfUXhL2n2s.jpg?size=674x781&quality=95&sign='
    'e8310f98da4ff095adb5e46ba20eef2d&type=album')

API_UPDATE: int = 1

DATE_HEADLIGHT: str = (
    '————————————\n{number}  {date} | {location} | {count}\n————————————\n')
DATE_HEADLIGHT_X: str = (
    '————————————\n{number}  Не смогу быть | {count}\n————————————\n')

EMOJI_NUMBERS: dict[int, str] = {
    0: '🚫',
    1: '1️⃣',
    2: '2️⃣',
    3: '3️⃣',
    4: '4️⃣',
    5: '5️⃣'}

LOCATIONS: dict[str, str] = {
    'секретное место на Горьковской': (
        'ParkKing (Александровский Парк, 4, ст.м. Горьковская)'),
    'секретное место на Чернышевской': (
        'Дворец «Олимпия» (Литейный пр., д. 14, ст.м. Чернышевская)'),
    'секретное место на Василеостровской': (
        'Цинь (16-я лин. B.O., 83, ст.м. Василеостровская)'),}

MEDALS: dict[int, list[str]] = {
    -2: ['#alibi_medal #alibi_gold_medal'],
    -4: ['#alibi_medal #alibi_silver_medal'],
    -6: ['#alibi_medal #alibi_bronze_medal'],}

MONTHS = {
    'января': 1,
    'февраля': 2,
    'марта': 3,
    'апреля': 4,
    'мая': 5,
    'июня': 6,
    'июля': 7,
    'августа': 8,
    'сентября': 9,
    'октября': 10,
    'ноября': 11,
    'декабря': 12}
WEEKDAYS = {
    0: 'пн',
    1: 'вт',
    2: 'ср',
    3: 'чт',
    4: 'пт',
    5: 'сб',
    6: 'вс'}

PINNED_POST_ID: int = 0
NON_PINNED_POST_ID: int = 1

POST_TOPICS: dict[str, str] = {
    'Анонс': 'preview',
    'Регистрация': 'checkin',
    'Итоги розыгрыша': 'prize_results',
    'alibispb_results': 'game_results',
    'Списки команд': 'teams'}
"""Нет данных для категорий:
    None: 'stop-list'
    None: 'photos'
    None: 'rating'
"""

VK_POST_LINK: str = 'https://vk.com/alibigames?w=wall-{}_{}'
