"""
Создайте декоратор log_plagiat_check, который будет использоваться для функции is_plagiat из предыдущей задачи. Этот декоратор должен выводить на экран информацию о том, какие слова проверяются и какой результат проверки.

Решение обязательно должно содержать:

код декоратора log_plagiat_check
код функции is_plagiat
чтение входных данных и применение функции is_plagiat
Входные данные необходимо считать из файла "words.txt". Файл содержит неизвестное число строк. Каждая строка содержит два слова через пробел. Необходимо для каждой строки вывести на экран:

оба слова
результат действия функции is_plagiat
Формат ввода
Файл words.txt.

Файл содержит неизвестное число строк. Каждая строка содержит два слова через пробел.

Формат вывода
Строка формата "Check '{слово1}' vs '{слово2}' -> '{True/False}'"

Пример
Ввод	Вывод
word wordtrue
df Df
words word
Check 'word' vs 'wordtrue' -> False
Check 'df' vs 'Df' -> True
Check 'words' vs 'word' -> True
"""


def log_plagiat_check(func):
    def wrapper(word1, word2):
        result = func(word1, word2)
        print(f"Check '{word1}' vs '{word2}' -> {result}")
        return result

    return wrapper


@log_plagiat_check
def is_plagiat(w1, w2):
    w1 = sorted(w1.lower())
    w2 = sorted(w2.lower())
    s = set()

    for char in w2:
        if char not in w1:
            s.add(char)
    return len(s) < 2


with open("words.txt", "r") as file:
    for line in file:
        word1, word2 = line.strip().split()
        is_plagiat(word1, word2)
