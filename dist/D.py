"""
Реализуйте класс Student, атрибутами которого являются name, surname и grade и который содержит следующие методы:

add_grade(без аргументов), увеличивающий значение атрибута grade на 1
print_info(без аргументов), печатающий информацию в следующем формате:
Student: {name} {surname}
Grade: {grade}
Например:

Student: Ivan Ivanov
Grade: 3
Реализуйте его подкласс PythonStudent, который дополнительно содержит атрибут python_mark со значением по умолчанию 0 и следующие методы:

learn_python(без аргументов), который открывает метод get_mark_python
get_mark_python(hw1, hw2, hw3, hw4) - принимает оценку за четыре ДЗ и возвращает оценку за курс по формуле 0.3hw1+ 0.3hw2 + 0.3hw3 + 0.1hw4, округленную до целого числа. Полученное значение также присваивается атрибуту python_mark
print_info(без аргументов), который должен печатать информацию о студенте в таком формате:
Student: {name} {surname}
Grade: {grade}
Python mark: {python_mark}
Например:

Student: Ivan Ivanov
Grade: 3
Python mark: 0
Метод print_info класса PythonStudent при этом должен вызывать соответствующий метод родительского класса. Это будет проверяться вручную.

Если к объекту PythonStudent применить метод get_mark_python до применения метода learn_python, метод возвращает число 0 и печатает строку "Надо пойти учить питон".

Пожалуйста, в конце кода впишите (для исполнения тестов) следующее выражение:

for i in range(8):
    exec(input())
Пример
Ввод	Вывод
s1 = Student("Ivan", "Ivanov", 3)
s2 = PythonStudent("Petr", "Ivanov", 2)
print(s1.name, s1.surname, s1.grade)
print(s2.name, s2.surname)
print(s2.grade)
Ivan Ivanov 3
Petr Ivanov
2
"""


class Student:
    def __init__(self, name, surname, grade):
        self.name = name
        self.surname = surname
        self.grade = grade

    def add_grade(self):
        self.grade += 1

    def print_info(self):
        print(f"Student: {self.name} {self.surname}")
        print(f"Grade: {self.grade}")


class PythonStudent(Student):
    def __init__(self, name, surname, grade):
        super().__init__(name, surname, grade)
        self.python_mark = 0
        self._learned_python = False

    def learn_python(self):
        self._learned_python = True

    def get_mark_python(self, hw1, hw2, hw3, hw4):
        if not self._learned_python:
            print("Надо пойти учить питон")
            return 0

        self.python_mark = round(0.3 * hw1 + 0.3 * hw2 + 0.3 * hw3 + 0.1 * hw4)
        return self.python_mark

    def print_info(self):
        super().print_info()
        print(f"Python mark: {self.python_mark}")


for i in range(8):
    exec(input())
