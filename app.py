
import pandas as pd
import streamlit as st
from client import async_weather_data
from data_processing import (filtered_data, get_avg_stand_dev_month, 
                             get_avg_stand_dev_season, normal_weather_temperature)
from datetime import datetime
import asyncio
import matplotlib.pyplot as plt

CITIES = ['New York', 'London', 'Paris', 'Tokyo', 'Moscow', 'Sydney',
          'Berlin', 'Beijing', 'Rio de Janeiro', 'Dubai', 'Los Angeles',
          'Singapore', 'Mumbai', 'Cairo', 'Mexico City']

async def main():
    st.title("Приложение: Погода во всем мире!")
    st.write("Разработали приложение для анализа данных о погоде openweathermap.org.")

    st.header("Шаг 1: Загрузите данные о погоде в формате csv")

    uploaded_file = st.file_uploader("Выберите CSV-файл", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df = filtered_data(df)
        st.write("Файл загружен, УРА!")
        st.header("Шаг 2: Выбер города")
        selected_city = st.selectbox("Выберите город для анализа температуры:", CITIES)
        api_key = st.text_input("Введите ваш API-ключ с OpenWeatherMap API и нажмите Enter:", type="password")
        if api_key:
            st.header(f"Шаг 3: Статистика температуры в городе {selected_city}")
            with st.form(key='weather_form'):
                submitted = st.form_submit_button("Получить данные о погоде")

                if submitted:
                    stat_weather_data = await async_weather_data([selected_city], api_key)
                    if isinstance(stat_weather_data, str):
                        st.error(stat_weather_data)
                    else:
                        mean_temperature_season, std_temperature_season = get_avg_stand_dev_season(df, selected_city)
                        mean_temperature_month, std_temperature_month = get_avg_stand_dev_month(df, selected_city) 
                        is_normal = normal_weather_temperature(mean_temperature_month, std_temperature_month, stat_weather_data[selected_city])
                        
                        if stat_weather_data:
                            st.write(f"### На текущий момент погода в городе **{selected_city}**:")
                            st.write(f"- Температура: **{stat_weather_data[selected_city]:.1f}°C**")

                            st.write("### Средние температуры для данного города в месяц и в сезон:")
                            st.write(f"- Средняя температура в городе за месяц: **{mean_temperature_month:.1f}°C**")
                            st.write(f"- Средняя температура в городе за сезон: **{mean_temperature_season:.1f}°C**")
                            
                            if is_normal:
                                st.write("### Температура является нормальной для данного месяца.")
                            else:
                                st.write("### Температруа не является нормальной для данного месяца.")
                            plot_with_outliers(df, selected_city)
                            st.pyplot(plt)
        else:
            st.write("Пожалуйста, введите ваш API-ключ с сайта openweathermap.org.")

    else:
        st.write("Пожалуйста, загрузите CSV-файл с данными о температуре в городах.")

def plot_with_outliers(df, city):
    filtered_df = df.query(f'city == "{city}"')

    plt.figure(figsize=(10, 5))
    plt.plot(filtered_df['timestamp'], filtered_df['temperature'], label='Температура', color='green')

    outliers = filtered_df[filtered_df['is_outlier_2s']]
    plt.scatter(outliers['timestamp'], outliers['temperature'], color='red', label='Аномалии')

    plt.title(f'Температура в городе {city}')
    plt.xlabel('Дата')
    plt.ylabel('Температура')
    plt.legend()
    plt.grid()

if __name__ == "__main__":
    asyncio.run(main())