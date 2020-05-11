## Average salary statistics
This project counts average salary for different programming languages developers, devopses and data science specialists in different cities or regions.

#### Dependences
You need Python3 interpreter to use this script. All needed dependences are included in requirements.txt file. Use 
```
pip install -r requirements.txt
``` 
to install them (use `pip3` instead `pip`  if you have both python2 and python3 versions).

#### Usage
Run the script  and give it the name of city or region as an argument (only cirillic symbols)
```
python avg_salary_stat.py Москва
```
use `python3` instead `python`  if you have both python2 and python3 versions
As a result you will get two tables. The first one will show you average salary statistics according to hh.ru resource for the last 30 days. And the second one will show you the same statistics according to superjob.ru for the last 7 days. This script processes vacancies with specified salary in RUR currency.

#### Purpose of project
This script was performed as a part of API web-services cource by [Devman](https://dvmn.org/modules)
