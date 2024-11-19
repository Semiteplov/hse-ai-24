"""
Реализуйте генератор tribonacci_generator(), который генерирует последовательность чисел
(каждый элемент равен сумме трёх предыдущих): 0, 1, 1, 2, 4, 7, 13, 24, 44, 81, 149, 274...

Пример работы функции представлен ниже.

gen = tribonacci_generator()
print(next(gen))
print(next(gen))
print(next(gen))
0
1
1
Сдайте только код функции-генератора и (после неё) допишите следующий код:

from sys import stdin
exec('\n'.join(stdin))
"""


def tribonacci_generator():
    a, b, c = 0, 1, 1
    yield a
    yield b
    yield c
    while True:
        next_value = a + b + c
        yield next_value
        a, b, c = b, c, next_value


from sys import stdin

exec('\n'.join(stdin))
