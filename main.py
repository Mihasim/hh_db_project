from utils import ParserEmployers


employer_list = ['Аптрейд', 'Точка', 'АВ Софт', 'ЭНКОСТ',
                 'МКСКОМ', 'Бизнес-Азимут', 'Генотек', 'Creonit',
                 'ScanFactory', 'Фабрика Решений']

if __name__ == '__main__':
    parser = ParserEmployers(employer_list)
    list_employers = parser.employers_collector()
    parser.saver(list_employers, 'employers.json')

    list_vacancies = parser.vacancies_collector('employers.json')
    parser.saver(list_vacancies, 'vacancies.json')

    parser.employers_data_collector('employers.json')
    parser.vacancies_data_collector('vacancies.json')