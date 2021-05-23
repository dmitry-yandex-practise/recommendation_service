from datetime import datetime
from random import randint
import csv
from uuid import uuid4
from pprint import pprint

film_work_list = None
users_list = None
persons_list = None

film_work_views_list = []
persons_views_list = []

YEAR = 2021
MONTH = 5
DAY = 23
DAY_RANGE_START = -5
DAY_RANGE_END = 5


with open('1000_film_works.csv', newline='') as csvfile:
    file_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    film_work_list = list(file_reader)

with open('1000_users.csv', newline='') as csvfile:
    file_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    users_list = list(file_reader)

with open('1000_persons.csv', newline='') as csvfile:
    file_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    persons_list = list(file_reader)

for idx, film_work in enumerate(film_work_list):
    for number in range(idx):
        date = datetime(year=YEAR,
                        month=MONTH,
                        day=DAY + randint(DAY_RANGE_START, DAY_RANGE_END)).strftime('%Y-%m-%d')
        film_work_views_list.append(
            [str(uuid4()),
             film_work_list[idx][0],
             users_list[randint(0, len(users_list)-1)][0],
             date
            ]
        )


for idx, person in enumerate(persons_list):
    for number in range(idx):
        date = datetime(year=YEAR,
                        month=MONTH,
                        day=DAY + randint(DAY_RANGE_START, DAY_RANGE_END)).strftime('%Y-%m-%d')
        persons_views_list.append(
            [str(uuid4()),
             persons_list[idx][0],
             users_list[randint(0, len(users_list)-1)][0],
             date
            ]
        )


with open('film_work_views.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for item in film_work_views_list:
        spamwriter.writerow(item)


with open('person_views.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for item in persons_views_list:
        spamwriter.writerow(item)

# pprint(film_work_views_list)



"""
for item in range(5):
    print(datetime(year=YEAR,
                   month=MONTH,
                   day=DAY + randint(DAY_RANGE_START, DAY_RANGE_END),
                   hour=randint(0,23),
                   minute=randint(0,59),
                   second=randint(0,59)))
"""
