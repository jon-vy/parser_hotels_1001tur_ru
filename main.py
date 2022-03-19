import datetime

import requests
from bs4 import BeautifulSoup
import json
import time
import asyncio
import aiohttp
from fake_useragent import UserAgent
ua = UserAgent()
hotel_list = []

# <editor-fold desc="Получаю количество страниц">
def get_pagin():
    r = requests.get("https://hotels.1001tur.ru/russia/").text
    soup = BeautifulSoup(r, "lxml")
    paginator = soup.findAll("a", class_="cmn-paginator__page-link")
    pag = paginator[-1].text
    # print(paginator[-1])
    return paginator[-1].text
# </editor-fold>

# <editor-fold desc="Парс данных">
async def get_data(session, page):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9image/avif,image/webp,*/*;q=0.8",
        "User-Agent": ua.random
    }
    params = {"page": page}
    url = "https://hotels.1001tur.ru/russia/"
    r = await session.get(url=url, headers=headers, params=params)
    # print(r)
    if r.status == 200:
        soup = BeautifulSoup(await r.text(), "lxml")
        hotel_block = soup.find("map-hotel-block").attrs[':hotellist']
        try:
            data_hotel = json.loads(hotel_block)['data']
        except json.decoder.JSONDecodeError:
            print(f"----------------\nОшибка в коде сайта\n{url}?page={page}\n--------------------")
            return
        for i in range(len(data_hotel)):
            try:
                hotel_name = data_hotel[i]['hotel_name']
            except:
                hotel_name = 'Без названия'
            try:
                city_name = data_hotel[i]['city_name']
            except:
                city_name = 'Город не известен'
            try:
                price = data_hotel[i]['price']
            except:
                price = 'Безценно'
            hotel_url = "https:" + data_hotel[i]['hotel_url']
            try:
                hotel_photo = data_hotel[i]['hotel_photo']
            except:
                hotel_photo = 'Нет фото'
            # print(hotel_name +' '+ city_name +' '+ price +' '+ hotel_url +' '+ hotel_photo)
            hotel_list.append(
                {
                    "Название гостиницы": hotel_name,
                    "Город": city_name,
                    "Цена": price,
                    "Фото": hotel_photo,
                    "Сайт": hotel_url
                }
            )
        print(f"Обработал {url}?page={page}")

    else:
        print(f"----------------\nОшибка. Ответ сайта {r.status}\n{url}?page={page}\n--------------------")
        return
# </editor-fold>

# <editor-fold desc="собрать задачи">
async def gather_data():
    page_count = int(get_pagin())  # Получить список страниц
    async with aiohttp.ClientSession() as session:  # Создаю сессию. Позволяет повторно использовать уже открытое соеденение
        tasks = []  # список задач

        for page in range(1, page_count + 1):
        # for page in range(1, 3):
            task = asyncio.create_task(get_data(session, page))  # Создал задачу
            tasks.append(task)  # Добавил её в список

        await asyncio.gather(*tasks)  # вернуть готовый список задач
# </editor-fold>



def main():
    # asyncio.run(gather_data())
    asyncio.get_event_loop().run_until_complete(gather_data())
    # asyncio.get_event_loop().run_until_complete(tasks())

    cur_time = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M")

    with open(f"hotels_{cur_time}.json", "w") as f:
        json.dump(hotel_list, f)

# Время работы: 39.53283214569092
if __name__ == '__main__':
    time_start = time.time()
    main()

    time_end = time.time()
    print(f"Время работы: {time_end - time_start}")


