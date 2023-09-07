import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
RAPID_API_HOST = 'hotels4.p.rapidapi.com'
RAPID_API_URL = 'https://hotels4.p.rapidapi.com/'
LOCATIONS_SEARCH = 'locations/v3/search'
PROPERTIES_LIST = 'properties/v2/list'
PROPERTIES_DETAIL = 'properties/v2/detail'
DEFAULT_COMMANDS = (
    ('start', 'Запустить бота'),
    ('help', 'Вывести справку'),
    ('lowprice', 'Найти самые дешевые отели в городе'),
    ('highprice', 'Найти самые дорогие отели в городе'),
    ('custom', 'Найти отели, наиболее подходящие по цене и расположению от центра'),
    ('history', 'Вывести последние 10 запросов из истории поиска отелей')
)
