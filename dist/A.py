"""
Попробуйте представить, что вы участвовали в разработке Яндекс Контеста. Помогите посчитать результаты тестирования!

Формат ввода
Вводится число N - число посылок в контест от студентов. Далее вводится N строк: Фамилия студента, номер задачи и вердикт Яндекс контеста через пробел. Задача считается сданной, если получила вердикт "OK". Студент мог сдавать задачу несколько раз: если хотя бы одна попытка получила вердикт "ОК", задача считается сданной.

Формат вывода
Информация о каждом студенте: фамилия, количество отправленных посылок, количество сданных задач. Студенты должны быть отсортированы в алфавитном порядке.

Пример 1
Ввод	Вывод
10
Ivanov 1 WA
Petrov 2 WA
Ivanov 3 CE
Ivanov 1 OK
Petrov 3 OK
Ivanov 3 OK
Ivanov 2 OK
Sidorov 3 OK
Sidorov 3 OK
Sidorov 3 CE
Ivanov 5 3
Petrov 2 1
Sidorov 3 1
"""
n = int(input())
students = {}

for _ in range(n):
    last_name, problem, verdict = input().split()

    if last_name not in students:
        students[last_name] = {"attempts": 0, "solved_problems": set()}

    students[last_name]["attempts"] += 1

    if verdict == "OK":
        students[last_name]["solved_problems"].add(problem)

for last_name in sorted(students):
    attempts = students[last_name]["attempts"]
    solved = len(students[last_name]["solved_problems"])
    print(last_name, attempts, solved)
