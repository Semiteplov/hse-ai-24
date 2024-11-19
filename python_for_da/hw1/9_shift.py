"""
Напишите генератор cyclic_shift(s), который принимает строку s и на каждой итерации возвращает новую строку, где символы сдвинуты на одну позицию влево. Генератор должен продолжать возвращать сдвинутые версии строки до тех пор, пока не вернется к исходному порядку (на этом генератор должен прекратить работу).

Пример работы функции:

for seq in cyclic_shift("abcdef"):
    print(seq)
abcdef
bcdefa
cdefab
defabc
efabcd
fabcde
Сдайте только код функции-генератора и (после неё) допишите следующий код:

from sys import stdin
exec('\n'.join(stdin))
"""


def cyclic_shift(s):
    n = len(s)

    for i in range(n):
        yield s
        s = s[1:] + s[0]


from sys import stdin

exec('\n'.join(stdin))
