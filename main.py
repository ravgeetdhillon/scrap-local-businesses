"""
Main Module for the App.
"""

import json
import os
import re
import requests
from bs4 import BeautifulSoup


def save_json(data, filename):
    """
    Save the `data` to JSON file with `filename`.
    """

    with open(filename, 'w', encoding='utf-8') as fl:
        json.dump(data, fl, ensure_ascii=False, indent=4)


def do_get(url):
    """
    Do a GET request to `url`.
    """

    response = requests.get(url)
    if response.status_code == 200:
        return response.text


def scrap_cities(response):
    """
    Scrap the content on the website.
    """

    soup = BeautifulSoup(response, 'html.parser')

    cities = []

    for a in soup.find('div', {'id': 'dnav'}).find_all('a'):
        city = {'title': a.get_text(), 'link': a['href']}
        cities.append(city)

    save_json(cities, 'data/cities.json')

    return cities


def scrap_content(response, city_title):
    """
    Scrap the content on the website.
    """

    soup = BeautifulSoup(response, 'html.parser')

    categories = []

    for a in soup.find('div', {'id': 'catnav'}).find_all('a'):
        category = {'title': a.get_text(), 'link': a['href']}
        categories.append(category)

    for category in categories:
        category_title = category.get('title').lower().replace(' ', '-')
        url = category.get('link')

        response = do_get(url)

        soup = BeautifulSoup(response, 'html.parser')

        entities = []
        for div in soup.findAll('div', {'class': 'post'}):
            entity = {}

            entity_name = div.find('h3').get_text()
            entity['name'] = entity_name

            information = div.find('div').get_text().split('\n')
            information = [info for info in information if info != '']

            for info in information:
                pattern = r'mobile-|address-|telephone number-|fax-'
                found = re.match(pattern, info, re.IGNORECASE)
                if found:
                    key = found.group().replace('-', '').lower()
                    value = info.replace(found.group(), '')
                    entity[key] = value

            entities.append(entity)

        save_json(entities, f'data/{city_title}/{category_title}.json')


def main():
    """
    Main module for the Scrapper.
    """

    os.mkdir('data')

    response = do_get('https://www.totalpunjab.com/')

    cities = scrap_cities(response)

    for city in cities:
        city_title = city.get('title').lower().replace(' ', '-')
        url = city.get('link')

        os.makedirs(f'data/{city_title}')
        response = do_get(url)
        scrap_content(response, city_title)


if __name__ == '__main__':
    main()
