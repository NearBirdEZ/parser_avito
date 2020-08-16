import requests
from bs4 import BeautifulSoup as bs
import csv

search = input("Что ищем на авито?\n")
search = "+". join(search.split())
URL = "https://www.avito.ru/moskva"
FILE = "finish_parse.csv"
HEADERS = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.206 (Edition Yx GX)",
           "accept": "*/*"}


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_undeground(item):
    undeground = item.find("span", class_="item-address-georeferences-item__content")
    if undeground:
        return undeground.get_text().strip()
    return "Метро не указано"


def get_pictures(item):
    pictures = item.find("img")
    if pictures:
        return pictures.get("srcset").split()[0]
    return "Фото отсутствует"


def get_pages(html):
    sp = bs(html, "html.parser")
    pagination = sp.find_all("span", class_="pagination-item-1WyVp")
    if pagination:
        pagination = str(pagination[-2:-1])
        return int(pagination.split(">")[1].split("<")[0])
    else:
        return 1


def get_contend(html):
    sp = bs(html, "html.parser")
    items = sp.find_all("div", class_="item__line")
    lst = []
    for item in items:
        lst.append({
            "title": item.find("div", class_="snippet-title-row").get_text().strip(),
            "price": item.find("div", class_="snippet-price-row").get_text().strip()[:-1],
            "undeground": get_undeground(item),
            "pictures": get_pictures(item),
            "link": "www.avito.ru"+item.find("a", class_="snippet-link").get("href"),
        })
    return lst


def save_file(items, path):
    with open(path, "w", newline="", encoding="cp1251") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Название", "Цена", "Метро", "Фотография", "Ссылка на товар"])
        for item in items:
            writer.writerow([item["title"],
                             item["price"],
                             item["undeground"],
                             item["pictures"],
                             item["link"]
                             ])


def parse():
    html = get_html(URL, params={"q": search, "p": 1})
    if html.ok:
        pages = get_pages(html.text)
        lst = []
        for page in range(1, pages+1):
            print(f"Парсим {page} из {pages}")
            html = get_html(URL, params={"q": search, "p": page})
            lst.extend(get_contend(html.text))
        save_file(lst, FILE)
        print(f'Получено {len(lst)} товар(ов)')
    else:
        print("Error")


parse()
