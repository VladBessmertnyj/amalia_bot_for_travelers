from telebot.types import Message
from loader import bot
from states.user_request import UserState


@bot.message_handler(commands=['start'])
def bot_start(message: Message) -> None:
    """Запуск бота"""

    bot.send_message(message.chat.id, 'Привет, меня зовут Амалия!')
    bot.set_state(message.from_user.id, UserState.standby, message.chat.id)
