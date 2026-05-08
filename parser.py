import time

import requests


languages = [
    "Python",
    "Java",
    "JavaScript",
    "C#",
    "C++",
    "PHP",
    "Ruby",
    "Go",
    "Rust",
    "Kotlin",
    "TypeScript",
    "Swift",
]

url = "https://career.habr.com/api/frontend/vacancies"

base_params = {"locations[]": "c_678"}


def predict_rub_salary(vacancy):
    salary = vacancy["salary"]
    if salary is None:
        return None
    if salary.get("currency") != "rur":
        return None

    salary_from = salary.get("from")
    salary_to = salary.get("to")

    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from:
        return salary_from * 1.2
    elif salary_to:
        return salary_to * 0.8
    else:
        return None


result = {}

for lang in languages:
    params = base_params.copy()
    params["q"] = f"{lang}"
    params["per_page"] = 50

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    vacancies_found = data["meta"]["totalResults"]
    total_pages = data["meta"]["totalPages"]
    all_vacancies = []

    for page in range(1, total_pages + 1):
        params["page"] = page
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        all_vacancies.extend(data["list"])
        # time.sleep(0.5)

    salaries = []
    for vacancy in all_vacancies:
        salary = predict_rub_salary(vacancy)
        if salary is not None:
            salaries.append(salary)

    vacancies_processed = len(salaries)
    average_salary = int(sum(salaries) / len(salaries)) if salaries else None

    result[lang] = {
        "vacancies_found": vacancies_found,
        "vacancies_processed": vacancies_processed,
        "average_salary": average_salary,
    }

print(result)
print()


params_py = {"locations[]": "c_678", "q": "Python"}
response_py = requests.get(url, params=params_py)
response_py.raise_for_status()
data_py = response_py.json()

for vacancy in data_py["list"]:
    print(predict_rub_salary(vacancy))
