from dotenv import load_dotenv
import os

load_dotenv()

TEAM_NAME: str = os.getenv('TEAM_NAME')
TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_ME: str = os.getenv('TELEGRAM_ME')
TELEGRAM_TEAM_CHAT: str = os.getenv('TELEGRAM_TEAM_CHAT')
VK_TOKEN_ADMIN: str = os.getenv('VK_TOKEN_ADMIN')
VK_USER_ME: str = os.getenv('VK_USER_ME')
VK_GROUP_TARGET: int = 40914100
VK_GROUP_TARGET_LOGO: str = (
    'https://sun9-58.userapi.com/impg/jHCjJnuHFU2eulxgvuUG3UJ8WomEiT7ahhir-'
    'A/bfK5YYS9vNU.jpg?size=591x591&quality=96&sign='
    '43a3b5e57c5a40dd2c9155323fc69804&type=album'
)

VK_POST_LINK: str = 'https://vk.com/detectit_spb?w=wall-{}_{}'

API_UPDATE: int = 1

PINNED_POST: int = 0
NON_PINNED_POST: int = 1

POST_TOPICS: dict[str, str] = {
    '#detectit_preview': 'preview',
    'Stop-list': 'stop-list',
    '#detectit_checkin': 'checkin',
    '#detectit_teams': 'teams',
    '#detectit_results': 'game_results',
    'Результаты розыгрыша': 'prize_results',
    'Итоги розыгрыша': 'prize_results',
    '#detectit_photos': 'photos',
}

LOCATIONS: dict[str, str] = {
    'секретное место на Горьковской': (
        'ParkKing" (Александровский Парк, 4, ст.м. Горьковская)'),
    'секретное место на Чернышевской': (
        '"Дворец «Олимпия»" (Литейный пр., д. 14, ст.м. Чернышевская)'),
    'секретное место на Василеостровской': (
        '"Цинь" (16-я лин. B.O., 83, ст.м. Василеостровская)'),
}

TEAMMATES: dict[int, str] = {
    602516446: os.getenv('PLAYER_602516446'),
    354986248: os.getenv('PLAYER_354986248'),
    897453301: os.getenv('PLAYER_897453301'),
    1257617401: os.getenv('PLAYER_1257617401'),
    124478813: os.getenv('PLAYER_124478813')
}

EMOJI_NUMBERS: dict[int, str] = {
    0: '🚫',
    1: '1️⃣',
    2: '2️⃣',
    3: '3️⃣',
    4: '4️⃣',
    5: '5️⃣',
}

MEDALS: dict[int, list[str]] = {
    -2: ['#detectit_medal #detectit_gold_medal'],
    -4: ['#detectit_medal #detectit_silver_medal'],
    -6: ['#detectit_medal #detectit_bronze_medal'],
}

DATE_HEADLIGHT: str = (
    '————————————\n{number}  {date} | {location} | {count}\n————————————\n'
)
DATE_HEADLIGHT_X: str = (
    '————————————\n{number}  Не смогу быть | {count}\n————————————\n'
)
