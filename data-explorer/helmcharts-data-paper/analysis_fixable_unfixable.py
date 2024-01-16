# what are the most common cves among all?
import pickle
import sqlite3
from collections import Counter

DB = 'cve2023.sqlite'
import ast


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
    while row is not None:
        if len(cve_counter) % 1000 == 0:
            print(f'Got {len(cve_counter)} cves')
        data = ast.literal_eval(row[1])
        cves = data.get('cves', {})
        cve_counter.update(cves.keys())
        for cve in cves.keys():
            cve_pkg_id_map[cve] = cves[cve]
        fixable_cves = data.get('fixable_vulnerabilities', [])
        actually_fixable.update(fixable_cves)

        # cve_fixable_counter.update(fixable_cves) Use this when need duplicates
        cve_fixable_counter.update(set(fixable_cves))  # Use this when need no duplicates

        row = cursor.fetchone()
    # print(cve_pkg_id_map)
    print(f'first round: {len(cve_counter)} cves')
    connection.close()
    connection = sqlite3.connect(DB)
    cursor = connection.cursor()
    cursor.execute(f'select * from {table_name}')
    row = cursor.fetchone()

    cve_unfixable_counter = Counter()
    while row is not None:
        data = ast.literal_eval(row[1])

        unfixable_cves = data.get('unfixable_vulnerabilities', [])
        for unfixable_cve in unfixable_cves:
            to_be_removed = []
            if unfixable_cve in actually_fixable:
                # print(f'Actually fixable: {unfixable_cve}')
                to_be_removed.append(unfixable_cve)
            unfixable_cves = remove_values_from_list(unfixable_cves, to_be_removed)
        cve_unfixable_counter.update(unfixable_cves)

        # Get the next row
        row = cursor.fetchone()
    print(f'second round: {len(cve_counter)} cves')
    connection.close()
    # # Persist to file pickle
    # import pickle
    # with open('cve_counter.pickle', 'wb') as f:
    #
    # Print the most common CVEs

    with open('counters.pickle', 'wb') as f:
        pickle.dump((cve_counter, cve_fixable_counter, cve_unfixable_counter, cve_pkg_id_map), f)
    print(f'From {len(cve_counter)} cves')
    for cve, count in cve_counter.most_common(n=100):
        print(f'{cve}: {count} - {cve_pkg_id_map[cve]["severity"]}')
        print(f'type of package impacted by {cve}: {cve_pkg_id_map[cve]["pkg_info"]}')
    print('-------FIXABLE--------------')

    print(f'From {len(cve_fixable_counter)} fixable cves')
    for cve, count in cve_fixable_counter.most_common(n=100):
        print(f'{cve}: {count} - {cve_pkg_id_map[cve]["severity"]}')
        print(f'type of package impacted by {cve}: {cve_pkg_id_map[cve]["pkg_info"]}')

    quit()
    print('--------UNFIXABLE-------------')
    print(f'From {len(cve_unfixable_counter)} unfixable cves')
    for cve, count in cve_unfixable_counter.most_common(n=100):
        print(f'{cve}: {count} - {cve_pkg_id_map[cve]["severity"]}')
        print(f'type of package impacted by {cve}: {cve_pkg_id_map[cve]["pkg_info"]}')

    print('---------------------')
    # a set of all impacted packages
    all_impacted_packages = set()
    for cve in cve_pkg_id_map.keys():
        all_impacted_packages.add(cve_pkg_id_map[cve]['pkg_info'].split(' || ')[1])
    # print(f'All impacted packages: \n {(all_impacted_packages)}')


if __name__ == '__main__':
    read_db('OperatorHubHelmChartsCVEReportsLatestOnlyMetrics')
    with open('counters_with_dup.pickle', 'rb') as f:
        cve_counter, cve_fixable_counter, cve_unfixable_counter, cve_pkg_id_map = pickle.load(f)
    print(f'From {len(cve_fixable_counter)} fixable cves')

    with open('counters.pickle', 'rb') as f:
        cve_counter1, cve_fixable_counter1, cve_unfixable_counter1, cve_pkg_id_map1 = pickle.load(f)

    print(f'From {len(cve_fixable_counter1)} fixable cves')
    print(cve_fixable_counter1)
    counter = 0
    for cve in cve_fixable_counter1.keys():
        if cve_fixable_counter1[cve] > 1:
            counter += 1
    print(counter)
