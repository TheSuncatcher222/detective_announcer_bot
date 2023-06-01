from http import HTTPStatus
import requests
from telegram import (
    Bot as TelegramBot,
    TelegramError, InlineKeyboardMarkup, InlineKeyboardButton)

from project.data.app_data import (
    ALIBI, ALIBI_TAG, DETECTIT_TAG,

    BUTTONS_TEAM_CONFIG_ALIBI, BUTTONS_TEAM_CONFIG_DETECTIT,

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


def edit_message(
        bot,
        message_id: int,
        new_text: str,
        chat_id: str = TELEGRAM_TEAM_CHAT,
        reply_markup: bool = None) -> None:
    """Edit target message in the telegram chat.
    Add reply_markup to the message if reply_markup is not None."""
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=new_text,
        reply_markup=reply_markup)
    return


def form_game_dates_text(group_name: str, team_config: dict[int, dict]) -> str:
    """Form text message from game_dates."""
    if group_name == ALIBI:
        tag: str = ALIBI_TAG
    else:
        tag = DETECTIT_TAG
    abstracts: list[str] = [tag, '']
    for num in team_config:
        date_location, teammates = team_config[num].values()
        if num != 0:
            symbol: str = EMOJI_SYMBOLS[num]
        else:
            symbol: str = EMOJI_SYMBOLS[group_name]['skip']
        abstracts.append(DATE_HEADLIGHT.format(
            number=symbol,
            date_location=date_location))
        for teammate, count in teammates.items():
            abstracts.append(f'• {teammate}')
            for _ in range(1, count):
                abstracts.append(f'• {teammate} {TEAM_GUEST}')
        abstracts.append('')
    return '\n'.join(abstracts)


def init_telegram_bot(token: str) -> TelegramBot:
    """Initialize telegram bot."""
    return TelegramBot(token=token)


def rebuild_team_config(
        team_config: dict[str, any],
        teammate_decision: dict[str, str | int]) -> dict[str, any]:
    """Rebuild data in team_config according teammate decision and return."""
    if not teammate_decision:
        return None
    teammate: str = teammate_decision['teammate']
    game_num: int = teammate_decision['game_num']
    decision: int = teammate_decision['decision']
    if decision == 1:
        if game_num == 0 and teammate not in team_config[0]['teammates']:
            team_config[0]['teammates'][teammate] = 1
            for i in range(1, len(team_config)):
                team_config[i]['teammates'].pop(teammate, None)
        elif game_num != 0:
            team_config[0]['teammates'].pop(teammate, None)
            if teammate not in team_config[game_num]['teammates']:
                team_config[game_num]['teammates'][teammate] = 0
            team_config[game_num]['teammates'][teammate] += 1
    else:
        if teammate in team_config[game_num]['teammates']:
            team_config[game_num]['teammates'][teammate] -= 1
            if team_config[game_num]['teammates'][teammate] == 0:
                del team_config[game_num]['teammates'][teammate]
    return team_config


def send_message(
        bot,
        message: str,
        chat_id: int = TELEGRAM_TEAM_CHAT,
        return_message_id: bool = False) -> None | int:
    """Send message to target telegram chat.
    If return_message_id return sended message id."""
    try:
        message: any = bot.send_message(chat_id=chat_id, text=message)
        if return_message_id:
            return message.message_id
        return
    except TelegramError:
        raise Exception("Bot can't send the message!")


def send_update_message(
        group_name: str,
        message: str,
        saved_data: dict[str, int | dict[str, any]],
        telegram_bot: TelegramBot) -> None:
    """Send update from VK group chat to the telegram chat."""
    if group_name == ALIBI:
        key_team: str = 'pinned_vk_message_id_alibi'
    else:
        key_team: str = 'pinned_vk_message_id_detectit'
    pinned_message_id: int = saved_data[key_team]
    if pinned_message_id:
        _pin_message(
            bot=telegram_bot,
            message_id=pinned_message_id,
            unpin=True)
    new_pinned_message: int = send_message(
        bot=telegram_bot, message=message, return_message_id=True)
    _pin_message(bot=telegram_bot, message_id=new_pinned_message)
    saved_data[key_team] = new_pinned_message
    return


def send_update_wall(
        group_name: str,
        parsed_post: dict[str, any],
        saved_data: dict[str, int | dict[str, any]],
        telegram_bot) -> None:
    """Send update from VK group wall to the telegram chat."""
    _send_photo(
        bot=telegram_bot,
        message='\n\n'.join(abstract for abstract in parsed_post['post_text']),
        photo_url=parsed_post['post_image_url'])
    if not parsed_post['game_dates']:
        return
    if group_name == ALIBI:
        buttons = BUTTONS_TEAM_CONFIG_ALIBI
        key_team: str = 'team_config_alibi'
    else:
        buttons = BUTTONS_TEAM_CONFIG_DETECTIT
        key_team: str = 'team_config_detectit'
    pinned_message_id: int = saved_data[key_team].get(
        'pinned_telegram_message_id', False)
    if pinned_message_id:
        edit_message(
            bot=telegram_bot,
            message_id=pinned_message_id,
            new_text=form_game_dates_text(
                game_dates=saved_data[key_team]['game_dates']))
        _pin_message(
            bot=telegram_bot,
            message_id=pinned_message_id,
            unpin=True)
    new_game_dates: dict[int, dict[str, any]] = (
        _create_new_team_config_game_dates(
            game_dates=parsed_post['game_dates']))
    new_pinned_message: int = _send_message_for_game_dates(
        bot=telegram_bot,
        message=form_game_dates_text(game_dates=new_game_dates),
        keyboard=buttons.get(len(new_game_dates), None))
    _pin_message(bot=telegram_bot, message_id=new_pinned_message)
    saved_data[key_team]['game_dates'] = new_game_dates
    saved_data[key_team]['pinned_telegram_message_id'] = new_pinned_message
    return


def _create_new_team_config_game_dates(
        game_dates: list[str]) -> dict[int, dict[str, any]]:
    """Create new data in team_config for new game_dates."""
    return {
        **{
            i + 1: {
                'date_location': game,
                'teammates': {}} for i, game in enumerate(game_dates)},
        0: {
            'date_location': 'Не смогу быть',
            'teammates': {}}}


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
            caption=message if len(message) < 1024 else (
                message[:1000] + ' ... (сообщение слишком длинное)'),
            chat_id=chat_id,
            photo=photo_url)
        return
    except TelegramError as err:
        raise Exception(f'Bot failed to send photo-message! Error: "{err}"')
