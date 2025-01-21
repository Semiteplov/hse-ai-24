import os

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile

from api import get_food_data, get_city_temperature
from middleware import LoggingMessageMiddleware
from states import UserProfile
from utils import calculate_water_norm, calculate_calorie_norm, get_user_data, users, generate_progress_chart

user_router = Router()
user_router.message.middleware(LoggingMessageMiddleware())

WORKOUTS = {
    "ходьба": 4,
    "бег": 10,
    "плавание": 9,
    "велосипед": 8,
    "йога": 3
}


@user_router.message(Command('set_profile'))
async def set_profile_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    get_user_data(user_id)
    await state.set_state(UserProfile.weight)
    await message.answer('Привет! Давайте настроим ваш профиль. Сколько вы весите (в кг)?',
                         reply_markup=ReplyKeyboardRemove())


@user_router.message(UserProfile.weight)
async def process_weight(message: Message, state: FSMContext):
    try:
        weight = int(message.text)
        user_id = message.from_user.id
        users[user_id]['weight'] = weight
        await state.set_state(UserProfile.height)
        await message.answer('Введите ваш рост (в см):')
    except ValueError:
        await message.answer('Пожалуйста, введите вес в числовом формате.')


@user_router.message(UserProfile.height)
async def process_height(message: Message, state: FSMContext):
    try:
        height = int(message.text)
        user_id = message.from_user.id
        users[user_id]['height'] = height
        await state.set_state(UserProfile.age)
        await message.answer('Введите ваш возраст:')
    except ValueError:
        await message.answer('Пожалуйста, введите рост в числовом формате.')


@user_router.message(UserProfile.age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        user_id = message.from_user.id
        users[user_id]['age'] = age
        await state.set_state(UserProfile.activity)
        await message.answer('Сколько минут активности у вас в день?')
    except ValueError:
        await message.answer('Пожалуйста, введите возраст в числовом формате.')


@user_router.message(UserProfile.activity)
async def process_activity(message: Message, state: FSMContext):
    try:
        activity = int(message.text)
        user_id = message.from_user.id
        users[user_id]['activity'] = activity
        await state.set_state(UserProfile.city)
        await message.answer('В каком городе вы находитесь?')
    except ValueError:
        await message.answer('Пожалуйста, введите количество активности в числовом формате.')


@user_router.message(UserProfile.city)
async def process_city(message: Message, state: FSMContext):
    city = message.text
    user_id = message.from_user.id

    try:
        temperature = get_city_temperature(city, os.getenv('OPEN_WEATHER_TOKEN'))
        users[user_id]['city'] = city
        users[user_id]['water_goal'] = calculate_water_norm(
            users[user_id]['weight'], users[user_id]['activity'], temperature
        )
        users[user_id]['calorie_goal'] = calculate_calorie_norm(
            users[user_id]['weight'], users[user_id]['height'], users[user_id]['age']
        )

        await message.answer(
            f'Ваш профиль настроен! Ваша дневная норма воды: {users[user_id]['water_goal']} мл.\n'
            f'Дневная норма калорий: {users[user_id]['calorie_goal']} ккал.\n'
            f'Теперь вы можете логировать воду с помощью команды /log_water, тренировки с помощью /log_workout, '
            f'и еду — с помощью /log_food.'
        )
        await state.clear()
    except Exception as e:
        await message.answer(f'Не удалось получить данные о погоде. Ошибка: {str(e)}')


@user_router.message(Command('log_water'))
async def log_water_command(message: Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)  # Получаем данные пользователя

    if not user_data["water_goal"]:
        await message.answer('Сначала настройте профиль с помощью команды /set_profile.')
        return

    try:
        args = message.text.split()
        if len(args) < 2:
            await message.answer('Пожалуйста, укажите количество воды в миллилитрах. Пример: /log_water 250')
            return

        water = int(args[1])
        user_data["logged_water"] += water
        remaining = max(0, user_data["water_goal"] - user_data["logged_water"])

        await message.answer(
            f'Вы выпили: {user_data["logged_water"]} мл воды.\n'
            f'Осталось: {remaining} мл до выполнения нормы.'
        )
    except ValueError:
        await message.answer('Пожалуйста, введите количество воды в числовом формате. Пример: /log_water 250')


@user_router.message(Command('log_food'))
async def log_food_command(message: Message, state: FSMContext):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer('Пожалуйста, укажите название продукта. Пример: /log_food банан')
        return

    product_name = args[1]

    try:
        food_data = get_food_data(product_name)
    except Exception as e:
        await message.answer(f'Не удалось получить данные о {product_name}. Ошибка: {str(e)}')
        return

    if not food_data or not food_data.get('calories_per_100g'):
        await message.answer(f'Не удалось найти информацию о продукте \'{product_name}\'. Попробуйте другой запрос.')
        return

    await state.update_data(current_food={
        'product_name': food_data['product_name'],
        'calories_per_100g': food_data['calories_per_100g']
    })
    await state.set_state(UserProfile.target)

    await message.answer(
        f'🍎 {food_data["product_name"]} содержит {food_data["calories_per_100g"]} ккал на 100 г. '
        f'Сколько грамм вы съели?'
    )


@user_router.message(UserProfile.target)
async def process_food_grams(message: Message, state: FSMContext):
    try:
        grams = float(message.text)
        user_id = message.from_user.id
        user_data = get_user_data(user_id)

        data = await state.get_data()
        current_food = data.get('current_food')

        if not current_food:
            await message.answer('Произошла ошибка. Попробуйте снова с помощью команды /log_food.')
            return

        calories_per_100g = current_food['calories_per_100g']
        product_name = current_food['product_name']
        total_calories = (calories_per_100g / 100) * grams

        user_data["logged_calories"] += total_calories

        await state.clear()
        await message.answer(
            f'Записано: {total_calories:.1f} ккал ({grams} г {product_name}).\n'
            f'Суммарно потреблено калорий: {user_data["logged_calories"]:.1f} ккал.'
        )
    except ValueError:
        await message.answer('Пожалуйста, введите количество граммов в числовом формате.')


@user_router.message(Command("log_workout"))
async def log_workout_command(message: Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)

    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer('Пожалуйста, укажите тип тренировки и время в минутах. Пример: /log_workout бег 30')
        return

    workout_type = args[1].lower()
    try:
        duration = int(args[2])
    except ValueError:
        await message.answer('Пожалуйста, укажите время тренировки в числовом формате. Пример: /log_workout бег 30')
        return

    if workout_type not in WORKOUTS:
        await message.answer(f'Неизвестный тип тренировки: {workout_type}. Доступные: {", ".join(WORKOUTS.keys())}')
        return

    calories_burned = WORKOUTS[workout_type] * duration
    additional_water = (duration // 30) * 200

    user_data["burned_calories"] += calories_burned
    user_data["logged_water"] += additional_water

    await message.answer(
        f'🏋️‍♂️ {workout_type.capitalize()} {duration} минут — {calories_burned} ккал.\n'
        f'Дополнительно: выпейте {additional_water} мл воды.\n'
        f'Суммарно сожжено калорий: {user_data["burned_calories"]} ккал.'
    )


@user_router.message(Command('check_progress'))
async def check_progress_command(message: Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)

    if not user_data["water_goal"] or not user_data["calorie_goal"]:
        await message.answer('Сначала настройте профиль с помощью команды /set_profile.')
        return

    remaining_water = max(0, user_data["water_goal"] - user_data["logged_water"])
    calorie_balance = max(0, user_data["calorie_goal"] - (user_data["logged_calories"] - user_data["burned_calories"]))

    progress_message = (
        f'📊 Прогресс:\n\n'
        f'💧 Вода:\n'
        f'- Выпито: {user_data["logged_water"]} мл из {user_data["water_goal"]} мл.\n'
        f'- Осталось: {remaining_water} мл.\n\n'
        f'🔥 Калории:\n'
        f'- Потреблено: {user_data["logged_calories"]:.1f} ккал из {user_data["calorie_goal"]:.1f} ккал.\n'
        f'- Сожжено: {user_data["burned_calories"]:.1f} ккал.\n'
        f'- Баланс: {calorie_balance:.1f} ккал.'
    )

    await message.answer(progress_message)


@user_router.message(Command('progress_chart'))
async def send_progress_chart(message: Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)

    if not user_data['water_goal'] or not user_data['calorie_goal']:
        await message.answer('Сначала настройте профиль с помощью команды /set_profile.')
        return

    file_path = await generate_progress_chart(user_data)
    await message.answer_photo(FSInputFile(file_path), caption='Ваш прогресс по воде и калориям 📊')


low_calorie_foods = [
    {"name": "Огурец", "calories": 15},
    {"name": "Капуста", "calories": 25},
    {"name": "Сельдерей", "calories": 16},
    {"name": "Шпинат", "calories": 23},
    {"name": "Редис", "calories": 20},
]


@user_router.message(Command('recommendations'))
async def send_recommendations(message: Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)

    if not user_data['calorie_goal']:
        await message.answer('Сначала настройте профиль с помощью команды /set_profile.')
        return

    # Рекомендации по продуктам
    food_recommendations = '\n'.join([f"{food['name']} — {food['calories']} ккал/100г" for food in low_calorie_foods])

    # Рекомендации по тренировкам
    calorie_deficit = max(0, user_data['calorie_goal'] - (user_data['logged_calories'] - user_data['burned_calories']))
    recommended_workouts = []
    for workout, calories_per_minute in WORKOUTS.items():
        duration = int(calorie_deficit / calories_per_minute)
        if duration > 0:
            recommended_workouts.append(f"{workout.capitalize()} — {duration} мин")

    workout_recommendations = "\n".join(recommended_workouts)

    response = (
        f'🔹 Рекомендации по продуктам:\n{food_recommendations}\n\n'
        f'🔹 Рекомендации по тренировкам:\n{workout_recommendations if recommended_workouts else 'Вы достигли своей цели!'}'
    )

    await message.answer(response)
