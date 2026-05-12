import requests
from environs import Env
from terminaltables import AsciiTable


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from:
        return salary_from * 1.2
    elif salary_to:
        return salary_to * 0.8
    else:
        return None


def predict_rub_salary(vacancy):
    salary = vacancy["salary"]
    if salary is None:
        return None
    if salary.get("currency") != "rur":
        return None
    return predict_salary(salary.get("from"), salary.get("to"))


def predict_rub_salary_superjob(vacancy):
    if vacancy.get("currency") != "rub":
        return None
    if (
        vacancy.get("agreement")
        and not vacancy.get("payment_from")
        and not vacancy.get("payment_to")
    ):
        return None
    return predict_salary(
        vacancy.get("payment_from"), vacancy.get("payment_to")
    )


def parse_from_superjob(languages):
    env = Env()
    env.read_env()
    superjob_url = "https://api.superjob.ru/2.0/vacancies/"
    title = "SuperJob"
    salary_statistics = {}
    headers = {"X-Api-App-Id": env.str("SUPERJOB_APP_ID")}

    for lang in languages:
        all_vacancies = []
        page = 0
        while True:
            params = {
                "page": page,
                "count": 100,
                "town": 4,
                "keyword": lang,
                "no_agreement": 1,
            }
            response = requests.get(
                superjob_url, headers=headers, params=params
            )
            data = response.json()
            vacancies = data.get("objects", [])
            all_vacancies.extend(vacancies)
            if not data.get("more"):
                break
            page += 1

        salaries = []
        for vacancy in all_vacancies:
            salary = predict_rub_salary_superjob(vacancy)
            if salary is not None:
                salaries.append(salary)

        vacancies_found = data.get("total", 0)
        vacancies_processed = len(salaries)
        average_salary = (
            int(sum(salaries) / len(salaries)) if salaries else None
        )
        salary_statistics[lang] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": vacancies_processed,
            "average_salary": average_salary,
        }
    print_statistics(salary_statistics, title)
    print()


def parse_from_habr(languages):
    habr_url = "https://career.habr.com/api/frontend/vacancies"
    title = "Habr"
    base_params = {"locations[]": "c_678"}
    salary_statistics = {}
    for lang in languages:
        params = base_params.copy()
        params["q"] = f"{lang}"
        params["per_page"] = 50

        response = requests.get(habr_url, params=params)
        response.raise_for_status()
        data = response.json()

        vacancies_found = data["meta"]["totalResults"]
        total_pages = data["meta"]["totalPages"]
        all_vacancies = data["list"]

        for page in range(2, total_pages + 1):
            params["page"] = page
            response = requests.get(habr_url, params=params)
            response.raise_for_status()
            data = response.json()
            all_vacancies.extend(data["list"])

        salaries = []
        for vacancy in all_vacancies:
            salary = predict_rub_salary(vacancy)
            if salary is not None:
                salaries.append(salary)

        vacancies_processed = len(salaries)
        average_salary = (
            int(sum(salaries) / len(salaries)) if salaries else None
        )

        salary_statistics[lang] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": vacancies_processed,
            "average_salary": average_salary,
        }

    print_statistics(salary_statistics, title)
    print()


def print_statistics(statistics, title):
    table_data = [
        [
            "Язык программирования",
            "Вакансий найдено",
            "Вакансий обработано",
            "Средняя зарплата",
        ]
    ]
    for lang, data in statistics.items():
        table_data.append(
            [
                lang,
                data["vacancies_found"],
                data["vacancies_processed"],
                data["average_salary"],
            ]
        )
    table = AsciiTable(table_data)
    table_title = title + "-" * (table.table_width - len(title))
    print(table_title)
    print(table.table)


def main():

    languages = [
        "Python",
        "Java",
        "JavaScript",
        "C",
        "C#",
        "C++",
        "PHP",
        "Ruby",
        "Go",
        "Rust",
        "Kotlin",
        "TypeScript",
        "Swift",
        "1C",
    ]

    parse_from_habr(languages)
    parse_from_superjob(languages)


if __name__ == "__main__":
    main()
