"""
Иногда требуется в качестве решение прислать только функцию/класс и код, запускающий тесты.

Условие задачи: напишите функцию interesting_trunc, которая принимает на вход список строк и возвращает новый список, который содержит измененные строки:

все строки переводятся в нижний регистр
если в строке было больше пяти символов, остаются только первые пять символов.
Сдайте код функции interesting_trunc, и допишите после неё код, запускающий тесты:

from sys import stdin
exec('\n'.join(stdin))
Что делаем? Сдаем в контест следующий код (не забудьте его дополнить, дописав функцию):

def interesting_trunc(list of strings):
    # код функции
    return # список, который возвращает функция

from sys import stdin
exec('\n'.join(stdin))
exec будет запускать код из тестов, которые используют Вашу функцию. Поэтому функция должна называться так, как в условии.
"""


def interesting_trunc(lines):
    formatted_lines = []
    for line in lines:
        if len(line) > 5:
            formatted_lines.append(line[:5].lower())
        else:
            formatted_lines.append(line.lower())

    return formatted_lines


print(interesting_trunc(['python', 'math', 'AI', 'machine learning']))

from sys import stdin

exec('\n'.join(stdin))
