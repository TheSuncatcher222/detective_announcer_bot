from http import HTTPStatus
import requests
import telegram
from telegram import TelegramError

from project.data.app_data import TELEGRAM_USER
#from main import get_game_dates_json, rebuild_game_dates_json


def check_telegram_bot_response(token: str) -> None:
    """Проверяет ответ telegram BOT API."""
    response: requests.Response = requests.get(
        f'https://api.telegram.org/bot{token}/getMe')
    status: int = response.status_code
    if status == HTTPStatus.OK:
        return
    elif status == HTTPStatus.UNAUTHORIZED:
        raise SystemExit('Telegram bot token is invalid!')
    else:
        raise SystemExit('Telegram API is unavaliable!')


def init_telegram_bot(token: str) -> telegram.Bot:
    return telegram.Bot(token=token)


def send_message(bot, message: str) -> None:
    """Отправляет сообщение в Telegram."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_USER,
            text=message)
    except TelegramError:
        raise Exception("Bot can't send the message!")
    return


def send_update(telegram_bot, parsed_post: dict) -> None:
    """Отправляет полученные данные с ВК в телеграм чат."""
    output_text: str = ''
    for paragraph in parsed_post['post_text']:
        # Сделать через .join()
        output_text += (paragraph + 2*'\n')
    try:
        telegram_bot.send_photo(
            chat_id=TELEGRAM_USER,
            photo=parsed_post['post_image_url'],
            caption=output_text)
        if 'game_dates' in parsed_post:
            # game_dates = rebuild_game_dates_json(
            #     new_game=parsed_post['game_dates'])
            # game_dates_message = get_game_dates_json(data=game_dates)
            # send_message(
            #     bot=telegram_bot, message=game_dates_message)
            pass
    except TelegramError as err:
        raise Exception(f"Bot can't send the message! Error message: {err}")
    return
