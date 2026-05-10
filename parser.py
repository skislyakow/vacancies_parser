import os
import time

import requests
from environs import Env


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

habr_url = "https://career.habr.com/api/frontend/vacancies"
superjob_url = "https://api.superjob.ru/2.0/vacancies/"


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


def parse_from_superjob(superjob_url, superjob_app_id, page=0, count=20):
    headers = {"X-Api-App-Id": superjob_app_id}
    params = {
        "page": page,
        "count": count,
        "town": 4,
        "catalogues": 48,
    }
    response = requests.get(superjob_url, headers=headers, params=params)
    data = response.json()
    for vacancy in data.get("objects", []):
        print(f"{vacancy['profession']}, {vacancy['town']['title']}")


def parse_from_habr(habr_url):
    for lang in languages:
        params = base_params.copy()
        params["q"] = f"{lang}"
        params["per_page"] = 50

        response = requests.get(habr_url, params=params)
        response.raise_for_status()
        data = response.json()

        vacancies_found = data["meta"]["totalResults"]
        total_pages = data["meta"]["totalPages"]
        all_vacancies = []

        for page in range(1, total_pages + 1):
            params["page"] = page
            response = requests.get(habr_url, params=params)
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
        average_salary = (
            int(sum(salaries) / len(salaries)) if salaries else None
        )

        result[lang] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": vacancies_processed,
            "average_salary": average_salary,
        }

    print(result)
    print()

    params_py = {"locations[]": "c_678", "q": "Python"}
    response_py = requests.get(habr_url, params=params_py)
    response_py.raise_for_status()
    data_py = response_py.json()

    for vacancy in data_py["list"]:
        print(predict_rub_salary(vacancy))


def main():
    env = Env()
    env.read_env()
    superjob_app_id = env.str("SUPERJOB_APP_ID")
    # parse_from_habr()

    print(parse_from_superjob(superjob_url, superjob_app_id, page=0, count=20))
    # Получить ID Москвы

    pass


if __name__ == "__main__":
    main()
