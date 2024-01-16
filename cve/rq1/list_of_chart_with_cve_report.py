import ast
import pickle

with open('../../data-explorer/helmcharts-data-paper/artifacthub_landscape_may2023.pickle', 'rb') as f:
    official_landscape = pickle.load(f)

print(f'From {len(official_landscape)} overall helm charts')
print('---------------------')
# get all package ids
all_official_pkgs = set()
for package in official_landscape:
    all_official_pkgs.add(package['package_id'])

import sqlite3

# COunter for official with a security report

DB = '../cve2023.sqlite'

connection = sqlite3.connect(DB)
cursor = connection.cursor()
cursor.execute(f'select * from OperatorHubHelmChartsCVEReportsLatestOnly')
row = cursor.fetchone()
with_cve = []
without_cve = []
while row is not None:
    data = '-'.join(row[0].split('-')[0:5])

    if data in all_official_pkgs and row[2] != '{}':
        with_cve.append(data)
    else:
        without_cve.append(data)
    row = cursor.fetchone()

print(f'official with cve: {len(set(with_cve))}')
with open('overall_with_report.pickle', 'wb') as f:
    pickle.dump(with_cve, f)
with open('overall_without_report.pickle', 'wb') as f:
    pickle.dump(without_cve, f)
connection.close()
