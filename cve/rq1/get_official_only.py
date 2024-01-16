import ast
import pickle

with open('../../data-explorer/helmcharts-data-paper/artifacthub_landscape_may2023_official.pickle', 'rb') as f:
    official_landscape = pickle.load(f)

print(f'From {len(official_landscape)} official packages')
print('---------------------')
print(official_landscape)

# get all package ids
all_official_pkgs = set()
for package in official_landscape:
    all_official_pkgs.add(package['package_id'])

print(all_official_pkgs)
print(len(all_official_pkgs))

import sqlite3

# Counter for official with a security report

DB = '../cve2023.sqlite'

connection = sqlite3.connect(DB)
cursor = connection.cursor()
cursor.execute(f'select * from OperatorHubHelmChartsCVEReportsLatestOnly')
row = cursor.fetchone()
official_with_cve = 0
while row is not None:
    data = '-'.join(row[0].split('-')[0:5])

    if data in all_official_pkgs and row[2] != '{}':
        print(f'{data} is official')
        official_with_cve += 1
    row = cursor.fetchone()

print(f'official with cve: {official_with_cve}')
connection.close()
