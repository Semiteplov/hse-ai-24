import httpx
import requests
import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt

from analyzer import *


@st.cache_data
def read_data(file):
    return pd.read_csv(file)


def get_current_temperature(api_key, city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(url)
    if response.status_code == 401:
        return {"error": response.json().get('message', 'Invalid API key.')}
    elif response.status_code == 200:
        data = response.json()
        return {'temperature': data['main']['temp']}
    else:
        return {'error': f'Unexpected error: {response.status_code}'}


def plot_time_series(data, city):
    st.subheader(f'Временной ряд температуры для {city}')
    city_data = data[data['city'] == city]
    plt.figure(figsize=(9, 6))
    plt.plot(city_data['date'], city_data['temperature'], label='Температура')
    plt.plot(city_data['date'], city_data['rolling_mean'], label='Скользящее среднее (30 дней)')
    anomalies = city_data[city_data['is_anomaly']]
    plt.scatter(anomalies['date'], anomalies['temperature'], color='red', label='Аномалии')
    plt.xlabel('Дата')
    plt.ylabel('Температура (°C)')
    plt.legend()
    st.pyplot(plt)


def plot_seasonal_profiles(data, city):
    st.subheader(f'Сезонные профили для {city}')
    city_data = data[data['city'] == city]
    city_data['month'] = pd.to_datetime(city_data['date']).dt.month
    seasonal_stats = city_data.groupby('season')['temperature'].agg(['mean', 'std']).reset_index()
    plt.figure(figsize=(9, 6))
    plt.bar(seasonal_stats['season'], seasonal_stats['mean'], yerr=seasonal_stats['std'], capsize=5)
    plt.xlabel('Сезон')
    plt.ylabel('Средняя температура (°C)')
    plt.title('Средняя температура и отклонения по сезонам')
    st.pyplot(plt)


def main():
    st.title('Анализ температурных данных и мониторинг текущей температуры через OpenWeatherMap API')

    uploaded_file = st.file_uploader('Загрузите файл с историческими данными', type='csv')
    if uploaded_file:
        try:
            data = read_data(uploaded_file)
            st.session_state.data = data
            st.dataframe(data.head())

            if 'city' in data.columns and 'temperature' in data.columns:
                if 'city' not in st.session_state:
                    st.session_state.city = data['city'].unique()[0]
                st.session_state.city = st.selectbox(
                    'Выберите город:',
                    data['city'].unique(),
                    index=list(data['city'].unique()).index(st.session_state.city)
                )

                use_parallel = st.checkbox('Использовать параллельный анализ')
                start_analysis = st.button('Начать анализ данных')

                if start_analysis:
                    with st.spinner('Анализ данных...'):
                        data['date'] = pd.to_datetime(data['timestamp'])
                        analyzed_data, elapsed_time = analyze_data_parallel(data) if use_parallel else analyze_data(
                            data)
                        st.session_state.analyzed_data = analyzed_data
                        st.session_state.elapsed_time = elapsed_time

                    st.success(f'Анализ завершен! Время: {elapsed_time:.2f}')

                if 'analyzed_data' in st.session_state:
                    plot_time_series(st.session_state.analyzed_data, st.session_state.city)
                    plot_seasonal_profiles(st.session_state.analyzed_data, st.session_state.city)

                st.session_state.api_key = st.text_input(
                    'Введите API ключ OpenWeatherMap', type='password'
                )

                if st.session_state.api_key:
                    if 'analyzed_data' in st.session_state:
                        temp_data = get_current_temperature(
                            st.session_state.api_key, st.session_state.city
                        )

                        if 'error' in temp_data:
                            st.error(temp_data['error'])
                        else:
                            current_temp = temp_data['temperature']
                            st.write(f'Текущая температура в {st.session_state.city}: {current_temp}°C')
                            season = st.session_state.analyzed_data.loc[
                                st.session_state.analyzed_data['city'] == st.session_state.city, 'season'
                            ].iloc[0]
                            seasonal_stats = st.session_state.analyzed_data[
                                st.session_state.analyzed_data['season'] == season
                                ]
                            mean_temp = seasonal_stats['mean'].iloc[0]
                            std_temp = seasonal_stats['std'].iloc[0]
                            lower_bound = mean_temp - 2 * std_temp
                            upper_bound = mean_temp + 2 * std_temp

                            if lower_bound <= current_temp <= upper_bound:
                                st.success('Текущая температура в пределах нормы.')
                            else:
                                st.error('Текущая температура выходит за пределы нормы!')
                    else:
                        st.error('Сначала выполните анализ данных, чтобы получить сезонную статистику.')
            else:
                st.error('Файл должен содержать колонки \'city\' и \'temperature\'.')
        except Exception as e:
            st.error(f'Ошибка обработки файла: {e}')
    else:
        st.write('Загрузите файл, чтобы начать работу.')


if __name__ == '__main__':
    # st.set_page_config(layout='wide')
    main()
