from telegram import InlineKeyboardButton

BUTTONS_TEAM_CONFIG_SAMPLE: dict[str, list[list[InlineKeyboardButton]]] = {
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
    3: [
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
    5: [
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