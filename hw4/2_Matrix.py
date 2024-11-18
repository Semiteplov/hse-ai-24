from sys import stdin


class Matrix():
    def __init__(self, data) -> None:
        self.data = [row[:] for row in data]

    def __str__(self) -> str:
        return '\n'.join(['\t'.join(map(str, row)) for row in self.data])

    def size(self):
        return (len(self.data), len(self.data[0]))


exec(stdin.read())
