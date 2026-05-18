import requests
from environs import Env
from terminaltables import AsciiTable


HABR_MOSCOW_CITY_ID = "c_678"
HABR_PER_PAGE = 50

SUPERJOB_MOSCOW_CITY_ID = 4
SUPERJOB_PER_PAGE = 100
SUPERJOB_NO_AGREEMENT = 1


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from:
        return salary_from * 1.2
    elif salary_to:
        return salary_to * 0.8
    else:
        return None


def predict_rub_salary_hh(vacancy):
    salary = vacancy["salary"]
    if not salary:
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


def get_habr_vacancies(language):
    habr_url = "https://career.habr.com/api/frontend/vacancies"

    params = {
        "locations[]": HABR_MOSCOW_CITY_ID,
        "q": language,
        "per_page": HABR_PER_PAGE,
    }

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

    return vacancies_found, all_vacancies


def get_superjob_vacancies(language, headers):
    superjob_url = "https://api.superjob.ru/2.0/vacancies/"

    all_vacancies = []
    page = 0
    while True:
        params = {
            "page": page,
            "count": SUPERJOB_PER_PAGE,
            "town": SUPERJOB_MOSCOW_CITY_ID,
            "keyword": language,
            "no_agreement": SUPERJOB_NO_AGREEMENT,
        }
        response = requests.get(superjob_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        vacancies = data.get("objects", [])
        all_vacancies.extend(vacancies)
        if not data.get("more"):
            break
        page += 1
    vacancies_found = data.get("total", 0)
    return vacancies_found, all_vacancies


def calculate_salary_statistics(vacancies, predict_salary_func):
    salaries = []
    for vacancy in vacancies:
        salary = predict_salary_func(vacancy)
        if salary:
            salaries.append(salary)

    vacancies_processed = len(salaries)
    average_salary = int(sum(salaries) / len(salaries)) if salaries else None

    return vacancies_processed, average_salary


def parse_from_superjob(languages, superjob_headers):
    salary_statistics = {}
    for lang in languages:
        vacancies_found, all_vacancies = get_superjob_vacancies(
            lang, superjob_headers
        )
        vacancies_processed, average_salary = calculate_salary_statistics(
            all_vacancies, predict_rub_salary_superjob
        )
        salary_statistics[lang] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": vacancies_processed,
            "average_salary": average_salary,
        }

    return salary_statistics


def parse_from_habr(languages):
    salary_statistics = {}
    for lang in languages:
        vacancies_found, all_vacancies = get_habr_vacancies(lang)
        vacancies_processed, average_salary = calculate_salary_statistics(
            all_vacancies, predict_rub_salary_hh
        )
        salary_statistics[lang] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": vacancies_processed,
            "average_salary": average_salary,
        }

    return salary_statistics


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
    table_title = f"{title}{'-' * (table.table_width - len(title))}"
    print(table_title)
    print(table.table)
    print()


def main():
    env = Env()
    env.read_env()

    superjob_headers = {"X-Api-App-Id": env.str("SUPERJOB_APP_ID")}

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

    print_statistics(parse_from_habr(languages), "Habr")
    print_statistics(
        parse_from_superjob(languages, superjob_headers), "SuperJob"
    )


if __name__ == "__main__":
    main()
