import json
import pandas as pd
import requests
from datetime import datetime

client_id = "t6ugnkLyraN7O3UpDWXrMt8TpAugS5MA"
client_secret = "OMasp0kUFOhzFwGm"

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

def take_info_from_api(city_name):
    def get_access_token(client_id, client_secret):
        url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            return None

    def get_flight_destinations(access_token, origin):
        url = "https://test.api.amadeus.com/v1/shopping/flight-destinations"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"origin": origin}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching data: {response.status_code}")
            print(response.text)
            return None

    def save_to_json(data, filename):
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

    def convert_date_format(date_str):
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d.%m.%Y')

    access_token = get_access_token(client_id, client_secret)
    if access_token:
        destinations = get_flight_destinations(access_token, city_name)
        if destinations and 'data' in destinations:
            print(json.dumps(destinations, indent=4))
            save_to_json(destinations, 'destinations.json')
        else:
            print("Data not found in API response.")
    else:
        print("Не удалось получить токен доступа")

    currency_exchange_rate = {
        "Япония": 0.5,
        "США": 100,
        "Южная Корея": 50,
        "Китай": 12,
        "Сингапур": 70,
    }
    airport_to_city = {
        "NRT": "Токио",
        "HND": "Токио",
        "LAX": "Лос-Анджелес",
        "ICN": "Сеул",
        "PEK": "Пекин",
        "MNL": "Манила",
        "SHA": "Шанхай",
        "HKG": "Гонг Конг",
        "TPE": "Тайпей",
        "BKK": "Бангкок",
        "SIN": "Сингапур",
        "HAN": "Ханой",
        "DPS": "Нгурах-Рай",
        "CEB": "Мактан-Себу",
        "CDG": "Париж",
        "LGW": "Гатвик",
        "HNL": "Гонолулу",
        "PVG": "Шанхай Пудун",
        "KIX": "Кансай",
        "MEL": "Мельбурн",
        "HKT": "Пхукета",
        "MAA": "Ченнай",
        "KUL": "Куала-Лумпур",
        "PER": "Перт",
    }
    airport_to_country = {
        "NRT": "Япония",
        "HND": "Япония",
        "LAX": "США",
        "ICN": "Южная Корея",
        "PEK": "Китай",
        "MNL": "Филиппины",
        "SHA": "Китай",
        "HKG": "Китай",
        "TPE": "Тайвань",
        "BKK": "Таиланд",
        "SIN": "Сингапур",
        "HAN": "Вьетнам",
        "DPS": "Индонезия",
        "CEB": "Филиппины",
        "CDG": "Франция",
        "LGW": "Великобритания",
        "HNL": "США",
        "PVG": "Китай",
        "KIX": "Япония",
        "MEL": "Австралия",
        "HKT": "Тайланд",
        "MAA": "Индия",
        "KUL": "Малайзия",
        "PER": "Австралия",
    }

    def convert_currency_to_rub(amount, country):
        rate = currency_exchange_rate.get(country, 1)
        return amount * rate

    with open('destinations.json', 'r') as file:
        json_data = json.load(file)

    flight_data = []
    unique_cities = {}
    for item in json_data['data']:
        origin_city = airport_to_city.get(item['origin'], "Unknown")
        destination_city = airport_to_city.get(item['destination'], "Unknown")
        origin_country = airport_to_country.get(item['origin'], "Unknown")
        destination_country = airport_to_country.get(item['destination'], "Unknown")
        departure_date = convert_date_format(item['departureDate'])
        price_in_rub = convert_currency_to_rub(float(item['price']['total']), origin_country)
        return_date = convert_date_format(item['returnDate'])
        flight_data.append({
            'Город вылета': origin_city,
            'Город назначения': destination_city,
            'Дата вылета': departure_date,
            'Дата прилета': return_date,
            'Авиакомпания': 'Unknown',
            'Цена (руб)': price_in_rub,
            'Источник данных': 'Amadeus API'
        })

        if origin_city not in unique_cities:
            unique_cities[origin_city] = (item['origin'], origin_country)
        if destination_city not in unique_cities:
            unique_cities[destination_city] = (item['destination'], destination_country)

    cities_data = [{
        'Идентификатор города': code,
        'Город': city,
        'Страна': country,
        'Код аэропорта': code
    } for city, (code, country) in unique_cities.items()]

    cities_df = pd.DataFrame(cities_data)
    cities_df.to_csv('cities.csv', index=False)

    flights_df = pd.DataFrame(flight_data)
    flights_df.to_csv('flights.csv', index=False)

