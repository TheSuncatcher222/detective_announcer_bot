from http import HTTPStatus
import requests
import telegram
from telegram import TelegramError

from project.data.app_data import DATE_HEADLIGHT, EMOJI_NUMBERS, TELEGRAM_USER


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


def rebuild_team_config(
        create_new: bool,
        team_config: dict,
        game_dates: list = None,
        teammate_decision: dict = None) -> None:
    """Rebuild data in team_config.
    If flag create_new is True - create new data for new game_dates.
    Otherwise change exists data according teammate decision."""
    if create_new:
        team_config['game_dates'] = {
            **{
            i + 1: {
                'date_location': game,
                'teammates_count': 0,
                'teammates': {}} for i, game in enumerate(game_dates)},
            0: {
                'date_location': 'Не смогу быть',
                'teammates_count': 0,
                'teammates': {}}}
    else:
        pass
    return


def form_game_dates_text(game_dates: dict) -> str:
    """Form text message from game_dates."""
    abstracts: list[str] = []
    for key in game_dates:
        date_location, teammates_count, teammates = game_dates[key].values()
        abstracts.append(DATE_HEADLIGHT.format(
            number=EMOJI_NUMBERS[key],
            date_location=date_location,
            teammates_count=teammates_count))
        for teammate in teammates:
            abstracts.append(f'{teammate}: {teammates[teammate]}')
    return '\n'.join(abstract for abstract in abstracts)


def send_message(bot, message: str, chat_id: int = TELEGRAM_USER) -> None:
    """Send message to target telegram user/chat."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_USER,
            text=message)
    except TelegramError:
        raise Exception("Bot can't send the message!")
    return


def send_photo(photo_url: str, bot, message: str = None) -> None:
    """Send photo with optional message to target telegram user/chat."""
    try:
        bot.send_photo(
            caption=message,
            chat_id=TELEGRAM_USER,
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
    if 'game_dates' in parsed_post:
        game_dates = rebuild_team_config(
            create_new=True,
            team_config=team_config,
            game_dates=parsed_post['game_dates'])
        game_dates_message = form_game_dates_text(game_dates=game_dates)
        # Убрать кнопки из сообщения с текущим last_message_id
        send_message(
            bot=telegram_bot, message=game_dates_message)
        # получить новый message_id и вписать его в словарь
    return
