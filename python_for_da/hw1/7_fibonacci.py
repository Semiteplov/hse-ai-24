"""
В этой задаче Вам предлагается написать функцию-генератор, которая генерирует следующий элемент последовательности Фибоначчи.

В последовательности Фибоначчи каждый элемент равен сумме двух предыдущих: 0, 1, 1, 2, 3, 5, 8, 13...

Сдайте код генератора fibonacci и в конце допишите следующий код:

from sys import stdin
exec('\n'.join(stdin))
Должен работать метод next(). Например, код ниже

gen = fibonacci()
print(next(gen))
print(next(gen))
Должен выводить:

0
1
"""


def fibonacci():
    a, b = 0, 1
    yield a
    while True:
        yield b
        a, b = b, a + b


from sys import stdin

exec('\n'.join(stdin))
