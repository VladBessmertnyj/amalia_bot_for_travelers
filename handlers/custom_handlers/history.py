from itertools import islice

from telebot.types import Message

from database.utils.CRUD import crud
from loader import bot
from states.user_request import UserState


@bot.message_handler(commands=['history'])
def history(message: Message) -> None:
    """Выводит сообщение пользователю с историей поиска отелей."""

    response = crud.retrieve_data(message.from_user.id)

    if len(response):
        lst = list()
        for row in islice(response, 10):
            lst.append(
                '\n\nДата и время запроса: {created_at}\n'
                'Введенная команда: {command}\n'
                'Найденные отели:\n{hotels}'
                .format(
                    created_at=row.created_at,
                    command=row.command,
                    hotels=row.hotels
                )
            )

        message_for_user = ''.join(lst)
        bot.send_message(message.from_user.id, message_for_user)
    else:
        bot.send_message(message.from_user.id, 'Вы пока не сделали ни одного запроса.')
    bot.set_state(message.from_user.id, UserState.standby, message.chat.id)
