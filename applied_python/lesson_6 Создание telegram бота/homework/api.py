import requests


def get_food_data(product_name):
    """
    Получение данных о продукте из OpenFoodFacts.

    :param product_name: Название продукта
    :return: Словарь с информацией о калориях и продукте или None
    """
    url = f'https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product_name}&json=true'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        if products:
            first_product = products[0]
            return {
                'product_name': first_product.get('product_name', 'Неизвестно'),
                'calories_per_100g': first_product.get('nutriments', {}).get('energy-kcal_100g', 0)
            }
        return None
    print(f'Ошибка: {response.status_code}')
    return None


def get_city_temperature(city: str, api_key: str) -> float:
    """
    Получает текущую температуру для указанного города через OpenWeatherMap API.

    :param city: Название города
    :param api_key: Ключ API для OpenWeatherMap
    :return: Температура в градусах Цельсия
    :raises Exception: Если запрос не удался или данные недоступны
    """
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}'
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    if 'main' not in data or 'temp' not in data['main']:
        raise Exception('Невозможно получить температуру из ответа API.')

    return data['main']['temp']
