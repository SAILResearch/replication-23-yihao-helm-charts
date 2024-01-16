import ast
import sqlite3
import statistics

DB = '../cve2023.sqlite'

conn = sqlite3.connect(DB)

cursor = conn.cursor()

cursor.execute('SELECT * FROM main.OperatorHubHelmCharts')

releases_total = []
while True:
    res = cursor.fetchone()
    if not res:
        break
    # uuid = '-'.join(res[0].split('-')[:5])
    releases = ast.literal_eval(res[5])
    releases_total.append(len(releases))

print(statistics.median(releases_total))
