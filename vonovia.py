import json
import schedule
import time
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from urllib.parse import urljoin
import logging


BASE_URL = 'https://www.vonovia.de'

# Вставьте свой токен бота
bot_token = '6187859381:AAGQaohroWL-bxwVVf32lLNtBF-WY61A6Js'
chat_id = '-913675079'

bot = Bot(token=bot_token)
dispatcher = Dispatcher(bot)
last_search_time = None
status_message_id = None
# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def send_to_telegram(data):
    global last_search_time, status_message_id

    # Чтение данных из файла
    with open('data.json', 'r') as f:
        previous_data = json.load(f)

    # Загрузка ранее отправленных объектов
    sent_objects = load_sent_objects()

    # Фильтрация новых объектов
    new_objects = filter_new_objects(data, previous_data, sent_objects)

    # Преобразование данных в сообщение
    message = format_message(new_objects)

    # Обновление времени последнего поиска
    last_search_time = time.strftime('%H:%M:%S')

    # Если есть новые объекты, отправляем новое сообщение
    if new_objects:
        new_objects_message = format_message(new_objects)
        if status_message_id:
            await bot.edit_message_text(chat_id=chat_id, message_id=status_message_id, text=new_objects_message)
        else:
            status_message = await bot.send_message(chat_id=chat_id, text=new_objects_message)
            status_message_id = status_message.message_id
            save_status_message_id(status_message_id)

        # Обработка команд из сообщения
        process_commands(new_objects_message)

    # Если нет новых объектов, изменяем сообщение с указанием времени последнего поиска
    else:
        status = f"Нет новых объектов :с {last_search_time}"
        if status_message_id:
            await bot.edit_message_text(chat_id=chat_id, message_id=status_message_id, text=status)
        else:
            status_message = await bot.send_message(chat_id=chat_id, text=status)
            status_message_id = status_message.message_id
            save_status_message_id(status_message_id)
            logging.info(status)

    # Сохранение отправленных объектов
    save_sent_objects(data)

def load_sent_objects():
    try:
        with open('sent_objects.json', 'r') as f:
            sent_objects = json.load(f)
    except FileNotFoundError:
        sent_objects = []
    return sent_objects

def filter_new_objects(data, previous_data, sent_objects):
    new_objects = []
    for item in data:
        if item['id'] not in sent_objects and item not in previous_data:
            new_objects.append(item)
    return new_objects

def format_message(objects):
    message = ''
    for item in objects:
        message += f"Objektnummer: {item['id']}\n"
        message += f"Kaltmiete: {item['price']} EUR\n"
        message += f"Größe: {item['size']} m²\n"
        message += f"Zimmer: {item['rooms']}\n"
        message += f"Link: {item['link']}\n\n"
    return message.strip()

def save_sent_objects(data):
    sent_objects = [item['id'] for item in data]
    with open('sent_objects.json', 'w') as f:
        json.dump(sent_objects, f)

async def scrape_website():
    async with aiohttp.ClientSession() as session:
        url = urljoin(BASE_URL, '/de-de/immobiliensuche/?rentType=miete&immoType=wohnung&city=Hamburg&perimeter=0&priceMaxRenting=0&priceMinRenting=0&sizeMin=0&sizeMax=0&minRooms=0&dachgeschoss=0&erdgeschoss=0&lift=0&balcony=0&sofortfrei=0&disabilityAccess=0&page=1')
        response = await session.get(url)
        response_text = await response.text()

        soup = BeautifulSoup(response_text, 'html.parser')

        listings = soup.select('article.molecule-result-list-item')

        data_list = []

        for listing in listings:
            link = listing.select_one('a.img-default')['href']
            absolute_link = urljoin(BASE_URL, link)  # Construct the absolute URL
            price = listing.select_one('li:nth-of-type(1) span.value').text.strip()
            size = listing.select_one('li:nth-of-type(2) span.value').text.strip()
            rooms = listing.select_one('li:nth-of-type(3) span.value').text.strip()
            listing_id = link.split('/')[-1]

            # Создание словаря с извлеченными данными
            data = {
                'id': listing_id,
                'price': price,
                'size': size,
                'rooms': rooms,
                'link': absolute_link
            }

            data_list.append(data)

        # Сохранение данных в файл
        with open('data.json', 'w') as f:
            json.dump(data_list, f)

        # Отправка данных в Telegram
        await send_to_telegram(data_list)

        # Логирование количества объектов
        logging.info(f'Scraped {len(data_list)} listings')

        # Запись результатов в лог
        with open('log.txt', 'a') as log_file:
            log_file.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")} - Scraped {len(data_list)} listings\n')

        # Логирование статуса выполнения расписания
            logging.info('Schedule running')

def save_status_message_id(status_message_id):
    with open('status_message_id.txt', 'w') as f:
        f.write(str(status_message_id))

def load_status_message_id():
    try:
        with open('status_message_id.txt', 'r') as f:
            return int(f.read())
    except FileNotFoundError:
        return None

def schedule_scraping():
    loop = asyncio.get_event_loop()
    loop.create_task(scrape_website())

    schedule.every(6).seconds.do(lambda: asyncio.run_coroutine_threadsafe(scrape_website(), loop))
    while True:
        schedule.run_pending()
        time.sleep(1)

def process_commands(message):
    # Разбиваем сообщение на отдельные строки
    lines = message.strip().split('\n')

    # Проверяем каждую строку на наличие команды
    for line in lines:
        if line.startswith('/price_threshold'):
            handle_price_threshold_command(line)

async def start_handler(event: types.Message):
    # Обрабатываем команду /start
    global status_message_id
    if event.chat.id == chat_id:
        status_message_id = event.reply_to_message.message_id
        save_status_message_id(status_message_id)

if __name__ == '__main__':
    logging.info('Script started')
    status_message_id = load_status_message_id()
    dispatcher.register_message_handler(start_handler, commands=['start'], content_types=[types.ContentType.NEW_CHAT_MEMBERS])
    schedule_scraping()
