from matplotlib import pyplot as plt


def calculate_water_norm(weight, activity_minutes, temperature):
    """
    Рассчитывает дневную норму воды.

    :param weight: Вес пользователя в кг
    :param activity_minutes: Минуты активности
    :param temperature: Температура окружающей среды
    :return: Норма воды в мл
    """
    base_water = weight * 30
    activity_water = (activity_minutes // 30) * 500
    temperature_water = 500 if temperature > 25 else 0
    return base_water + activity_water + temperature_water


def calculate_calorie_norm(weight, height, age):
    """
    Рассчитывает дневную норму калорий.

    :param weight: Вес пользователя в кг
    :param height: Рост пользователя в см
    :param age: Возраст пользователя
    :return: Норма калорий в ккал
    """
    return 10 * weight + 6.25 * height - 5 * age


users = {}


def get_user_data(user_id):
    if user_id not in users:
        users[user_id] = {
            "weight": None,
            "height": None,
            "age": None,
            "activity": None,
            "city": None,
            "water_goal": None,
            "calorie_goal": None,
            "logged_water": 0,
            "logged_calories": 0,
            "burned_calories": 0,
        }
    return users[user_id]


async def generate_progress_chart(user_data):
    """
    Генерирует график прогресса воды и калорий на основе данных пользователя.
    """
    water_goal = user_data["water_goal"]
    logged_water = user_data["logged_water"]
    remaining_water = max(0, water_goal - logged_water)

    calorie_goal = user_data["calorie_goal"]
    logged_calories = user_data["logged_calories"]
    burned_calories = user_data["burned_calories"]
    net_calories = logged_calories - burned_calories
    remaining_calories = max(0, calorie_goal - net_calories)

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    # Вода
    axes[0].bar(["Выпито", "Осталось"], [logged_water, remaining_water], color=["blue", "lightgray"])
    axes[0].set_title("Вода")
    axes[0].set_ylabel("Миллилитры")
    axes[0].set_ylim(0, water_goal)

    # Калории
    axes[1].bar(["Потреблено", "Осталось"], [net_calories, remaining_calories], color=["green", "lightgray"])
    axes[1].set_title("Калории")
    axes[1].set_ylabel("Калории")
    axes[1].set_ylim(0, calorie_goal)

    plt.tight_layout()
    file_path = "progress_chart.png"
    plt.savefig(file_path)
    plt.close()

    return file_path
