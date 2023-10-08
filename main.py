from utils import ParserEmployers, DBCreator, DBManager
from config import config

#Список компаний по которым ищем вакансии
employer_list = ['Аптрейд', 'Точка', 'АВ Софт', 'ЭНКОСТ',
                 'МКСКОМ', 'Бизнес-Азимут', 'Генотек', 'Creonit',
                 'ScanFactory', 'Фабрика Решений']

if __name__ == '__main__':
    #Параметры для входа в БД
    params = config()

    parser = ParserEmployers(employer_list)

    list_employers = parser.employers_collector()
    parser.saver(list_employers, 'employers.json')

    list_vacancies = parser.vacancies_collector('employers.json')
    parser.saver(list_vacancies, 'vacancies.json')

    employers_data = parser.employers_data_collector('employers.json')
    vacancies_data = parser.vacancies_data_collector('vacancies.json')

    db_creator =DBCreator('hhdb', params)
    db_creator.create_database()
    db_creator.save_data_to_database_empl(employers_data)
    db_creator.save_data_to_database_vac(vacancies_data)

    db_manager = DBManager('hhdb', params)
    db_manager.get_companies_and_vacancies_count()
    db_manager.get_all_vacancies()
    db_manager.get_avg_salary()
    db_manager.get_vacancies_with_higher_salary()
    db_manager.get_vacancies_with_keyword()
