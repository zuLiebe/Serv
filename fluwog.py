import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot
import schedule
import time

# URL сайта для скрапинга
url = 'https://www.fluwog.de/wohnen/wohnungssuche/'

# Токен и ID чата для отправки уведомлений в Telegram
bot_token = '6187859381:AAGQaohroWL-bxwVVf32lLNtBF-WY61A6Js'
chat_id = '-913675079'

def scrape_website():
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    result_element = soup.find('div', class_='col-12')
    result_text = result_element.text.strip() if result_element else ''
    return result_text

def send_telegram_message(message):
    bot = Bot(token=bot_token)
    bot.send_message(chat_id=chat_id, text=message)

def check_results():
    current_results = scrape_website()
    previous_results = ''
    if os.path.isfile('results.txt'):
        with open('results.txt', 'r') as file:
            previous_results = file.read().strip()
    if current_results != previous_results:
        send_telegram_message(f"https://www.fluwog.de/wohnen/wohnungssuche/ Number of results changed: {current_results}")
    with open('results.txt', 'w') as file:
        file.write(current_results)

def schedule_scraping():
    check_results()
    schedule.every(19).seconds.do(check_results)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    schedule_scraping()
