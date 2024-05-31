import httpx
import asyncio
import json

# id_vacancy: list[int] = []

employment_dict = {
    "Полная занятость": "full",
    "Частичная занятость": "part",
    "Проектная работа": "project",
    "Волонтерство": "volunteer",
    "Стажировка": "probation",
}

async def get_city_id(city: str) -> int | str:
    url = f"https://api.hh.ru/suggests/areas?text={city}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        data = r.json()

        if (len(data['items']) == 0):
            return "Нет такого города"
        else:
            return data['items'][0]['id']

async def get_vacancies(city_id: int, job: str, amount: int) -> str:
    vacancies: list[Vacancy] = []
    text: str = ""
    url = f'https://api.hh.ru/vacancies?host=rabota.by&area={city_id}&text="{job}"&order_by=publication_time&per_page={amount}'

    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        data = r.json()

    amount_vacancies = len(data["items"])

    if (amount > amount_vacancies):
        amount = amount_vacancies

    if (amount_vacancies == 0):
        return "Нет подходящих вакансий"
    
    else:
        for i in range(0, amount):
            instance = data["items"][i] 

            text += instance["name"] + "\n"
                
            if (instance["salary"] is None):
                text += "Договорная \n"
            elif (instance["salary"]["to"] is None):
                text += f"{instance["salary"]["from"]} {instance["salary"]["currency"]} \n"
            elif (instance["salary"]["from"] is None):
                text += f"{instance["salary"]["to"]} {instance["salary"]["currency"]} \n"
            else:  
                text += f"От {instance["salary"]["from"]} до {instance["salary"]["to"]} \n"

            text += instance["experience"]["name"] + "\n"
            text += instance["alternate_url"] + "\n"
            text += "\n"

        return text

