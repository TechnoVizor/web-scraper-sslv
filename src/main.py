import requests
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime


today = datetime.now().strftime("%Y-%m-%d")
filename = f'riga_flats_{today}.csv'

url = 'https://www.ss.lv/ru/real-estate/flats/riga/all/sell/'
domain = 'https://www.ss.lv'
seen_ad_ids = set()
headers_ua = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def clean_price(text):
    return ''.join(filter(str.isdigit, text))

csv_headers = ['ID', 'Район', 'Улица', 'Комнаты', 'Площадь', 'Этаж', 'Серия', 'Цена за м2', 'Цена' , 'Ссылка']

with open(filename, 'w', newline='' , encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    writer.writerow(csv_headers)

    page_number = 1

    while True:
        print(f"\nПарсим страницу № {page_number} ")
        try:
            response = requests.get(url, headers=headers_ua , timeout=10)
            print(f"Ответ от URL:    {response.url}")
            print(f"Код ответа:      {response.status_code}")
            soup = BeautifulSoup(response.text, 'lxml')
            rows = soup.find_all('tr', id=lambda x: x and x.startswith('tr_'))
            if not rows:
                print("На этой странице нет объявлений. Парсинг завершен.")
                break

            new_ads_on_page = 0
            
            for row in rows:
                add_id = row.get('id')
                if add_id in seen_ad_ids:
                    continue
                
                cells = row.find_all('td')

                if len(cells) < 9:
                    continue

                link_tag = cells[1].find('a')
                if link_tag:
                    href = link_tag.get('href')
                    full_link = f"https://www.ss.lv{href}"
                else:
                    full_link = "-"

                loc_parts = cells[3].get_text(separator="|", strip=True).split("|")
                district = loc_parts[0] if len(loc_parts) > 0 else "-"
                street = loc_parts[1] if len(loc_parts) > 1 else "-"

                rooms = cells[4].get_text(strip=True)
                area = cells[5].get_text(strip=True)
                floor = cells[6].get_text(strip=True)
                series = cells[7].get_text(strip=True)

                if len(cells) >= 10:
                    price_m2 = cells[8].get_text(strip=True)
                    total_price = cells[9].get_text(strip=True)
                else:
                    total_price = cells[8].get_text(strip=True)
                    try:
                        p_val = float(clean_price(total_price))
                        a_val = float(area.replace(',', '.'))
                        price_m2 = f"{int(p_val / a_val)} €"
                    except:
                        price_m2 = "-"

                writer.writerow([add_id, district, street, rooms, area, floor, series, price_m2, total_price , full_link])
                seen_ad_ids.add(add_id)
                new_ads_on_page += 1

                print(f"На странице {page_number} собрано новых: {new_ads_on_page} шт.")

            if new_ads_on_page == 0:
                print("Новые объявления закончились. Остановка.")
                break

            next_page_link = soup.find('a', rel='next')
            if next_page_link:
                href = next_page_link.get('href')
                url = domain + next_page_link.get('href')
                page_number += 1
                time.sleep(0.5)
            else:
                print("Кнопка 'Далее' не найдена. Это последняя страница.")
                break
        except Exception as e:
            print(f"Ошибка: {e}")
            break

print(f"\nГотово! Данные в файле: {filename}")


