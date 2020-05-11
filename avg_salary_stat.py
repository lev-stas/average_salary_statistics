import requests
from terminaltables import DoubleTable
from dotenv import load_dotenv
import argparse
import os


LANGUAGES = [
    'C',
    'C++',
    'C#',
    'Python',
    'Java',
    'Javascript',
    'Ruby',
    'Scala',
    'Go',
    '1C',
    'PHP',
    'DevOps',
    'Data Analyst',
    'Data Scientist'
    ]


def get_city_id_hh(url, city_name):
    city_response = requests.get(url)
    locations = city_response.json()
    for country in locations:
        if city_name in country.values():
            return country['id']
        for region in country['areas']:
            if city_name in region.values():
                return region['id']
            for city in region['areas']:
                if city_name in city.values():
                    return city['id']


def get_city_id_sj(url, headers, city_name):
    city_response = requests.get(url, headers=headers)
    locations = city_response.json()
    for country in locations:
        if 'title' not in country.keys():
            continue
        for city in country['towns']:
            if city_name in city.values():
                return city['id']
            if 'regions' not in country.keys():
                continue
            for region in country['regions']:
                if city_name == region['title']:
                    return region['id']
                for town in region['towns']:
                    if city_name in town.values():
                        return town['id']


def get_hh_vacancies(url, params):

    vacancies = []
    page = 0
    pages = 1

    while page < pages:
        params['page'] = page
        response = requests.get(url, params=params)
        response.raise_for_status()
        answer = response.json()
        for item in answer['items']:
            vacancies.append(item)
        page += 1
        pages = answer['pages']
    return vacancies


def get_salary_statistics_hh(vacancy_url, areas_url, languages):
    statistics = {}
    for language in languages:
        request_params = {
            'text': language,
            'area': get_city_id_hh(areas_url, city_name),
            'period': 30,
            'only_with_salary': True
        }

        answer = get_hh_vacancies(vacancy_url, request_params)
        number_and_avg_salary = count_avg_language_salary_hh(answer)
        vacancies_count = len(answer)
        vacancies_processed = number_and_avg_salary[0]
        avg_salary = number_and_avg_salary[1]
        statistics[language] = {
            'vacancies_count': vacancies_count,
            'vacancies_processed': vacancies_processed,
            'average_salary': avg_salary
        }
    return statistics


def count_avg_language_salary_hh(response):
    avg_salaries = []
    for item in response:
        if not item['salary']['currency'] == 'RUR':
            continue
        salary_from = item['salary']['from']
        salary_to = item['salary']['to']
        avg_vacancy_salary = count_avg_salary(salary_from, salary_to)
        avg_salaries.append(avg_vacancy_salary)
    processed_vacansies = len(avg_salaries)
    if processed_vacansies:
        avg_language_salary = int(sum(avg_salaries) / processed_vacansies)
    else:
        avg_language_salary = 0
    language_stats = [processed_vacansies, avg_language_salary]
    return language_stats


def count_avg_salary(start, end):
    if not start:
        avg_salary = end * 0.8
    elif not end:
        avg_salary = start * 1.2
    else:
        avg_salary = (end + start) / 2
    return avg_salary


def get_sj_vacancies(url, headers, params):
    vacancies = []
    page = 0
    more = True

    while more:
        params['page'] = page
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        answer = response.json()
        for vacancy in answer['objects']:
            vacancies.append(vacancy)
        page += 1
        more = answer['more']
    return vacancies


def get_salary_statistics_sj(vacancy_url, areas_url, headers, languages):
    sj_statistics = {}
    for language in languages:
        sj_params = {
            'catalogues': 48,
            'town': get_city_id_sj(areas_url, headers, city_name),
            'period': 7,
            'keywords[0][srws]': 1,
            'keywords[0][keys]': language
            }
        sj_statistics[language] = {}
        response = get_sj_vacancies(vacancy_url, headers, sj_params)
        total_vacancies = len(response)
        processed_vacancies = []
        for vacancy in response:
            if (vacancy['payment_from'] or vacancy['payment_to']) and vacancy['currency'] == 'rub':
                salary_from = vacancy['payment_from']
                salary_to = vacancy['payment_to']
                avg_salary = count_avg_salary(salary_from, salary_to)
                processed_vacancies.append(avg_salary)
            else:
                continue
        total_processed = len(processed_vacancies)
        if total_processed:
            total_avg_salary = sum(processed_vacancies) / total_processed
        else:
            total_avg_salary = 0

        sj_statistics[language] = {
            'vacancies_count': total_vacancies,
            'vacancies_processed': total_processed,
            'average_salary': int(total_avg_salary)
        }

    return sj_statistics


def make_terminal_table(statistics, title):
    table = [['Language', 'Vacancies count', 'Vacancies processed', 'Average salary']]
    for language, category in statistics.items():
        languages = []
        languages.append(language)
        for count in category.values():
            languages.append(count)
        table.append(languages)
    terminal_table = DoubleTable(table, title=title)
    return terminal_table.table

if __name__ == '__main__':
    load_dotenv()
    sj_token = os.getenv('SJ_TOKEN')
    sj_headers = {'X-Api-App-Id': sj_token}

    hh_vacancy_url = 'https://api.hh.ru/vacancies/'
    sj_vacancy_url = 'https://api.superjob.ru/2.30/vacancies'
    hh_areas_url = 'https://api.hh.ru/areas'
    sj_areas_url = 'https://api.superjob.ru/2.30/regions/combined'

    parser = argparse.ArgumentParser(description='show average salary for different languages developers')
    parser.add_argument('city_name', help='input city name in cirilic from the capital letter')
    args = parser.parse_args()
    city_name = args.city_name

    hh = get_salary_statistics_hh(hh_vacancy_url, hh_areas_url, LANGUAGES)
    sj = get_salary_statistics_sj(sj_vacancy_url, sj_areas_url, sj_headers, LANGUAGES)
    print(make_terminal_table(hh, 'Head Hunter vacancies'))
    print(make_terminal_table(sj, 'Super Job vacancies'))

