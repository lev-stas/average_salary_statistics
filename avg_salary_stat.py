import requests
from terminaltables import DoubleTable
from dotenv import load_dotenv
import argparse
import os

HH_URL = 'https://api.hh.ru/vacancies/'
SJ_URL = 'https://api.superjob.ru/2.30/vacancies'

LANGUAGES = ['C', 'C++', 'C#', 'Python','Java', 'Javascript','Ruby', 'Scala','Go', '1C', 'PHP', 'DevOps','Data Analyst','Data Scientist']

def get_city_id_hh (city_name):
    city_response = requests.get('https://api.hh.ru/areas')
    locations = city_response.json()
    for country in locations:
        if city_name in country.values():
            return country['id']
        else:
            for region in country['areas']:
                if city_name in region.values():
                    return region['id']
                else:
                    for city in region['areas']:
                        if city_name in city.values():
                            return city['id']


def get_city_id_sj (city_name):
    city_response = requests.get('https://api.superjob.ru/2.30/regions/combined', headers = sj_headers)
    locations = city_response.json()
    for country in locations:
        if not 'title' in country.keys():
            continue
        else:
            for city in country['towns']:
                if city_name in city.values():
                    return city['id']
            if not 'regions' in country.keys():
                continue
            else:
                for region in country['regions']:
                    if city_name == region['title']:
                        return region['id']
                    else:
                        for town in region['towns']:
                            if city_name in town.values():
                                return town['id']
                    

def get_hh_vacancies (params):
    
    vacancies = []
    page = 0
    pages = 1
    
    while page < pages:
        params['page'] = page
        response = requests.get(HH_URL, params=params)
        response.raise_for_status()
        answer = response.json()
        for item in answer['items']:
            vacancies.append(item)
        page += 1
        pages = answer['pages']
    return vacancies

def get_salary_statistics_hh (language_list):
    statistics = {}
    for language in language_list:
        request_params = {
            'text' : f'{language}',
            'area' : get_city_id_hh (city_name),
            'period' : 30,
            'only_with_salary' : True
        }
        
        answer = get_hh_vacancies(request_params)
        number_and_avg_salary = count_avg_language_salary_hh(answer)
        vacancies_count = len(answer)
        vacancies_processed = number_and_avg_salary[0]
        avg_salary = number_and_avg_salary[1]
        statistics[language]={
            'vacancies_count': vacancies_count,
            'vacancies_processed' : vacancies_processed,
            'average_salary' : avg_salary
        }
    return statistics

def count_avg_language_salary_hh (response):
    avg_salaries = []
    for item in response:
        if not item['salary']['currency'] == 'RUR':
            continue
        avg_vacancy_salary = count_avg_position_salary_hh (item)
        avg_salaries.append(avg_vacancy_salary)
    processed_vacansies = len(avg_salaries)
    if processed_vacansies:
        avg_language_salary = int(sum(avg_salaries) / processed_vacansies)
    else:
        avg_language_salary = 0
    language_stats = [processed_vacansies, avg_language_salary]
    return language_stats
        
def count_avg_position_salary_hh (vacancy):
    start = vacancy['salary']['from']
    end = vacancy['salary']['to']
    if not start:
        avg_salary = end * 0.8
    elif not end:
        avg_salary = start * 1.2
    else:
        avg_salary = (end + start) / 2
    return avg_salary
   
def get_sj_vacancies(params):
    vacancies = []
    page = 0
    more = True
    
    while more:
        params['page'] = page
        response = requests.get(SJ_URL, headers = sj_headers, params=params)
        response.raise_for_status()
        answer = response.json()
        for vacancy in answer ['objects']:
            vacancies.append(vacancy)
        page += 1
        more = answer['more']
    return vacancies

def count_avg_language_salary_sj (vacancy):
    start = vacancy ['payment_from']
    end = vacancy ['payment_to']
    if not end:
        avg_salary = start * 1.2
    elif not start:
        avg_salary = end * 0.8
    else:
        avg_salary = (start + end) / 2
    return avg_salary

def get_salary_statistics_sj (languages_list):
    sj_statistics = {}
    for language in languages_list:
        sj_params = {
            'catalogues' : 48,
            'town' : get_city_id_sj (city_name),
            'period' : 7,
            'keywords[0][srws]' : 1,
            'keywords[0][keys]' : f'{language}'
            }
        sj_statistics [f'{language}'] = {}
        response = get_sj_vacancies(sj_params)
        total_vacancies = len(response)
        processed_vacancies = []
        for vacancy in response:
            if (vacancy ['payment_from'] or vacancy ['payment_to']) and vacancy ['currency'] == 'rub':
                avg_salary = count_avg_language_salary_sj (vacancy)
                processed_vacancies.append(avg_salary)
            else:
                continue
        total_processed = len (processed_vacancies)
        if total_processed:
            total_avg_salary = sum(processed_vacancies) / total_processed
        else:
            total_avg_salary = 0
    
        sj_statistics [f'{language}']['vacancies_count'] = total_vacancies
        sj_statistics [f'{language}'] ['vacancies_processed'] = total_processed
        sj_statistics [f'{language}'] ['average_salary'] = int(total_avg_salary)
    
    return sj_statistics

def make_terminal_table(dictionary, title):
    table_list = [['Language','Vacancies count','Vacancies processed','Average salary']]
    for key, value in dictionary.items():
        language_list = []
        language_list.append(key)
        for value in value.values():
            language_list.append(value)
        table_list.append(language_list)
    terminal_table = DoubleTable(table_list, title = title)
    return terminal_table.table

if __name__ == '__main__':
    load_dotenv()
    sj_token = os.getenv('SJ_TOKEN')
    sj_headers = {'X-Api-App-Id' : sj_token}

    parser = argparse.ArgumentParser(description='show average salary for different languages developers')
    parser.add_argument('city_name', help='input city name in cirilic from the capital letter')
    args = parser.parse_args()
    city_name = args.city_name

    hh = get_salary_statistics_hh (LANGUAGES)
    sj = get_salary_statistics_sj (LANGUAGES)
    print(make_terminal_table(hh, 'Head Hunter vacancies'))
    print(make_terminal_table(sj, 'Super Job vacancies'))
    

