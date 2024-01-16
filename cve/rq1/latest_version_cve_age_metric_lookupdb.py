# what are the most common cves among all?
import pickle
import sqlite3
from collections import Counter

DB = '../cve2023.sqlite'
import json, ast


def remove_values_from_list(the_list, val):
    for v in val:
        the_list = [value for value in the_list if value != v]
    return the_list


def read_db(table_name: str):
    connection = sqlite3.connect(DB)
    cursor = connection.cursor()
    cursor.execute(f'select * from {table_name}')
    row = cursor.fetchone()
    # row[1] is the json containing the metrics like below
    # Initialize a counter for CVEs
    cve_counter = Counter()
    cve_fixable_counter = Counter()
    actually_fixable = set()
    cve_pkg_id_map = {}
    helm_to_fixable_cves = {}
    with open('uuid_release_age_tmp.pickle', 'rb') as f:
        lookup_table = pickle.load(f)
    while row is not None:
        data = ast.literal_eval(row[1])
        true_uuid = '-'.join(row[0].split('-')[:5])
        # # For this uuid lookup the release date
        # if true_uuid in lookup_table:
        #     print(lookup_table[true_uuid])
        # else:
        #     row = cursor.fetchone()
        #     continue # There are extremely rare cases where the helm chart gets deleted by the author
        fixable_cves = data.get('fixable_vulnerabilities', [])
        # in this anlysis we do not consider the cves become fixable after release
        actually_fixable.update(fixable_cves)  # This is for lookup later
        helm_to_fixable_cves[true_uuid] = fixable_cves

        row = cursor.fetchone()
    # print(cve_pkg_id_map)
    print(f'first round: {len(cve_counter)} cves')
    connection.close()
    # with open('actually_fixables.pickle', 'wb') as f:
    #     pickle.dump(actually_fixable, f)
    #
    with open('helm_to_fixable_cves.pickle', 'wb') as f:
        pickle.dump(helm_to_fixable_cves, f)


if __name__ == '__main__':
    read_db('OperatorHubHelmChartsCVEReportsLatestOnlyMetrics')
