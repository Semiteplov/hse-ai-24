from sys import stdin


class Matrix():
    def __init__(self, data) -> None:
        self.data = [row[:] for row in data]

    def __str__(self) -> str:
        return '\n'.join(['\t'.join(map(str, row)) for row in self.data])

    def size(self):
        return (len(self.data), len(self.data[0]))

    def __add__(self, other: 'Matrix') -> 'Matrix':
        result = []
        for i in range(len(self.data)):
            row = []
            for j in range(len(self.data[0])):
                row.append(self.data[i][j] + other.data[i][j])
            result.append(row)

        return Matrix(result)

    def __mul__(self, number) -> 'Matrix':
        result = []
        for i in range(len(self.data)):
            row = []
            for j in range(len(self.data[0])):
                row.append(self.data[i][j] * number)
            result.append(row)

        return Matrix(result)

    __rmul__ = __mul__


# exec(stdin.read())

m = Matrix([[1, 1, 0], [0, 2, 10], [10, 15, 30]])
alpha = 15
print(m * alpha)
print(alpha * m)
