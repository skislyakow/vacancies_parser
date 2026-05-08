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
result = {}

for lang in languages:
    params = base_params.copy()
    params["q"] = f"{lang}"
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    result[lang] = data["meta"]["totalResults"]

print(result)
