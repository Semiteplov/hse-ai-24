class Student():
    def __init__(self, name, surname, grade) -> None:
        self.name = name
        self.surname = surname
        self.grade = grade

    def add_grade(self):
        self.grade += 1

    def print_info(self):
        print(f'Student: {self.name} {self.surname}')
        print(f'Grade: {self.grade}')


class PythonStudent(Student):
    def __init__(self, name, surname, grade) -> None:
        super().__init__(name, surname, grade)
        self.python_mark = 0
        self.learned_python = False

    def learn_python(self):
        self.learned_python = True

    def get_mark_python(self, hw1, hw2, hw3, hw4):
        if not self.learned_python:
            print('Надо пойти учить питон')
            return 0
        self.python_mark = round(0.3 * hw1 + 0.3 * hw2 + 0.3 * hw3 + 0.1 * hw4)
        return self.python_mark

    def print_info(self):
        super().print_info()
        print(f'Python mark: {self.python_mark}')


for i in range(8):
    exec(input())
