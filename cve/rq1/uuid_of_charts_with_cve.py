# what are the most common cves among all?
import pickle
import sqlite3

DB = '../cve2023.sqlite'


def read_db(table_name: str):
    connection = sqlite3.connect(DB)
    cursor = connection.cursor()
    cursor.execute(f'select * from {table_name}')
    row = cursor.fetchone()

    uuids = []
    while row is not None:
        uuid = row[0]
        uuids.append(uuid)
        row = cursor.fetchone()
    with open('uuid_that_has_cve.pickle', 'wb') as f:
        pickle.dump(uuids, f)


if __name__ == '__main__':
    read_db('OperatorHubHelmChartsCVEReportsLatestOnlyMetrics')
