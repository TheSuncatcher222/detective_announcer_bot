from http import HTTPStatus
import requests
import telegram
from telegram import TelegramError, InlineKeyboardMarkup, InlineKeyboardButton

from project.data.app_data import (
    DATE_HEADLIGHT, EMOJI_SYMBOLS, TEAM_GUEST, TELEGRAM_TEAM_CHAT)


def check_telegram_bot_response(token: str) -> None:
    """Check telegram BOT API response."""
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
    """Initialize telegram bot."""
    return telegram.Bot(token=token)


def create_keyboard_game_date(
        games_count: int) -> list[list[InlineKeyboardButton]]:
    """Create InlineKeyboardButton for game dates message."""
    keyboard: list = []
    for i in range(1, games_count + 1):
        keyboard.append(
            [f"{EMOJI_SYMBOLS[i]}{EMOJI_SYMBOLS['+']}",
             f"{EMOJI_SYMBOLS[i]}{EMOJI_SYMBOLS['-']}"])
    keyboard.append([f'{EMOJI_SYMBOLS[0]}'])
    return keyboard


def create_new_team_config_game_dates(
        game_dates: list, team_config: dict) -> None:
    """Create new data in team_config for new game_dates."""
    team_config['game_count'] = len(game_dates)
    team_config['game_dates'] = {
        **{
            i + 1: {
                'date_location': game,
                'teammates': {}} for i, game in enumerate(game_dates)},
        0: {
            'date_location': 'Не смогу быть',
            'teammates': {}}}
    team_config['game_dates_keyboard'] = create_keyboard_game_date(
        games_count=team_config['game_count'])
    return


def rebuild_team_config_game_dates(
        team_config: dict,
        teammate_decision: dict) -> None:
    """Rebuild data in team_config according teammate decision."""
    teammate: str = teammate_decision['teammate']
    game_num: int = teammate_decision['game_num']
    decision: int = teammate_decision['decision']
    if decision == 1:
        if game_num == 0 and teammate not in team_config[
                'game_dates'][game_num]['teammates']:
            team_config['game_dates'][game_num]['teammates'][teammate] = 1
            for i in range(1, team_config['game_count']):
                team_config['game_dates'][i]['teammates'].pop(teammate, None)
        else:
            team_config['game_dates'][0]['teammates'].pop(teammate, None)
            if teammate not in team_config[
                    'game_dates'][game_num]['teammates']:
                team_config[
                    'game_dates'][game_num]['teammates'][teammate] = 0
            team_config['game_dates'][game_num]['teammates'][teammate] += 1
    else:
        if teammate in team_config['game_dates'][game_num]['teammates']:
            team_config['game_dates'][game_num]['teammates'][teammate] -= 1
            if team_config['game_dates'][game_num]['teammates'][teammate] == 0:
                del team_config['game_dates'][game_num]['teammates'][teammate]
    return


def form_game_dates_text(game_dates: dict) -> str:
    """Form text message from game_dates."""
    abstracts: list[str] = []
    for num in game_dates:
        teammates_count: int = sum(
            game_dates[num]['teammates'][teammate]
            for teammate in game_dates[num]['teammates'])
        date_location, teammates = game_dates[num].values()
        abstracts.append(DATE_HEADLIGHT.format(
            number=EMOJI_SYMBOLS[num],
            date_location=date_location,
            teammates_count=teammates_count))
        for teammate, count in teammates.items():
            abstracts.append(teammate)
            for _ in range(1, count):
                abstracts.append(f'{teammate} {TEAM_GUEST}')
    return '\n'.join(abstracts)


def send_message(bot, message: str, chat_id: int = TELEGRAM_TEAM_CHAT) -> None:
    """Send message to target telegram user/chat."""
    try:
        bot.send_message(
            chat_id=chat_id,
            text=message)
    except TelegramError:
        raise Exception("Bot can't send the message!")
    return


def send_message_for_game_dates(
        bot,
        message: str,
        keyboard: list[list[InlineKeyboardMarkup]],
        chat_id: int = TELEGRAM_TEAM_CHAT) -> int:
    """Send message with game dates and keyboard to target telegram user/chat.
    Return message id."""
    try:
        message = bot.send_message(
            chat_id=chat_id,
            reply_markup=InlineKeyboardMarkup(keyboard),
            text=message)
    except TelegramError:
        raise Exception("Bot can't send the message!")
    return message.message_id


def send_photo(
        bot,
        photo_url: str,
        message: str = None,
        chat_id: int = TELEGRAM_TEAM_CHAT) -> None:
    """Send photo with optional message to target telegram user/chat."""
    try:
        bot.send_photo(
            caption=message,
            chat_id=chat_id,
            photo=photo_url)
    except TelegramError as err:
        raise Exception(f'Bot failed to send photo-message! Error: {err}')
    return


def send_update(parsed_post: dict, team_config: dict, telegram_bot) -> None:
    """Send update from VK group wall to target telegram chat."""
    send_photo(
        bot=telegram_bot,
        message='\n\n'.join(s for s in parsed_post['post_text']),
        photo_url=parsed_post['post_image_url'])
    if parsed_post['game_dates']:
        create_new_team_config_game_dates(
            game_dates=parsed_post['game_dates'], team_config=team_config)
        # Убрать кнопки из сообщения с текущим last_message_id
        team_config['last_message_id'] = send_message_for_game_dates(
            bot=telegram_bot,
            message=form_game_dates_text(game_dates=team_config['game_dates']),
            keyboard=team_config['game_dates_keyboard'])
    return
