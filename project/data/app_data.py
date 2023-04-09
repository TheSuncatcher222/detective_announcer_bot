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
TEAM_CONFIG_BUTTONS = {
    1: [
        [
            InlineKeyboardButton('1️⃣✅', callback_data='1 +1'),
            InlineKeyboardButton('1️⃣❌', callback_data='1 -1'),
            InlineKeyboardButton('🚫', callback_data='0 +1')]],
    2: [
        [
            InlineKeyboardButton('1️⃣✅', callback_data='1 +1'),
            InlineKeyboardButton('1️⃣❌', callback_data='1 -1'),
            InlineKeyboardButton('2️⃣✅', callback_data='2 +1'),
            InlineKeyboardButton('2️⃣❌', callback_data='2 -1')],
        [
            InlineKeyboardButton('🚫', callback_data='0 +1')]],
    3: [
        [
            InlineKeyboardButton('1️⃣✅', callback_data='1 +1'),
            InlineKeyboardButton('1️⃣❌', callback_data='1 -1'),
            InlineKeyboardButton('2️⃣✅', callback_data='2 +1'),
            InlineKeyboardButton('2️⃣❌', callback_data='2 -1')],
        [
            InlineKeyboardButton('3️⃣✅', callback_data='3 +1'),
            InlineKeyboardButton('3️⃣❌', callback_data='3 -1'),
            InlineKeyboardButton(' ', callback_data=None),
            InlineKeyboardButton('🚫', callback_data='0 +1')]],
    4: [
        [
            InlineKeyboardButton('1️⃣✅', callback_data='1 +1'),
            InlineKeyboardButton('1️⃣❌', callback_data='1 -1'),
            InlineKeyboardButton('2️⃣✅', callback_data='2 +1'),
            InlineKeyboardButton('2️⃣❌', callback_data='2 -1')],
        [
            InlineKeyboardButton('3️⃣✅', callback_data='3 +1'),
            InlineKeyboardButton('3️⃣❌', callback_data='3 -1'),
            InlineKeyboardButton('4️⃣✅', callback_data='4 +1'),
            InlineKeyboardButton('4️⃣❌', callback_data='4 -1')],
        [
            InlineKeyboardButton('🚫', callback_data='0 +1')]],
    5: [
        [
            InlineKeyboardButton('1️⃣✅', callback_data='1 +1'),
            InlineKeyboardButton('1️⃣❌', callback_data='1 -1'),
            InlineKeyboardButton('2️⃣✅', callback_data='2 +1'),
            InlineKeyboardButton('2️⃣❌', callback_data='2 -1')],
        [
            InlineKeyboardButton('3️⃣✅', callback_data='3 +1'),
            InlineKeyboardButton('3️⃣❌', callback_data='3 -1'),
            InlineKeyboardButton('4️⃣✅', callback_data='4 +1'),
            InlineKeyboardButton('4️⃣❌', callback_data='4 -1')],
        [
            InlineKeyboardButton('5️⃣✅', callback_data='5 +1'),
            InlineKeyboardButton('5️⃣❌', callback_data='5 -1'),
            InlineKeyboardButton(' ', callback_data=None),
            InlineKeyboardButton('🚫', callback_data='0 +1')]],
    6: [
        [
            InlineKeyboardButton('1️⃣✅', callback_data='1 +1'),
            InlineKeyboardButton('1️⃣❌', callback_data='1 -1'),
            InlineKeyboardButton('2️⃣✅', callback_data='2 +1'),
            InlineKeyboardButton('2️⃣❌', callback_data='2 -1')
        ],
        [
            InlineKeyboardButton('3️⃣✅', callback_data='3 +1'),
            InlineKeyboardButton('3️⃣❌', callback_data='3 -1'),
            InlineKeyboardButton('4️⃣✅', callback_data='4 +1'),
            InlineKeyboardButton('4️⃣❌', callback_data='4 -1')],
        [
            InlineKeyboardButton('5️⃣✅', callback_data='5 +1'),
            InlineKeyboardButton('5️⃣❌', callback_data='5 -1'),
            InlineKeyboardButton('6️⃣✅', callback_data='6 +1'),
            InlineKeyboardButton('6️⃣❌', callback_data='6 -1')],
        [
            InlineKeyboardButton('🚫', callback_data='0 +1')]]}

TEAM_GUEST: str = '(приглашенный гость)'

VK_POST_LINK: str = 'https://vk.com/alibigames?w=wall-'
