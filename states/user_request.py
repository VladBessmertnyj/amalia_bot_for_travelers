from telebot.handler_backends import State, StatesGroup


class UserState(StatesGroup):
    standby = State()
    start = State()
    city_name = State()
    location_id = State()
    price_range = State()
    distance_range = State()
    check_in_date = State()
    check_out_date = State()
    number_of_guests = State()
    children_number_and_age = State()
    children_list = State()
    hotels_list = State()
    hotel_photos = State()
    photos_number = State()
    return_to_hotel_list = State()
