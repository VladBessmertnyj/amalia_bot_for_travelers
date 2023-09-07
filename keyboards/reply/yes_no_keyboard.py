from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def yes_no_markup() -> ReplyKeyboardMarkup:
    """Возвращает клавиатуру c кнопками 'Да' и 'Нет'"""

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text='Да'))
    keyboard.add(KeyboardButton(text='Нет'))
    return keyboard
