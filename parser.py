import requests


url = "https://career.habr.com/api/frontend/vacancies"
params_all = {"locations[]": "c_678"}
response_all = requests.get(url, params=params_all)
response_all.raise_for_status()
data_all = response_all.json()
print("Всего вакансий в Москве:", data_all["meta"]["totalResults"])

params_py = {"locations[]": "c_678", "q": "python"}
response_py = requests.get(url, params_py)
response_py.raise_for_status()
data_py = response_py.json()
print("Python вакансий в Москве:", data_py["meta"]["totalResults"])
