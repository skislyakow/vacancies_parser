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
print()

params_py = {"locations[]": "c_678", "q": "Python"}
response_py = requests.get(url, params=params_py)
response_py.raise_for_status()
data_py = response_py.json()

for vacancy in data_py["list"]:
    print(vacancy["salary"])
