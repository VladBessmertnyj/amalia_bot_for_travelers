from datetime import datetime
from typing import List, Dict

from requests import Timeout
from telebot.types import Message, ReplyKeyboardRemove, CallbackQuery

from loader import bot
from site_api.request_and_search import hotels_founding, city_founding, hotel_address_and_photos
from states.user_request import UserState
from keyboards.inline.cities_keyboard import city_markup
from keyboards.inline.hotels_keyboard import hotels_markup
from keyboards.reply.yes_no_keyboard import yes_no_markup
from utils.check_date import check_date
from utils.check_children_age import check_children_age
from utils.display_hotel_info import display_info
from utils.exceptions import HotelsNotFoundError
from utils.value_range import value_range
from database.utils.CRUD import crud


def create_database_record(user_id: int, command: str, hotels_list: List) -> List[Dict]:
    """Создает словарь для загрузки в базу данных истории запросов пользователя."""

    hotels_names = list()
    for hotel in hotels_list:
        hotels_names.append(f"{hotel['name']}")
    hotels = '\n'.join(hotels_names)
    data = [
        {
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'user_id': user_id,
            'command': command,
            'hotels': hotels
        }
    ]
    return data


@bot.message_handler(commands=['lowprice', 'highprice', 'custom'])
def start(message: Message) -> None:
    """Запрашивает у пользователя название города, в котором нужно найти отели."""

    bot.send_message(message.from_user.id, 'В каком городе нужно найти отели?')
    bot.set_state(message.from_user.id, UserState.start, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['command'] = message.text[1:]


@bot.message_handler(state=UserState.start)
def get_city_name(message: Message) -> None:
    """Выводит клавиатуру с названиями районов города."""

    try:
        bot.send_message(message.from_user.id, 'Ищу город, пожалуйста, подождите.')
        cities = city_founding(message)
        if cities:
            bot.send_message(message.from_user.id, 'Уточните, пожалуйста:', reply_markup=city_markup(cities))
            bot.set_state(message.from_user.id, UserState.city_name, message.chat.id)
        else:
            bot.send_message(message.from_user.id, 'Извините, такой город не найден, пожалуйста,'
                                                   ' введите другое название.')
    except Timeout:
        bot.send_message(message.from_user.id, 'Сервер не отвечает, пожалуйста, попробуйте еще раз.')
    except TypeError:
        bot.send_message(message.from_user.id, 'Не удалось вывести список городов, пожалуйста, попробуйте еще раз.')
    except AttributeError:
        bot.send_message(message.from_user.id,
                         'Не удалось получить данные с сервера, пожалуйста, попробуйте еще раз.')


@bot.callback_query_handler(func=lambda query: True, state=UserState.city_name)
def get_location_id(query: CallbackQuery) -> None:
    """
    Получает ID локации из функции обратного вызова. Если введена команда 'custom', запрашивает у пользователя
    минимальную и максимальную цену. Если 'lowprice' или 'highprice' - предполагаемую дату заселения.

    """

    bot.answer_callback_query(query.id)

    with bot.retrieve_data(query.from_user.id) as data:
        data['location_id'] = query.data

    if data['command'] == 'custom':
        bot.send_message(query.from_user.id, 'Введите минимальную и максимальную цену через дефис (например, 100-300).')
        bot.set_state(query.from_user.id, UserState.location_id)
    else:
        bot.send_message(query.from_user.id, 'Введите предполагаемую дату заселения в формате d.mm.yyyy.')
        bot.set_state(query.from_user.id, UserState.distance_range)


@bot.message_handler(state=UserState.location_id)
def get_price_range(message: Message) -> None:
    """Получает диапазон цен, и запрашивает диапазон расстояний."""

    try:
        price_range = value_range(message.text)

        with bot.retrieve_data(message.from_user.id) as data:
            data['min_price'] = price_range[0]
            data['max_price'] = price_range[1]

        bot.send_message(message.from_user.id,
                         'Введите минимальное и максимальное расстояние от центра в километрах '
                         'через дефис (например, 0-3 или 5-10).')
        bot.set_state(message.from_user.id, UserState.price_range)
    except ValueError:
        bot.send_message(message.from_user.id, 'Некорректный ввод, пожалуйста, попробуйте еще раз.')


@bot.message_handler(state=UserState.price_range)
def get_distance_range(message: Message) -> None:
    """Получает диапазон расстояний и запрашивает предполагаемую дату заселения."""

    try:
        distance_range = value_range(message.text)

        with bot.retrieve_data(message.from_user.id) as data:
            data['min_distance'] = distance_range[0]
            data['max_distance'] = distance_range[1]

        bot.send_message(message.from_user.id, 'Введите предполагаемую дату заселения в формате d.mm.yyyy.')
        bot.set_state(message.from_user.id, UserState.distance_range)
    except ValueError:
        bot.send_message(message.from_user.id, 'Некорректный ввод, пожалуйста, попробуйте еще раз.')


@bot.message_handler(state=UserState.distance_range)
def get_check_in_date(message: Message) -> None:
    """Получает предполагаемую дату заселения и запрашивает предполагаемую дату выселения."""

    if check_date(message):

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['check_in_date'] = message.text

        bot.send_message(message.from_user.id, 'Теперь введите предполагаемую дату выселения.')
        bot.set_state(message.from_user.id, UserState.check_in_date)
    else:
        bot.send_message(message.from_user.id, 'Дата должна быть в формате d.mm.yyyy и должна быть равна или больше '
                                               'текущей даты. Пожалуйста, попробуйте еще раз.')


@bot.message_handler(state=UserState.check_in_date)
def get_check_out_date(message: Message) -> None:
    """Получает предполагаемую дату выселения и запрашивает количество взрослых постояльцев"""

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if check_date(message, data['check_in_date']):
            bot.send_message(message.from_user.id, 'Введите количество взрослых постояльцев '
                                                   '(от 18 лет, максимум 14 человек).')
            data['check_out_date'] = message.text

            bot.set_state(message.from_user.id, UserState.check_out_date, message.chat.id)
        elif check_date(message) and data['check_in_date'] >= message.text:
            bot.send_message(message.from_user.id, 'Дата выселения должна быть хотя бы на 1 день позже даты заселения')
        else:
            bot.send_message(message.from_user.id, 'Дата должна быть в формате d.mm.yyyy и должна быть позже '
                                                   'даты заселения. Пожалуйста, попробуйте еще раз.')


@bot.message_handler(state=UserState.check_out_date)
def get_number_of_guests(message: Message) -> None:
    """Получает количество взрослых постояльцев и запрашивает, есть ли дети."""

    if message.text.isdigit() and 0 < int(message.text) < 15:
        bot.send_message(message.from_user.id, 'С детьми?', reply_markup=yes_no_markup())

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['number_of_guests'] = int(message.text)

        bot.set_state(message.from_user.id, UserState.number_of_guests, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Количество постояльцев должно выражаться целым числом '
                                               'и не может быть больше 14-ти.')


@bot.message_handler(state=UserState.number_of_guests)
def get_children_number_and_age(message: Message) -> None:
    """
    Если пользователь ответил 'Да' на вопрос, есть ли дети, запрашивает их возраст и количество.
    Если 'Нет', запрашивает, сколько отелей вывести на экран.

    """

    if message.text == 'Да':
        bot.send_message(message.from_user.id, 'Введите возраст детей через пробел (до 18-ти лет, максимум 6 детей).',
                         reply_markup=ReplyKeyboardRemove())
        bot.set_state(message.from_user.id, UserState.children_number_and_age, message.chat.id)
    elif message.text == 'Нет':
        bot.send_message(message.from_user.id, 'Сколько отелей вывести на экран? (Не более 10)',
                         reply_markup=ReplyKeyboardRemove())
        bot.set_state(message.from_user.id, UserState.children_list, message.chat.id)

        with bot.retrieve_data(message.from_user.id) as data:
            data['children_list'] = []

    else:
        bot.send_message(message.from_user.id, 'Некорректный ввод, пожалуйста, попробуйте еще раз.')


@bot.message_handler(state=UserState.children_number_and_age)
def get_children_list(message: Message) -> None:
    """Получает возраст и количество детей и запрашивает, сколько отелей вывести на экран."""

    age_list = message.text.split()
    if check_children_age(age_list):

        with bot.retrieve_data(message.from_user.id) as data:
            data['children_list'] = [{'age': int(i)} for i in age_list]

        bot.send_message(message.from_user.id, 'Сколько отелей вывести на экран? (Не более 10)')
        bot.set_state(message.from_user.id, UserState.children_list, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Возраст детей может выражаться только целыми положительными числами '
                                               'и не может быть больше 17 лет.')


@bot.message_handler(state=UserState.children_list)
def get_hotels_list(message: Message) -> None:
    """
    Запрашивает с сервера список отелей и выводит клавиатуру с их названиями.
    Добавляет запись в базу данных истории поиска отелей.

    """

    if message.text.isdigit() and 0 < int(message.text) <= 10:
        bot.send_message(message.from_user.id, 'Запрашиваю список отелей, пожалуйста, подождите.')
        number_of_results = int(message.text)

        try:
            with bot.retrieve_data(message.from_user.id) as data:
                data['hotels_list'] = hotels_founding(message, number_of_results)
                bot.send_message(message.from_user.id,
                                 'Выберите отель для получения подробной информации:',
                                 reply_markup=hotels_markup(data['hotels_list']))

            crud.add_data(create_database_record(message.from_user.id, data['command'], data['hotels_list']))
            bot.set_state(message.from_user.id, UserState.hotels_list, message.chat.id)

        except Timeout:
            bot.send_message(message.from_user.id, 'Сервер не отвечает, пожалуйста, попробуйте еще раз.')
        except TypeError:
            bot.send_message(message.from_user.id, 'Ошибка сервиса: не удалось получить список отелей. '
                                                   'Пожалуйста, попробуйте еще раз.')
        except AttributeError:
            bot.send_message(message.from_user.id,
                             'Не удалось получить данные с сервера, пожалуйста, попробуйте еще раз.')
        except HotelsNotFoundError:
            bot.send_message(message.from_user.id, 'Подходящие отели не найдены. Пожалуйста, введите новую команду.')
            bot.set_state(message.from_user.id, UserState.standby, message.chat.id)

    else:
        bot.send_message(message.from_user.id, 'Количество выводимых отелей должно быть выражено целым числом и'
                                               ' не может быть меньше 1 и больше 10.')


@bot.callback_query_handler(func=lambda query: True, state=UserState.hotels_list)
def get_hotel_info(query: CallbackQuery) -> None:
    """
    Получает ID отеля из функции обратного вызова и запрашивает с сервера информацию о выбранном отеле
    и удаляет отель из списка для клавиатуры. Спрашивает пользователя, вывести ли фотографии отеля на экран,
    и выводит клавиатуру с вариантами ответов.

    """

    bot.answer_callback_query(query.id)
    bot.send_message(query.from_user.id, 'Загружаю информацию, пожалуйста, подождите.')

    try:
        with bot.retrieve_data(query.from_user.id) as data:
            for hotel in data['hotels_list']:
                if query.data == hotel['hotel_id']:
                    address_and_photos = hotel_address_and_photos(query.data)
                    data['name'] = hotel['name']
                    data['address'] = address_and_photos['address']
                    data['distance_from_center'] = hotel['distance_from_center']
                    data['price'] = hotel['price']
                    data['photos'] = address_and_photos['photos']
                    data['hotels_list'].remove(hotel)
                    break

        bot.send_message(query.from_user.id, 'Показать фотографии отеля?', reply_markup=yes_no_markup())
        bot.set_state(query.from_user.id, UserState.hotel_photos)

    except Timeout:
        bot.send_message(query.from_user.id, 'Сервер не отвечает, пожалуйста, попробуйте еще раз.')
    except TypeError:
        bot.send_message(query.from_user.id, 'Не удалось вывести список отелей, пожалуйста, попробуйте еще раз.')
    except AttributeError:
        bot.send_message(query.from_user.id,
                         'Не удалось получить данные с сервера, пожалуйста, попробуйте еще раз.')


@bot.message_handler(state=UserState.hotel_photos)
def get_photos_number(message: Message) -> None:
    """
    При выборе 'Да' спрашивает пользователя, сколько фотографий загрузить.
    При выборе 'Нет' выводит информацию об отеле без фото и возвращает пользователя
    на стадию выбора отеля с клавиатуры.

    """

    if message.text == 'Да':
        bot.send_message(message.from_user.id,
                         'Сколько фотографий загрузить? (Не более 5)',
                         reply_markup=ReplyKeyboardRemove())
        bot.set_state(message.from_user.id, UserState.photos_number, message.chat.id)
    elif message.text == 'Нет':
        display_info(message)
        bot.set_state(message.from_user.id, UserState.return_to_hotel_list)


@bot.message_handler(state=UserState.photos_number)
def display_info_with_photos(message: Message) -> None:
    """Выводит информацию об отеле с фотографиями."""

    if message.text.isdigit() and 0 < int(message.text) <= 5:
        display_info(message, int(message.text))
        bot.set_state(message.from_user.id, UserState.return_to_hotel_list)
    else:
        bot.send_message(message.from_user.id, 'Количество выводимых фотографий должно быть выражено целым числом и'
                                               ' не может быть меньше 1 и больше 5.')


@bot.message_handler(state=UserState.return_to_hotel_list)
def finishing(message: Message) -> None:
    """
    При выборе 'Да' выводит клавиатуру с непросмотренными отелями.
    При выборе 'Нет' завершает выполнение команды.

    """

    if message.text == 'Да':
        bot.send_message(message.from_user.id, 'Вас поняла.', reply_markup=ReplyKeyboardRemove())

        with bot.retrieve_data(message.from_user.id) as data:
            bot.send_message(message.from_user.id,
                             'Выберите отель для получения подробной информации:',
                             reply_markup=hotels_markup(data['hotels_list']))

        bot.set_state(message.from_user.id, UserState.hotels_list, message.chat.id)

    elif message.text == 'Нет':
        bot.send_message(message.from_user.id,
                         'Вас поняла. Пожалуйста, введите новую команду.',
                         reply_markup=ReplyKeyboardRemove())
        bot.set_state(message.from_user.id, UserState.standby, message.chat.id)
