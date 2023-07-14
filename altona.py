import requests
from bs4 import BeautifulSoup
from telegram import Bot
import time

# URL сайта для скрапинга
url = 'https://2222820.hpm.immosolve.eu/?startRoute=result-list&objectIdentifier=2'

# Отключение проверки сертификата
requests.packages.urllib3.disable_warnings()

def check_results():
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.content, 'html.parser')
    result_element = soup.find('div', class_='no_results')
    if result_element is not None:
        result_text = result_element.text.strip()
        if result_text != 'Momentan sind leider keine Immobilien in unserem Angebot verfügbar.':
            # Отправка уведомления в Telegram
            bot_token = '1736081100:AAF2xjTtTjK5jNBVql-rU2bZe8NYcaMm_H4'
            chat_id = '-1001949522816'
            bot = Bot(token=bot_token)
            message = 'Объявления появились на сайте! Ссылка: {}'.format(url)
            bot.send_message(chat_id=chat_id, text=message)
        else:
            print('Ничего нет.')

while True:
    check_results()
    print('Проверка выполнена, работаем, ещё больше ищем, найдём обязательно, держать строй!')
    time.sleep(20)
