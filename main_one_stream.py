import requests
from bs4 import BeautifulSoup
import fake_useragent
import json
import time
import asyncio
import aiohttp

ua = fake_useragent.UserAgent()

def get_pagin():
    r = requests.get("https://hotels.1001tur.ru/russia/").text
    soup = BeautifulSoup(r, "lxml")
    paginator = soup.findAll("a", class_="cmn-paginator__page-link")
    pag = paginator[-1].text
    # print(paginator[-1])
    return paginator[-1].text


hotel_list = []
def get_data(s, pag):
    url = "https://hotels.1001tur.ru/russia/"
    params = {"page": pag}
    r = s.get(url=url, params=params)
    if r.status_code == 200:
        # with open("index.html", "w", encoding="utf-8") as file:
        #     file.write(r.text)
        soup = BeautifulSoup(r.text, "lxml")
        hotel_block = soup.find("map-hotel-block").attrs[':hotellist']

        try:
            data_hotel = json.loads(hotel_block)['data']
        except json.decoder.JSONDecodeError:
            print(f"----------------\nОшибка в коде сайта\n{url}?page={j}\n--------------------")
            return

        for i in range(len(data_hotel)):
            hotel_name = data_hotel[i]['hotel_name']
            city_name = data_hotel[i]['city_name']
            price = data_hotel[i]['price']
            hotel_url = "https:" + data_hotel[i]['hotel_url']
            hotel_photo = data_hotel[i]['hotel_photo']
            print(hotel_name +' '+ city_name +' '+ price +' '+ hotel_url +' '+ hotel_photo)
            hotel_list.append(
                {
                    "Название гостиницы": hotel_name,
                    "Город": city_name,
                    "Цена": price,
                    "Фото": hotel_photo,
                    "Сайт": hotel_url
                }
            )

    # print(hotel_list)
    # with open("data_file.json", "w") as write_file:
    #     json.dump(hotel_list, write_file)


# В один поток Время работы: 355.74669075012207
if __name__ == '__main__':
    time_start = time.time()
    s = requests.session()
    pag = int(get_pagin())
    # print(type(pag))

    for j in range(1, pag):
        get_data(s, j)
        print(f'-------------------------{j}------------------------------------------------')

    with open("data_file.json", "w") as write_file:
        json.dump(hotel_list, write_file)

    time_end = time.time()
    print(f"Время работы: {time_end - time_start}")


