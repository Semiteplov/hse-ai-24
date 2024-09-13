"""
Напишите генератор subsets, который принимает на вход список уникальных целых чисел и генерирует все подмножества этого списка. Пример использования приведен ниже.

lst = [1, 2, 30]
for subset in subsets(lst):
    print(subset)
Может вывести:

[]
[30]
[2]
[2, 30]
[1]
[1, 30]
[1, 2]
[1, 2, 30]
Должен работать метод next. Пример:

lst = [1, 2, 30]
gen = subsets(lst)
print(next(gen), next(gen))
Может вывести:

[] [30]
Порядок, в котором выводятся списки-подмножества, значения не имеет. Сдайте только код функции-генератора subsets и (после неё) допишите следующий код:

from sys import stdin
exec('\n'.join(stdin))
"""


def subsets(lst):
    n = len(lst)
    for i in range(2 ** n):
        subset = []
        for j in range(n):
            if i & (1 << j):  # Проверяем, включен ли j-й элемент в подмножество
                subset.append(lst[j])
        yield subset


from sys import stdin

exec('\n'.join(stdin))
