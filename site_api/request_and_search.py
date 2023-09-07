from typing import List, Tuple, Dict
from telebot.types import Message
from requests import codes, get, post
from itertools import islice
from config_data.config import \
    RAPID_API_URL, RAPID_API_KEY, RAPID_API_HOST, LOCATIONS_SEARCH, PROPERTIES_LIST, PROPERTIES_DETAIL
from loader import bot
from utils.exceptions import HotelsNotFoundError


def api_request(method_endswith: str, method_type: str, headers: Dict, params: Dict = None) -> Dict:
    """
    Запрос к API сервиса.

    Args:
        method_endswith (str): Эндпоинт API;
        method_type (str): Тип запроса (GET или POST)
        headers: Dict,
        params: Dict

    """

    url = f'{RAPID_API_URL}{method_endswith}'

    if method_type == 'GET':
        response = get(url, params=params, headers=headers, timeout=15)
        if response.status_code == codes.ok:
            return response.json()
    elif method_type == 'POST':
        response = post(url, json=params, headers=headers, timeout=15)
        if response.status_code == codes.ok:
            return response.json()


def city_founding(message: Message) -> Tuple:
    """Запрос списка ID и названий городов."""

    params = {"q": message.text, "locale": "ru_RU", "langid": "1033", "siteid": "300000001"}
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }
    response = api_request(LOCATIONS_SEARCH, 'GET', headers, params=params)

    cities = list()
    lst = response.get('sr')
    for elem in lst:
        if elem['type'] == 'CITY' or elem['type'] == 'NEIGHBORHOOD':
            cities.append({'city_id': elem.get('gaiaId'), 'city_name': elem.get('regionNames').get('shortName')})
    return tuple(cities)


def hotels_founding(message: Message, number_of_results: int) -> List:
    """Запрос списка отелей с информацией."""

    sort, min_price, max_price = 'PRICE_LOW_TO_HIGH', 1, 9999

    with bot.retrieve_data(message.from_user.id) as data:
        location_id = data['location_id']
        check_in_date = data['check_in_date'].split('.')
        check_out_date = data['check_out_date'].split('.')
        number_of_guests = data['number_of_guests']
        children_list = data['children_list']
        command = data['command']
        if command == 'custom':
            sort = 'DISTANCE'
            min_price = data['min_price']
            max_price = data['max_price']
            min_distance = data['min_distance']
            max_distance = data['max_distance']

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "ru_RU",
        "siteId": 300000001,
        "destination": {"regionId": location_id},
        "checkInDate": {
            "day": int(check_in_date[0]),
            "month": int(check_in_date[1]),
            "year": int(check_in_date[2])
        },
        "checkOutDate": {
            "day": int(check_out_date[0]),
            "month": int(check_out_date[1]),
            "year": int(check_out_date[2])
        },
        "rooms": [
            {
                "adults": number_of_guests,
                "children": children_list
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 200,
        "sort": sort,
        "filters": {"price": {
            "max": max_price,
            "min": min_price
        }}
    }

    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }

    response = api_request(PROPERTIES_LIST, 'POST', headers=headers, params=payload)

    hotels_list = list()
    lst = response.get('data').get('propertySearch').get('properties')

    if command == 'highprice':
        lst = reversed(lst)

    if command == 'custom':
        filtered_lst = list()
        for elem in lst:
            distance = elem.get('destinationInfo').get('distanceFromDestination').get('value')
            if not distance < min_distance and not distance > max_distance:
                filtered_lst.append(elem)
            if len(filtered_lst) >= number_of_results:
                break
        lst = filtered_lst

    if not lst:
        raise HotelsNotFoundError

    for elem in islice(lst, number_of_results):
        hotels_list.append(
            {
                'hotel_id': elem.get('id'),
                'name': elem.get('name'),
                'distance_from_center': elem.get('destinationInfo').get('distanceFromDestination').get('value'),
                'price': elem.get('price').get('lead').get('formatted')
            }
        )
    return hotels_list


def hotel_address_and_photos(hotel_id: str) -> Dict:
    """Запрос адреса и фотографий отеля."""

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "ru_RU",
        "siteId": 300000001,
        "propertyId": hotel_id
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }

    response = api_request(PROPERTIES_DETAIL, 'POST', headers=headers, params=payload)

    data = response.get('data').get('propertyInfo')
    address = data.get('summary').get('location').get('address').get('addressLine')
    lst = data.get('propertyGallery').get('images')
    photos = list()
    for elem in lst:
        photos.append({'description': elem.get('image').get('description'),
                       'url': elem.get('image').get('url')})
    result = {'address': address, 'photos': photos}
    return result
