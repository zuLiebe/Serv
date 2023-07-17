import json
from aiogram import Bot, types
import asyncio
import time

# Вставьте свой токен бота и ID чата
bot_token = '1736081100:AAF2xjTtTjK5jNBVql-rU2bZe8NYcaMm_H4'
chat_id = '-1001949522816'

async def send_to_telegram():
    # Чтение данных из файла
    with open('data.json', 'r') as f:
        data = json.load(f)

    # Загрузка ранее отправленных объектов
    sent_objects = load_sent_objects()

    # Фильтрация новых объектов
    new_objects = filter_new_objects(data, sent_objects)

    # Преобразование данных в сообщение
    message = format_message(new_objects)

    # Отправка сообщения в Telegram
    if message:
        bot = Bot(token=bot_token)
        await bot.send_message(chat_id=chat_id, text=message)

    # Сохранение отправленных объектов
    save_sent_objects(data)

def load_sent_objects():
    try:
        with open('sent_objects.json', 'r') as f:
            sent_objects = json.load(f)
    except FileNotFoundError:
        sent_objects = []
    return sent_objects

def filter_new_objects(data, sent_objects):
    new_objects = []
    for item in data:
        if item['Objektnummer'] not in sent_objects:
            new_objects.append(item)
    return new_objects

def format_message(objects):
    message = ''
    for item in objects:
        message += f"Objektnummer: {item['Objektnummer']}\n"
        message += f"Netto-Kalt-Miete: {item['Netto-Kalt-Miete']}\n"
        message += f"Gesamtmiete: {item['Gesamtmiete']}\n"
        message += f"Zimmer: {item['Zimmer']}\n"
        message += f"Verfügbar ab: {item['Verfügbar ab']}\n\n"
        message += f"Link: {item['Link']}\n\n"
    return message.strip()

def save_sent_objects(data):
    sent_objects = [item['Objektnummer'] for item in data]
    with open('sent_objects.json', 'w') as f:
        json.dump(sent_objects, f)

async def schedule_sending():
    while True:
        await send_to_telegram()
        await asyncio.sleep(5)  # Ожидание 5 секунд перед повторным выполнением

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(schedule_sending())
