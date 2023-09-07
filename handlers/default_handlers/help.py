from telebot.types import Message
from config_data.config import DEFAULT_COMMANDS
from loader import bot
from states.user_request import UserState


@bot.message_handler(commands=['help'])
def bot_help(message: Message) -> None:
    """Вызов справки"""

    bot.set_state(message.from_user.id, UserState.standby, message.chat.id)
    text = [f"/{command} - {desk}" for command, desk in DEFAULT_COMMANDS]
    bot.send_message(message.chat.id, "\n".join(text))
