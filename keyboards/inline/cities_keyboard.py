from typing import Tuple
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def city_markup(cities: Tuple) -> InlineKeyboardMarkup:
    """Возвращает клавиатуру со списком городов."""

    destinations_keyboard = InlineKeyboardMarkup()
    for city in cities:
        destinations_keyboard.add(InlineKeyboardButton(text=city['city_name'], callback_data=str(city['city_id'])))
    return destinations_keyboard
