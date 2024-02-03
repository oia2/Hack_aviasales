from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/api/flights')
def api_flights():
    conn = sqlite3.connect('AirTickets.db')
    cursor = conn.cursor()

    departure_city = request.args.get('departure_city')
    destination_city = request.args.get('destination_city')
    departure_date_str = request.args.get('departure_date')
    return_date_str = request.args.get('return_date')

    departure_date = datetime.strptime(departure_date_str, '%Y-%m-%d').strftime('%d.%m.%Y')
    return_date = datetime.strptime(return_date_str, '%Y-%m-%d').strftime('%d.%m.%Y')

    cursor.execute("""
           SELECT * FROM Flights WHERE Departure_city=? AND Destination_city=? AND Date_departure=? AND Date_destination=?
       """, (departure_city, destination_city, departure_date, return_date))
    flights = cursor.fetchall()

    if not flights:
        cursor.execute("""
               SELECT * FROM Flights WHERE Departure_city=? AND Destination_city=? AND Date_departure=?
           """, (departure_city, destination_city, departure_date))
        flights = cursor.fetchall()
        if flights:
            response_data = {'flights': flights, 'alternative_results': 1}
        else:
            three_days_before = (datetime.strptime(departure_date, '%d.%m.%Y') - timedelta(days=3)).strftime('%Y-%m-%d')
            three_days_after = (datetime.strptime(departure_date, '%d.%m.%Y') + timedelta(days=3)).strftime('%Y-%m-%d')
            three_days_after_str = datetime.strptime( three_days_after, '%Y-%m-%d').strftime('%d.%m.%Y')
            three_days_before_str = datetime.strptime( three_days_before, '%Y-%m-%d').strftime('%d.%m.%Y')
            print(three_days_before_str)
            print(three_days_after_str)
            print(departure_date)
            cursor.execute("""
                SELECT * FROM Flights 
                WHERE Departure_city=? 
                AND Destination_city=? 
                AND Date_departure BETWEEN ? AND ?
            """, (departure_city, destination_city, three_days_before_str, three_days_after_str))
            flights = cursor.fetchall()
            response_data = {'flights': flights, 'alternative_results': 2}
    else:
        response_data = {'flights': flights, 'alternative_results': 0}

    print(response_data)
    conn.close()
    return jsonify(response_data)

@app.route('/api/price_forecast')
def api_price_forecast():
    departure_city = request.args.get('departure_city')
    destination_city = request.args.get('destination_city')

    conn = sqlite3.connect('AirTickets.db')
    cursor = conn.cursor()

    cursor.execute("""
           SELECT Date_departure, Price FROM Flights 
           WHERE Departure_city=? AND Destination_city=?
       """, (departure_city, destination_city))
    print('Запрос отправлен')
    price_data = cursor.fetchall()
    print(price_data)
    conn.close()
    return jsonify(price_data)

if __name__ == '__main__':
    app.run(debug=True)