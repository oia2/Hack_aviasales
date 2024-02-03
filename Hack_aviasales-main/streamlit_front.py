import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import mplcursors
from scipy import interpolate
import plotly.express as px
def get_departure_cities():
    conn = sqlite3.connect('AirTickets.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT Departure_city FROM Flights")
    cities = cursor.fetchall()
    conn.close()
    return [city[0] for city in cities]
def get_destination_cities():
    conn = sqlite3.connect('AirTickets.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT Destination_city FROM Flights")
    cities = cursor.fetchall()
    conn.close()
    return [city[0] for city in cities]

departure_cities = get_departure_cities()
destination_cities = get_destination_cities()

# Функция для получения рейсов
def fetch_flights(departure_city, destination_city, departure_date, return_date):
    departure_date_str = departure_date.strftime('%Y-%m-%d')
    return_date_str = return_date.strftime('%Y-%m-%d')
    response = requests.get(f'http://localhost:5000/api/flights?departure_city={departure_city}&destination_city={destination_city}&departure_date={departure_date_str}&return_date={return_date_str}')
    return response

# Функция для отображения рейсов и кнопок прогнозирования
def show_flights(flights_data, response_data):
    if response_data.get('alternative_results') == 1:
        st.info("К сожалению, на выбранные даты нет доступных рейсов. Вот все доступные авиарейсы с датой вылета, указанной вами:")
    elif response_data.get('alternative_results') == 2:
        st.warning("К сожалению, доступных билетов на вашу дату вылета не найдено. Здесь представлен список билетов, которые, возможно, вам подойдут:")
    elif response_data.get('alternative_results') == 0:
        st.success("Найдены следующие рейсы:")

    for flight in flights_data:
        flight_info = f"{flight[1]} -> {flight[2]}, {flight[3]} - {flight[4]},Авиакомпания: {flight[5]}, Цена: {flight[6]} руб."
        st.write(flight_info)
        if st.button("Прогноз цены на билет", key=f"button_{flight[0]}"):
            fetch_and_plot_price_forecast(flight[1], flight[2])

# Функция для запроса прогноза цен и построения графика
def fetch_and_plot_price_forecast(departure_city, destination_city):
    price_response = requests.get(f'http://localhost:5000/api/price_forecast?departure_city={departure_city}&destination_city={destination_city}')
    if price_response.status_code == 200:
        price_data = price_response.json()
        flight_info_list = [f"Из {departure_city} в {destination_city}" for _ in range(len(price_data))]

        plot_price_forecast_with_prediction(price_data, flight_info_list)
    else:
        st.error("Ошибка при получении данных о ценах")

# Функция построения графика цен
def plot_price_forecast_with_prediction(price_data, flight_data, inflation_rate=0.05):
    df = pd.DataFrame(price_data, columns=["Дата", "Цена"])
    df['Дата'] = pd.to_datetime(df['Дата'], format='%d.%m.%Y')
    df = df.sort_values(by='Дата')

    df['Инфо'] = flight_data

    last_date = df['Дата'].iloc[-1]
    prediction_dates = pd.date_range(start=last_date, periods=180, freq='D')
    linear_interp = interpolate.interp1d(df['Дата'].map(datetime.toordinal), df['Цена'], fill_value='extrapolate')
    predicted_prices = linear_interp([date.toordinal() for date in prediction_dates])
    df_prediction = pd.DataFrame({'Дата': prediction_dates, 'Цена': predicted_prices})

    df_prediction['Цена'] = df_prediction['Цена'] * (1 + inflation_rate)
    fig = px.line(df, x='Дата', y='Цена', title='Изменение цен на билеты', labels={'Цена': 'Цена (руб)'}, markers=True, hover_data=["Инфо"])
    fig.add_scatter(x=df_prediction['Дата'], y=df_prediction['Цена'], mode='lines+markers', name='Прогноз с учетом инфляции', hoverinfo='name+y+x')

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color="white"
    )
    st.plotly_chart(fig, use_container_width=True)
def main():
    st.markdown("""
        <style>
        .header {
            font-size: 24px;
            font-weight: bold;
            color: #ffffff;
            padding: 10px;
            text-align: center;
        }
        .subheader {
            color: #ffffff;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown('<div class="header">Название Компании или Проекта</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Добро пожаловать в наш сервис прогнозирования стоимости авиабилетов</div>', unsafe_allow_html=True)

    with st.form("input_form"):
        departure_city = st.selectbox("Город вылета",  departure_cities)
        destination_city = st.selectbox("Город назначения", destination_cities)
        departure_date = st.date_input("Дата вылета", datetime.today())
        return_date = st.date_input("Дата прилета", datetime.today())
        submit_button = st.form_submit_button("Найти рейсы")

    if submit_button:
        response = fetch_flights(departure_city, destination_city, departure_date, return_date)
        if response.status_code == 200:
            response_data = response.json()
            st.session_state['flights_data'] = response_data['flights']
            st.session_state['response_data'] = response_data
        else:
            st.error("Ошибка при получении данных")

    if 'flights_data' in st.session_state:
        show_flights(st.session_state['flights_data'], st.session_state['response_data'])

if __name__ == "__main__":
    main()