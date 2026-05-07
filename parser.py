import requests


url = "https://career.habr.com/api/frontend/vacancies"
params = {"locations[]": "c_678"}
response = requests.get(url, params=params)
response.raise_for_status()

data = response.json()
print("Всего найдено:", data["meta"]["totalResults"])
print("Первая вакансия:")
print(data["list"][0])
