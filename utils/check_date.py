from datetime import datetime, timedelta
from telebot.types import Message


def check_date(message: Message, date_string: str | None = None) -> bool:
    """Проверяет правильность написания даты."""

    if date_string:
        date = (datetime.strptime(date_string, '%d.%m.%Y') + timedelta(days=1)).date()
    else:
        date = datetime.today().date()
    try:
        return datetime.strptime(message.text, '%d.%m.%Y').date() >= date
    except ValueError:
        return False
