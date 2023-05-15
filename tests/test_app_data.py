class InlineKeyboardButton():

    def __init__(self, text, callback_data):
        self.text = text
        self.callback_data = callback_data
    
    def __repr__(self):
        return f"InlineKeyboardButton(text='{self.text}', callback_data='{self.callback_data}')"

# Для 1 - 3 игр