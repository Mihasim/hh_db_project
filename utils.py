import json

import requests as requests
import psycopg2


class ParserEmployers:
    """
    Получение списка работодателей и вакансий
    этих работадателй с сайта hh.ru.
    Данные записываются в json файлы
    """

    def __init__(self, keywords: list) -> None:
        self.keywords = keywords

    def employers_collector(self) -> list:
        """
        Получение списка работодателей с сайта hh.ru
        """
        employers_list = []
        for keyword in self.keywords:
            url = f"https://api.hh.ru/employers"
            response = requests.get(url, params={"text": keyword,
                                                 "per_page": 10,
                                                 "page": 0})
            employers = response.json()
            for employer in employers["items"]:
                if employer["open_vacancies"] > 0: #Выводим только те компании у которых есть открытые вакансии
                    employers_list.append(employer)
        return employers_list

    def vacancies_collector(self, employers_list) -> list:
        """
        Получение списка вакансий по работодателям с сайта hh.ru
        """
        with open(employers_list, 'r', encoding="utf-8") as f:
            data_vacancies = json.load(f)

        vacancies_list = []
        for data in data_vacancies:
            vacancies_url = data["vacancies_url"] #ссылка на вакансии
            vacancies_data = requests.get(vacancies_url).json()
            for vacancy in vacancies_data["items"]:
                vacancies_list.append(vacancy)
        return vacancies_list

    def employers_data_collector(self, employers_list):
        """
        Запиывает данные о работодателях
        (id, name, open_vacancies)
        в json файл
        """

    def vacancies_data_collector(self, vacancies_list):
        """
        Записывает данные о вакансиях
        (id, name, area[name], salary[from], salary[to], alternate_url, employer[name])
        в json файл
        """

    @staticmethod
    def saver(list_vacancies: list, file_name: str):
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(list_vacancies, f, indent=2, ensure_ascii=False)
        print(f'"{file_name}" сохранено')


class DBManager:
    def __init__(self):
        pass

    def get_companies_and_vacancies_count(self):
        '''
        получает список всех компаний и количество вакансий у каждой компании.
        :return:
        '''

    def get_all_vacancies(self):
        '''
        получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию.
        :return:
        '''

    def get_avg_salary(self):
        '''
        получает среднюю зарплату по вакансиям.
        :return:
        '''

    def get_vacancies_with_higher_salary(self):
        '''
        получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.
        :return:
        '''

    def get_vacancies_with_keyword(self):
        '''
        получает список всех вакансий, в названии которых
        содержатся переданные в метод слова, например python.
        :return:
        '''
