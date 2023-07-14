import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import schedule
import time

BASE_URL = 'https://www.saga.hamburg'

def scrape_website():
    url = urljoin(BASE_URL, '/immobiliensuche?type=wohnungen')
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    listings = soup.select('div.teaser3.teaser3--listing.teaser-simple--boxed')

    data_list = []

    for listing in listings:
        link = listing.select_one('a.inner')['href']
        absolute_link = urljoin(BASE_URL, link)  # Construct the absolute URL
        listing_response = requests.get(absolute_link)
        listing_soup = BeautifulSoup(listing_response.text, 'html.parser')

        details = listing_soup.select('dl.dl-props')

        objektnummer = details[0].select_one("dt:-soup-contains('Objektnummer') + dd").get_text(strip=True)
        netto_miete = details[0].select_one("dt:-soup-contains('Netto-Kalt-Miete') + dd").get_text(strip=True)
        gesamtmiete = details[0].select_one("dt:-soup-contains('Gesamtmiete') + dd").get_text(strip=True)
        zimmer = details[0].select_one("dt:-soup-contains('Zimmer') + dd").get_text(strip=True)
        verfugbar_ab = details[0].select_one("dt:-soup-contains('Verfügbar ab') + dd").get_text(strip=True)

        # Создание словаря с извлеченными данными
        data = {
            'Objektnummer': objektnummer,
            'Netto-Kalt-Miete': netto_miete,
            'Gesamtmiete': gesamtmiete,
            'Zimmer': zimmer,
            'Verfügbar ab': verfugbar_ab,
        }

        data_list.append(data)

    # Сохранение данных в файл
    with open('data.json', 'w') as f:
        json.dump(data_list, f)

    # Запись результатов в лог
    with open('log.txt', 'a') as log_file:
        log_file.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")} - Scraped {len(data_list)} listings\n')

def schedule_scraping():
    schedule.every(9).seconds.do(scrape_website)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    schedule_scraping()
