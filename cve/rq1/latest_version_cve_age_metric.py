# This is a metric to show how much time between fixable cves and a release

# This file produces an artifact <uuid->release_age> mapping pickle file

# average cve response time << google scholar this

import json
import pickle
import random
import sqlite3
import time
from pprint import pprint
import feedparser
import requests
from tqdm import tqdm

header = {'Accept': 'application/json',
          'X-API-KEY-ID': '<api_id1>',
          'X-API-KEY-SECRET': '<api_secret1>='
          }

header_gmail = {'Accept': 'application/json',
                'X-API-KEY-ID': '<api_id2>',
                'X-API-KEY-SECRET': '<api_secret2>'
                }

import ast

DB = '../cve2023.sqlite'
connection = sqlite3.connect(DB)
cursor = connection.cursor()
lookup_table = {}

# error restore
with open('uuid_release_age_tmp.pickle', 'rb') as f:
    lookup_table = pickle.load(f)


def get_version_detail_for_age_metric(helm_landscape_to_scrape):
    row = 0
    print('total: ', len(helm_landscape_to_scrape))
    print('already done ', len(lookup_table))
    for uuid in helm_landscape_to_scrape:
        try:
            true_uuid = '-'.join(uuid.split('-')[:5])
            helm_id = true_uuid
            if helm_id in lookup_table:
                row += 1
                continue
            else:
                time.sleep(0.5)

            row += 1
            print(f'Processing {row}')
            cursor.execute('SELECT * FROM main.OperatorHubHelmCharts WHERE uuid=?', (helm_id,))
            res = cursor.fetchone()
            latest_version = ast.literal_eval(res[5])[0]  # The latest version is the first element in the list
            print(latest_version)
            org_name = res[3].split('/')[0]
            helm_name = res[3].split('/')[1]

            version_detail_api = 'https://artifacthub.io/api/v1/packages/helm/{repoName}/{packageName}/{version}'
            if row % 2 == 0:
                headers = header
            else:
                headers = header_gmail
            res = requests.get(
                version_detail_api.format(repoName=org_name, packageName=helm_name, version=latest_version),
                headers=headers)
            print(version_detail_api.format(repoName=org_name, packageName=helm_name, version=latest_version))
            if 'available_versions' not in res.json():
                print('no available_versions')
                lookup_table[helm_id] = None
                continue
            available_versions = res.json()['available_versions']
            timestamp_of_local_latest_version = None
            if_ever_contains_security_updates = False
            for version_dict in available_versions:
                if version_dict['version'] == latest_version:
                    timestamp_of_local_latest_version = version_dict['ts']
                if 'contains_security_updates' in version_dict and version_dict['contains_security_updates']:
                    if_ever_contains_security_updates = True
            print(timestamp_of_local_latest_version, latest_version)
            if timestamp_of_local_latest_version:
                print(
                    f'human readable time: {time.strftime("%Y-%m-%d", time.localtime(timestamp_of_local_latest_version))}')
            lookup_table[helm_id] = (
                timestamp_of_local_latest_version, latest_version, if_ever_contains_security_updates)
        except Exception as e:
            print(f'Error: {e}')
            with open('uuid_release_age_tmp.pickle', 'wb') as f:
                pickle.dump(lookup_table, f)
            quit()
        except KeyboardInterrupt:
            with open('uuid_release_age_tmp.pickle', 'wb') as f:
                pickle.dump(lookup_table, f)
            quit()

    with open('uuid_release_age.pickle', 'wb') as f:
        pickle.dump(lookup_table, f)


if __name__ == '__main__':
    # helm_landscape_to_scrape = get_helm_landscape()
    # persist_to_sqlite(file_name='artifacthub_landscape_may2023.pickle')
    # check_missing()
    with open('uuid_that_has_cve.pickle', 'rb') as f:
        helm_landscape_to_scrape = pickle.load(f)
        # persist_to_sqlite(file_name='artifacthub_landscape_may2023.pickle')
        get_version_detail_for_age_metric(helm_landscape_to_scrape)
    # print(operator_dict)
    # persist_to_pickle(operator_dict)
