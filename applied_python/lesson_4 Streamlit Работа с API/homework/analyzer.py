import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd


def get_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Autumn"


def analyze_city(city_data):
    city_data['rolling_mean'] = city_data['temperature'].rolling(window=30).mean()
    city_data['season'] = city_data['date'].dt.month.apply(get_season)
    seasonal_stats = city_data.groupby('season')['temperature'].agg(['mean', 'std']).reset_index()
    city_data = city_data.merge(seasonal_stats, on='season')
    city_data['is_anomaly'] = (
            (city_data['temperature'] > city_data['mean'] + 2 * city_data['std']) |
            (city_data['temperature'] < city_data['mean'] - 2 * city_data['std'])
    )
    return city_data


def analyze_data(data):
    results = []
    start_time = time.time()

    for city in data['city'].unique():
        city_data = data[data['city'] == city].copy()
        results.append(analyze_city(city_data))
    return pd.concat(results), time.time() - start_time


def analyze_data_parallel(data):
    cities = data['city'].unique()
    city_datasets = [data[data['city'] == city].copy() for city in cities]
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(analyze_city, city_datasets))

    return pd.concat(results), time.time() - start_time
