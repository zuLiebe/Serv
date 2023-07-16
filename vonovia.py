import json
import schedule
import time
import asyncio
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = 'https://www.vonovia.de'

# Вставьте свой токен бота и ID чата
bot_token = '1736081100:AAF2xjTtTjK5jNBVql-rU2bZe8NYcaMm_H4'
chat_id = '-1001949522816'

last_search_time = None
status_message_id = None

async def send_to_telegram(data):
    global last_search_time, status_message_id

    # Чтение данных из файла
    with open('data_code1.json', 'r') as f:
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
        message_id = await send_message(new_objects_message)
        save_message_id(message_id)

        # Здесь можно добавить дополнительные действия при появлении нового объявления
        for new_object in new_objects:
            # Например, отправка дополнительной информации или выполнение других действий
            await process_new_object(new_object)

    # Если нет новых объектов, изменяем сообщение с указанием времени последнего поиска
    else:
        status = f"{last_search_time} жду fluwog.de saga.hamburg altoba.de vonovia.de "
        if status_message_id:
            await edit_message(status)
        else:
            message_id = await send_message(status)
            save_message_id(message_id)

    # Сохранение отправленных объектов
    save_sent_objects(data)

def load_sent_objects():
    try:
        with open('sent_objects_code1.json', 'r') as f:
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
    with open('sent_objects_code1.json', 'w') as f:
        json.dump(sent_objects, f)

def save_message_id(message_id):
    global status_message_id
    status_message_id = message_id
    with open('message_id_code1.txt', 'w') as f:
        f.write(str(message_id))

def load_message_id():
    global status_message_id
    try:
        with open('message_id_code1.txt', 'r') as f:
            status_message_id = int(f.read().strip())
    except FileNotFoundError:
        status_message_id = None

def scrape_website():
    url = urljoin(BASE_URL, '/de-de/immobiliensuche/?rentType=miete&immoType=wohnung&city=Hamburg&perimeter=0&priceMaxRenting=0&priceMinRenting=0&sizeMin=0&sizeMax=0&minRooms=0&dachgeschoss=0&erdgeschoss=0&lift=0&balcony=0&sofortfrei=0&disabilityAccess=0&page=1')
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

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
    with open('data_code1.json', 'w') as f:
        json.dump(data_list, f)

    # Отправка данных в Telegram
    asyncio.create_task(send_to_telegram(data_list))

    # Запись результатов в лог
    with open('log_code1.txt', 'a') as log_file:
        log_file.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")} - Scraped {len(data_list)} listings\n')

async def send_message(text):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    params = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(url, json=params)
    data = response.json()
    message_id = data['result']['message_id']
    return message_id

async def edit_message(text):
    url = f'https://api.telegram.org/bot{bot_token}/editMessageText'
    params = {
        'chat_id': chat_id,
        'message_id': status_message_id,
        'text': text
    }
    requests.post(url, json=params)

async def process_new_object(new_object):
    # Выполнение действий при появлении нового объявления
    # Например, отправка дополнительной информации
    additional_info = f"Новое объявление:\n{new_object['id']}\n{new_object['link']}"
    await send_message(additional_info)

async def schedule_scraping():
    while True:
        await asyncio.sleep(26)
        scrape_website()

if __name__ == '__main__':
    load_message_id()
    asyncio.run(schedule_scraping())
