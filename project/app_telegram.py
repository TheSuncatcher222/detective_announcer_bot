from http import HTTPStatus
import requests
import telegram
from telegram import TelegramError, InlineKeyboardMarkup, InlineKeyboardButton

from project.data.app_data import (
    DATE_HEADLIGHT, EMOJI_SYMBOLS, TEAM_CONFIG_BUTTONS, TEAM_GUEST,
    TELEGRAM_TEAM_CHAT)


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


def edit_message(
        bot,
        team_config: dict[str, any],
        chat_id: str = TELEGRAM_TEAM_CHAT,
        enable_markup: bool = True) -> None:
    """Edit target message in target telegram chat.
    If enable_markup is True add markup to message."""
    keys: list[list[InlineKeyboardButton]] | None = TEAM_CONFIG_BUTTONS.get(
        team_config['game_count'], None) if enable_markup else None
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=team_config['last_message_id'],
        text=_form_game_dates_text(game_dates=team_config['game_dates']),
        reply_markup=InlineKeyboardMarkup(keys) if keys else None)
    return


def rebuild_team_config_game_dates(
        team_config: dict[str, any],
        teammate_decision: dict[str, str | int]) -> bool:
    """Rebuild data in team_config according teammate decision."""
    if not teammate_decision:
        return False
    teammate: str = teammate_decision['teammate']
    game_num: int = teammate_decision['game_num']
    decision: int = teammate_decision['decision']
    if decision == 1:
        if game_num == 0 and teammate not in team_config[
                'game_dates'][game_num]['teammates']:
            team_config['game_dates'][game_num]['teammates'][teammate] = 1
            for i in range(1, team_config['game_count']):
                team_config['game_dates'][i]['teammates'].pop(teammate, None)
            return True
        elif game_num != 0:
            team_config['game_dates'][0]['teammates'].pop(teammate, None)
            if teammate not in team_config[
                    'game_dates'][game_num]['teammates']:
                team_config[
                    'game_dates'][game_num]['teammates'][teammate] = 0
            team_config['game_dates'][game_num]['teammates'][teammate] += 1
            return True
    else:
        if teammate in team_config['game_dates'][game_num]['teammates']:
            team_config['game_dates'][game_num]['teammates'][teammate] -= 1
            if team_config['game_dates'][game_num]['teammates'][teammate] == 0:
                del team_config['game_dates'][game_num]['teammates'][teammate]
            return True
    return False


def send_message(bot, message: str, chat_id: int = TELEGRAM_TEAM_CHAT) -> None:
    """Send message to target telegram chat."""
    try:
        bot.send_message(
            chat_id=chat_id,
            text=message)
        return
    except TelegramError:
        raise Exception("Bot can't send the message!")


def _create_new_team_config_game_dates(
        game_dates: list[str], team_config: dict[str, any]) -> None:
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
    return


def _form_game_dates_text(game_dates: dict) -> str:
    """Form text message from game_dates."""
    abstracts: list[str] = []
    for num in game_dates:
        date_location, teammates = game_dates[num].values()
        abstracts.append(DATE_HEADLIGHT.format(
            number=EMOJI_SYMBOLS[num],
            date_location=date_location))
        for teammate, count in teammates.items():
            abstracts.append(f'• {teammate}')
            for _ in range(1, count):
                abstracts.append(f'• {teammate} {TEAM_GUEST}')
        abstracts.append('')
    return '\n'.join(abstracts)


def _pin_message(
        bot,
        message_id: int,
        chat_id: int = TELEGRAM_TEAM_CHAT,
        unpin: bool = False) -> None:
    """Pin / unpin message in telegram chat."""
    if not unpin:
        bot.pinChatMessage(chat_id=chat_id, message_id=message_id)
    else:
        bot.unpinChatMessage(chat_id=chat_id, message_id=message_id)


def _send_message_for_game_dates(
        bot,
        message: str,
        keyboard: list[list[InlineKeyboardButton]],
        chat_id: int = TELEGRAM_TEAM_CHAT) -> int:
    """Send message with game dates and keyboard to target telegram chat.
    Return message id."""
    try:
        message: any = bot.send_message(
            chat_id=chat_id,
            reply_markup=InlineKeyboardMarkup(keyboard),
            text=message)
        return message.message_id
    except TelegramError as err:
        raise Exception(f"Bot can't send the message! {err}")


def _send_photo(
        bot,
        photo_url: str,
        message: str = None,
        chat_id: int = TELEGRAM_TEAM_CHAT) -> None:
    """Send photo with optional message to target telegram chat."""
    try:
        bot.send_photo(
            caption=message,
            chat_id=chat_id,
            photo=photo_url)
    except TelegramError as err:
        raise Exception(f'Bot failed to send photo-message! Error: {err}')
    return


def send_update(
        parsed_post: dict[str, any],
        team_config: dict[str, any],
        telegram_bot) -> None:
    """Send update from VK group wall to target telegram chat."""
    _send_photo(
        bot=telegram_bot,
        message='\n\n'.join(s for s in parsed_post['post_text']),
        photo_url=parsed_post['post_image_url'])
    if parsed_post['game_dates']:
        if team_config['last_message_id']:
            _pin_message(
                bot=telegram_bot,
                message_id=team_config['last_message_id'],
                unpin=True)
            edit_message(
                bot=telegram_bot, team_config=team_config, enable_markup=False)
        _create_new_team_config_game_dates(
            game_dates=parsed_post['game_dates'], team_config=team_config)
        team_config['last_message_id'] = _send_message_for_game_dates(
            bot=telegram_bot,
            message=_form_game_dates_text(
                game_dates=team_config['game_dates']),
            keyboard=TEAM_CONFIG_BUTTONS.get(team_config['game_count'], None))
        _pin_message(
            bot=telegram_bot, message_id=team_config['last_message_id'])
    return
