from typing import List
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def hotels_markup(hotels_list: List) -> InlineKeyboardMarkup:
    """Возвращает клавиатуру со списком отелей."""

    hotels_keyboard = InlineKeyboardMarkup()
    for hotel in hotels_list:
        hotels_keyboard.add(InlineKeyboardButton(text=hotel['name'], callback_data=hotel['hotel_id']))
    return hotels_keyboard
