import json
from typing import Any

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
                if employer["open_vacancies"] > 0:  # Выводим только те компании у которых есть открытые вакансии
                    employers_list.append(employer)
        return employers_list

    def vacancies_collector(self, employers_list: str) -> list:
        """
        Получение списка вакансий по работодателям с сайта hh.ru
        """
        with open(employers_list, 'r', encoding="utf-8") as f:
            data_vacancies = json.load(f)

        vacancies_list = []
        for data in data_vacancies:
            vacancies_url = data["vacancies_url"]  # ссылка на вакансии
            vacancies_data = requests.get(vacancies_url).json()
            for vacancy in vacancies_data["items"]:
                vacancies_list.append(vacancy)
        return vacancies_list

    def employers_data_collector(self, employers_list: str) -> list[dict]:
        """
        Запиывает данные о работодателях
        (id, name, open_vacancies)
        в json файл
        """
        with open(employers_list, 'r', encoding="utf-8") as f:
            employers_data = json.load(f)
        employers_list_dict = []
        for data in employers_data:
            employers_dict = {
                'employer_id': data['id'],
                'employer_name': data['name'],
                'employer_url': data['alternate_url'],
                'employer_open_vacancies': data['open_vacancies']
            }
            employers_list_dict.append(employers_dict)
        return employers_list_dict

    def vacancies_data_collector(self, vacancies_list: str) -> list[dict]:
        """
        Записывает данные о вакансиях
        (id, name, area[name], salary[from], salary[to], alternate_url, employer[name])
        в json файл
        """
        with open(vacancies_list, 'r', encoding="utf-8") as f:
            vacancies_data = json.load(f)
        vacancies_list_dict = []
        for data in vacancies_data:
            try:
                vacancies_salary_from = data['salary']['from']
                if type(vacancies_salary_from) != int:
                    vacancies_salary_from = 0
            except TypeError:
                vacancies_salary_from = 0

            try:
                vacancies_salary_to = data['salary']['to']
                if vacancies_salary_to is None:
                    vacancies_salary_to = 0
            except TypeError:
                vacancies_salary_to = 0

            vacancies_dict = {
                'vacancy_id': data['id'],
                'vacancy_name': data['name'],
                'vacancy_employer': data['employer']['name'],
                'vacancy_salary_from': vacancies_salary_from,
                'vacancy_salary_to': vacancies_salary_to,
                'vacancy_area': data['area']['name'],
                'vacancy_url': data['alternate_url'],
            }
            vacancies_list_dict.append(vacancies_dict)
        return vacancies_list_dict

    @staticmethod
    def saver(list_vacancies: list, file_name: str) -> None:
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(list_vacancies, f, indent=2, ensure_ascii=False)
        print(f'"{file_name}" сохранено')


class DBCreator:
    def __init__(self, database_name: str, params: dict) -> None:
        self.database_name = database_name
        self.params = params

    def create_database(self) -> None:
        """
        Создание базы данных и таблиц для сохранения данных о работодателях и вакансиях
        """

        conn = psycopg2.connect(dbname='postgres', **self.params)
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(f"DROP DATABASE IF EXISTS {self.database_name}")
        cur.execute(f"CREATE DATABASE {self.database_name}")

        conn.close()

        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE employers (
                    employer_id VARCHAR(10) UNIQUE PRIMARY KEY ,
                    employer_name VARCHAR(99) UNIQUE NOT NULL,
                    employer_url VARCHAR(99),
                    employer_open_vacancies INTEGER
                )
            """)
        with conn.cursor() as cur:
            cur.execute("""
                   CREATE TABLE vacancies (
                       vacancy_id VARCHAR(10) PRIMARY KEY,
                       vacancy_name VARCHAR(99),
                       employer_name VARCHAR(99) NOT NULL REFERENCES employers(employer_name),
                       vacancy_salary_from INT,
                       vacancy_salary_to INT,
                       vacancy_area VARCHAR(99),
                       vacancy_url VARCHAR(99)
                   )
               """)

        conn.commit()
        conn.close()

    def save_data_to_database_empl(self, employers: list[dict[str, Any]]) -> None:
        """
        Сохранение данных о работодателях и вакансиях в базу данных.
        """

        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            for employer in employers:
                cur.execute(
                    """
                    INSERT INTO employers (employer_id, employer_name, employer_url, employer_open_vacancies)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (employer['employer_id'], employer['employer_name'], employer['employer_url'],
                     employer['employer_open_vacancies'])
                )
        conn.commit()
        conn.close()

    def save_data_to_database_vac(self, vacancies: list[dict]) -> None:
        """
        Сохранение данных о работодателях и вакансиях в базу данных.
        """

        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            for vacancy in vacancies:
                cur.execute(
                    """
                    INSERT INTO vacancies (vacancy_id, vacancy_name, employer_name, 
                    vacancy_salary_from, vacancy_salary_to, vacancy_area, vacancy_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (vacancy['vacancy_id'], vacancy['vacancy_name'], vacancy['vacancy_employer'],
                     vacancy['vacancy_salary_from'], vacancy['vacancy_salary_to'],
                     vacancy['vacancy_area'], vacancy['vacancy_url'])
                )
        conn.commit()
        conn.close()


class DBManager:
    def __init__(self, database_name: str, params: dict) -> None:
        self.database_name = database_name
        self.params = params

    def get_companies_and_vacancies_count(self) -> None:
        """
        получает список всех компаний и количество вакансий у каждой компании.
        """
        print('\n\nсписок всех компаний и количество вакансий у каждой компании')
        conn = psycopg2.connect(dbname=self.database_name, **self.params)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT employer_name, employer_open_vacancies FROM employers
                """
            )
            rows = cur.fetchall()
            for row in rows:
                print(row)
        conn.close()

    def get_all_vacancies(self) -> None:
        """
        получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию.
        """
        print('\n\nСписок всех вакансий с указанием названия компании, '
              'названия вакансии и зарплаты и ссылки на вакансию.')
        conn = psycopg2.connect(dbname=self.database_name, **self.params)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT employer_name, vacancy_name, vacancy_salary_from, vacancy_url FROM vacancies
                """
            )
            rows = cur.fetchall()
            for row in rows:
                print(row)
        conn.close()

    def get_avg_salary(self) -> None:
        """
        получает среднюю зарплату по вакансиям.
        """
        print('\n\nсредняя зарплата по вакансиям.')
        conn = psycopg2.connect(dbname=self.database_name, **self.params)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT AVG(vacancy_salary_from) 
                FROM vacancies
                WHERE vacancy_salary_from > 0
                """
            )
            rows = cur.fetchall()
            for row in rows:
                print(row)
        conn.close()

    def get_vacancies_with_higher_salary(self) -> None:
        """
        получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.
        """
        print('\n\nсписок всех вакансий, у которых зарплата выше средней по всем вакансиям.')
        conn = psycopg2.connect(dbname=self.database_name, **self.params)
        with conn.cursor() as cur:
            cur.execute(
                """
            SELECT vacancy_name, vacancy_salary_from
            FROM vacancies
            WHERE vacancy_salary_from > (
                SELECT AVG(vacancy_salary_from) 
                FROM vacancies
                WHERE vacancy_salary_from > 0)
	        """
            )
            rows = cur.fetchall()
            for row in rows:
                print(row)
        conn.close()

    def get_vacancies_with_keyword(self) -> None:
        """
        получает список всех вакансий, в названии которых
        содержатся переданные в метод слова, например python.
        """
        print('\n\nСписок всех вакансий, в названии которых '
              'содержатся переданные в метод слова, например python.')
        conn = psycopg2.connect(dbname=self.database_name, **self.params)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM vacancies
                WHERE vacancy_name LIKE '%Python%' OR vacancy_name LIKE '%python%'
                """
            )
            rows = cur.fetchall()
            for row in rows:
                print(row)
        conn.close()
