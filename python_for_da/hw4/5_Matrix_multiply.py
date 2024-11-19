from sys import stdin


class Matrix():
    def __init__(self, data) -> None:
        self.data = [row[:] for row in data]

    def __str__(self) -> str:
        return '\n'.join(['\t'.join(map(str, row)) for row in self.data])

    def size(self):
        return (len(self.data), len(self.data[0]))

    def __add__(self, other: 'Matrix') -> 'Matrix':
        if self.size() != other.size():
            raise MatrixError(self, other)
        
        result = []
        for i in range(len(self.data)):
            row = []
            for j in range(len(self.data[0])):
                row.append(self.data[i][j] + other.data[i][j])
            result.append(row)

        return Matrix(result)

    def __mul__(self, other) -> 'Matrix':
        if isinstance(other, (int, float)):
            result = []
            for i in range(len(self.data)):
                row = []
                for j in range(len(self.data[0])):
                    row.append(self.data[i][j] * other)
                result.append(row)
            return Matrix(result)
        
        else:
            if self.size()[1] != other.size()[0]:
                raise MatrixError(self, other)

            result = []
            for i in range(len(self.data)):
                new_row = []
                for j in range(len(other.data[0])):
                    element_sum = 0
                    for k in range(len(self.data[0])):
                        element_sum += self.data[i][k] * other.data[k][j]
                    new_row.append(element_sum)
                result.append(new_row)
            return Matrix(result)

    __rmul__ = __mul__

    def transpose(self) -> 'Matrix':
        transposed_data = []
        for j in range(len(self.data[0])):
            new_row = []
            for i in range(len(self.data)):
                new_row.append(self.data[i][j])
            transposed_data.append(new_row)
        self.data = transposed_data
        return self


class MatrixError(Exception):
    def __init__(self, matrix1: 'Matrix', matrix2: 'Matrix') -> None:
        self.matrix1 = matrix1
        self.matrix2 = matrix2


exec(stdin.read())
