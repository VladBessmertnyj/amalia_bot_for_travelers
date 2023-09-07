from itertools import islice
from telebot.types import Message, ReplyKeyboardRemove
from keyboards.reply.yes_no_keyboard import yes_no_markup
from loader import bot
from states.user_request import UserState


def display_hotel_info(message: Message) -> None:
    """Отправляет пользователю сообщение с информацией об отеле."""

    with bot.retrieve_data(message.from_user.id) as data:
        info: str = f"Вывожу информацию о выбранном отеле:\n\n" \
                    f"Название отеля: {data['name']}\n" \
                    f"Адрес отеля: {data['address']}\n" \
                    f"Расстояние до центра города: {data['distance_from_center']} км.\n" \
                    f"Цена: {data['price']}\n"
        bot.send_message(message.from_user.id, info)


def display_hotel_photos(message: Message, photos_number: int) -> None:
    """Отправляет пользователю фотографии отеля."""

    with bot.retrieve_data(message.from_user.id) as data:
        for elem in islice(data['photos'], photos_number):
            bot.send_message(message.from_user.id, elem['description'])
            bot.send_message(message.from_user.id, elem['url'])


def display_info(message: Message, photos_number: int | None = None) -> None:
    """
    Отправляет пользователю информацию об отеле. Отправляет фотографии, если указано их количество.
    Возвращает пользователя на стадию выбора отеля или завершает выполнение команды /lowprice.

    """

    display_hotel_info(message)
    if photos_number:
        display_hotel_photos(message, photos_number)
    with bot.retrieve_data(message.from_user.id) as data:
        if data['hotels_list']:
            bot.send_message(message.from_user.id,
                             'Желаете ли Вы посмотреть остальные отели из списка?',
                             reply_markup=yes_no_markup())
        else:
            bot.send_message(message.from_user.id,
                             'Вы посмотрели все отели из списка, пожалуйста, введите новую команду.',
                             reply_markup=ReplyKeyboardRemove())
            bot.set_state(message.from_user.id, UserState.start, message.chat.id)
