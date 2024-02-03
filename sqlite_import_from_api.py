import pandas as pd
import sqlite3

def import_from_api():
    conn = sqlite3.connect('AirTickets.db')
    cursor = conn.cursor()

    flights_df = pd.read_csv('flights.csv')
    cities_df = pd.read_csv('cities.csv')

    for index, row in flights_df.iterrows():
        cursor.execute("""
            SELECT * FROM Flights WHERE Departure_city=? AND Destination_city=? AND Date_departure=? AND Date_destination=?
        """, (row['Город вылета'], row['Город назначения'], row['Дата вылета'], row['Дата прилета']))
        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO Flights (Departure_city, Destination_city, Date_departure, Date_destination, Airline, Price, Data_Source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (row['Город вылета'], row['Город назначения'], row['Дата вылета'], row['Дата прилета'], row['Авиакомпания'], row['Цена (руб)'], row['Источник данных']))

    for index, row in cities_df.iterrows():
        cursor.execute("""
            SELECT * FROM Cities WHERE City_name=? AND Country=? AND Airport_Code=?
        """, (row['Город'], row['Страна'], row['Код аэропорта']))
        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO Cities (City_name, Country, Airport_Code)
                VALUES (?, ?, ?)
            """, (row['Город'], row['Страна'], row['Код аэропорта']))

    conn.commit()
    conn.close()

def clear_data():
    conn = sqlite3.connect('AirTickets.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Flights")
    cursor.execute("DELETE FROM Cities")

    conn.commit()
    conn.close()

def show():
    conn = sqlite3.connect('AirTickets.db')
    cursor = conn.cursor()

    print("Таблица Flights:")
    cursor.execute("SELECT * FROM Flights")
    flights = cursor.fetchall()
    for flight in flights:
        print(flight)

    print("\nТаблица Cities:")
    cursor.execute("SELECT * FROM Cities")
    cities = cursor.fetchall()
    for city in cities:
        print(city)

    conn.close()
