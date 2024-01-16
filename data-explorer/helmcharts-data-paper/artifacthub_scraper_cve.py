import json
import pickle
import random
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


def get_helm_landscape(dry_run: bool = False):
    landscape = []
    for offset in tqdm(range(0, 11038, 60)):  # number of helm charts as of 2023
        print(f'Working on offset {offset}')
        artifacthub_url = f'https://artifacthub.io/api/v1/packages/search?kind=0&facets=true&sort=relevance&limit=60&offset={offset}'
        response = requests.get(artifacthub_url)
        data = json.dumps(response.json(), indent=4)
        page_content = json.loads(data)
        actual_helm_to_scrape = []
        try:
            for package in page_content['packages']:
                actual_helm_to_scrape.append(package)
        except KeyError as e:
            print(f'theres a bug in the scraper/api, check!, offset: {offset}')
            # emergency save
            with open(f'artifacthub_landscape_may2023_backup_offset{offset}_failed.pickle', 'wb') as f:
                print(f'Writing to pickle file for {len(landscape)} helm charts')
                pickle.dump(landscape, f)
            continue
        landscape.extend(actual_helm_to_scrape)  # noqa
        print(f'Number of valid helm charts in batch {len(landscape)}')

        time.sleep(random.randint(1, 5))

    with open('artifacthub_landscape_may2023.pickle', 'wb') as f:
        print(f'Writing to pickle file for {len(landscape)} helm charts')
        pickle.dump(landscape, f)
    return landscape


from db_store import persist_cve, persist_package, init_db, update_package, update_package_name, search_uuid

import ast


def get_cves(helm_landscape_to_scrape: list, start_from: tuple[int, int] = (0, 0), restart: bool = False):  # noqa
    """

    :param helm_landscape_to_scrape: full list of helm charts to scrape
    :param start_from: select the index of the helm chart to start scraping from
    :return: None
    """
    if restart:
        # also disabled in schema.sql, uncomment there to enable
        init_db()  # recreate db if needed
    helm_counter = 0
    flag = True
    for helm in helm_landscape_to_scrape:
        if helm_counter < start_from[0]:
            helm_counter += 1
            continue
        print('######################')
        cve_report_counter = 0
        org_name = helm['repository']['name']
        helm_name = helm['normalized_name']
        helm_id = helm['package_id']
        # helm_versions = get_helm_versions(org_name, helm_name)
        # its already in table OperatorHubHelmCharts so we use lookup not request
        got = search_uuid(uuid=helm_id, table_name='OperatorHubHelmCharts')
        if not got:
            print(f'no uuid {helm_id} in OperatorHubHelmCharts')
            raise
        else:
            helm_versions = ast.literal_eval(got[5])
            print(f'got {len(helm_versions)} versions for {helm_id}')
            print('latest version is', helm_versions[0])

        print(
            f'\nScraping started for {org_name}/{helm_name} latest-{helm_versions[0]}: with {len(helm_versions)} versions, '
            f'Helm processed count: {helm_counter}')
        skip_all = False
        # for helm_version in tqdm([helm_versions[0]]):
        for helm_version in [helm_versions[0]]:  # latest only
            if helm_counter == start_from[0] and cve_report_counter < start_from[1]:
                cve_report_counter += 1
                continue
            elif flag and cve_report_counter >= start_from[1]:
                flag = False
                print(
                    f'restarting from helm count {helm_counter} {helm_name} and cve report count {cve_report_counter} version {helm_version}')
            if not skip_all:
                cve_report = get_cve_report(helm_id, helm_version)
                time.sleep(random.randint(1, 3))
            else:
                cve_report = {}
            # print(cve_report)
            if cve_report == {} or cve_report is None:  # null or {}
                print(f'no cve report for {helm_id} {helm_version}')
                cve_report_counter += 1
                persist_cve((f'{helm_id}-{helm_version}', helm_name, json.dumps({}), helm_version),
                            'OperatorHubHelmChartsCVEReportsLatestOnly')
                skip_all = True
                # keep going and see if all versions are empty
                break
            persist_cve((f'{helm_id}-{helm_version}', helm_name, json.dumps(cve_report), helm_version),
                        'OperatorHubHelmChartsCVEReportsLatestOnly')
            cve_report_counter += 1
        helm_counter += 1


def get_cve_report(helm_id, helm_version):
    """
    Helper function of get_cves
    :param helm_id:
    :param helm_version:
    :return:
    """
    cve_report_api = f'https://artifacthub.io/api/v1/packages/{helm_id}/{helm_version}/security-report'
    try:
        if random.randint(0, 1) == 1:
            cve_report = requests.get(cve_report_api, headers=header)
            print(f'url requested {cve_report_api} with GitHub api')
        else:
            cve_report = requests.get(cve_report_api, headers=header_gmail)
            print(f'url requested {cve_report_api} with Gmail api')
        if cve_report.content == b'':  # not available
            return {}
        else:
            cve_report = cve_report.json()
    except Exception as e:
        print(f'errored at {helm_id} {helm_version}')
        print(e)
        time.sleep(60)
        return get_cve_report(helm_id, helm_version)
    # pprint(cve_report.json())

    return cve_report


def get_helm_versions(org_name, helm_name):
    """
    Helper function of get_cves
    :param org_name:
    :param helm_name:
    :return:
    """
    # version_api = f'https://artifacthub.io/api/v1/packages/{helm_id}/changelog'
    # versions = requests.get(version_api)
    # pprint(versions.json())  # some packages has no changelog available
    version_rss_api = f'https://artifacthub.io/api/v1/packages/helm/{org_name.lower()}/{helm_name.lower()}/feed/rss'
    if random.randint(0, 1) == 1:
        feed = feedparser.parse(version_rss_api, request_headers=header_gmail)
        print(f'getting rss api {version_rss_api} with Gmail account ')
    else:
        feed = feedparser.parse(version_rss_api, request_headers=header)
        print(f'getting rss api {version_rss_api} with GitHub account')

    feed_entries = feed['entries']
    helm_versions = [entry.title for entry in feed_entries]
    print(f'\nhelm_versions of {helm_name}: {len(helm_versions)}')
    if not helm_versions:
        print(f'no versions for {helm_name}')
        time.sleep(180)
        return get_helm_versions(org_name, helm_name)
    return helm_versions


def persist_to_pickle(data):
    with open('artifacthub_data_may2023.pickle', 'wb') as f:
        pickle.dump(data, f)
    print('Data persisted to pickle file')


def persist_to_sqlite(file_name: str):
    with open(file_name, 'rb') as f:
        from db_store import init_db
        init_db()
        data = pickle.load(f)
        for index, helm in enumerate(data):
            if index < 2222:  # skipper
                continue
            elif index == 2222:
                print(f' {index + 1} {helm["repository"]["name"]}/{helm["normalized_name"]}')
            quit()
            org_name = helm['repository']['name']
            helm_name = helm['normalized_name']
            helm_id = helm['package_id']

            # two duplicates
            # total valid 9382 as of 2022 12
            """
            UNIQUE constraint failed: OperatorHubHelmCharts.uuid
            ('87650315-e31d-41c3-b1f5-1d8c1a8f6201', 'kube-prometheus-stack', 'prometheus-worawutchan', '{"package_id": "87650315-e31d-41c3-b1f5-1d8c1a8f6201", "name": "kube-prometheus-stack", "normalized_name": "kube-prometheus-stack", "logo_image_id": "0503add5-3fce-4b63-bbf3-b9f649512a86", "stars": 1, "description": "kube-prometheus-stack collects Kubernetes manifests, Grafana dashboards, and Prometheus rules combined with documentation and scripts to provide easy to operate end-to-end Kubernetes cluster monitoring with Prometheus using the Prometheus Operator.", "version": "12.8.0", "app_version": "0.44.0", "deprecated": false, "signed": false, "production_organizations_count": 0, "ts": 1607676926, "repository": {"url": "https://worawutchan.github.io/helm-charts", "kind": 0, "name": "prometheus-worawutchan", "official": false, "user_alias": "worawutchan", "display_name": "prometheus-worawutchan", "repository_id": "fd7f4268-c6ec-4196-a94d-3e8af6758127", "scanner_disabled": false, "verified_publisher": false}}')
            UNIQUE constraint failed: OperatorHubHelmCharts.uuid
            ('b2904e15-1624-4f6a-b042-96b412c605f3', 'base', 'nn-co', '{"package_id": "b2904e15-1624-4f6a-b042-96b412c605f3", "name": "base", "normalized_name": "base", "stars": 0, "description": "A Base or general chart for Kubernetes", "version": "0.1.0", "app_version": "1.0.0", "license": "Apache-2.0", "deprecated": false, "signed": false, "security_report_summary": {"low": 95, "high": 16, "medium": 15, "unknown": 0, "critical": 4}, "all_containers_images_whitelisted": false, "production_organizations_count": 0, "ts": 1631181901, "repository": {"url": "https://urbanindo.github.io/99-charts", "kind": 0, "name": "nn-co", "official": false, "display_name": "99 Group", "repository_id": "4f1c5ad0-57f9-4123-966d-94f8c57b47b2", "scanner_disabled": false, "organization_name": "99", "verified_publisher": true, "organization_display_name": "99 Group"}}')
            """
            # update_package_name((helm_name, f'{org_name}/{helm_name}', helm_id), 'OperatorHubHelmCharts')
            available_versions = get_helm_versions(org_name, helm_name)
            time.sleep(random.random())
            persist_package((helm_id, helm_name, org_name, f'{org_name}/{helm_name}', json.dumps(helm),
                             str(available_versions), len(available_versions),
                             f'{helm_id}-{available_versions[0]}'), 'OperatorHubHelmCharts')
            print(f'persisting {helm_name} {helm_id} at Row {index + 1} done.')

            # persist_to_pickle((str(available_versions), len(available_versions), f'{helm_id}-{available_versions[0]}', helm_id),'OperatorHubHelmCharts')


def check_missing():
    # check if a row containing a column is missing
    # if missing, add the column
    # if not missing, do nothing
    import sqlite3
    # Connect to the database
    conn = sqlite3.connect('cve2023.sqlite')
    c = conn.cursor()
    # Execute a SELECT statement to retrieve all rows from the table
    c.execute('SELECT * FROM OperatorHubHelmCharts')
    # Use fetchall() to retrieve all rows as a list of tuples
    rows = c.fetchall()
    with open('artifacthub_landscape_may2023.pickle', 'rb') as f:
        helm_landscape_to_scrape = pickle.load(f)

    # Iterate over the rows and print each column value
    for idx, row in enumerate(rows):
        id = row[0]
        name = row[3]
        helm = helm_landscape_to_scrape[idx]
        org_name = helm['repository']['name']
        helm_name = helm['normalized_name']
        print(f'Dow<{idx + 1}> UUID: {id}, Name: {name}')
        print(f"How<{idx + 1}> UUID: {helm['package_id']}, Name: {org_name}/{helm_name}")
        if idx == 4936:
            break
    # Close the database connection
    conn.close()


if __name__ == '__main__':
    # helm_landscape_to_scrape = get_helm_landscape()
    # persist_to_sqlite(file_name='artifacthub_landscape_may2023.pickle')
    # check_missing()
    with open('artifacthub_landscape_may2023.pickle', 'rb') as f:
        helm_landscape_to_scrape = pickle.load(f)
        # persist_to_sqlite(file_name='artifacthub_landscape_may2023.pickle')
        get_cves(helm_landscape_to_scrape=helm_landscape_to_scrape, start_from=(1323, 0), restart=True)
    # print(operator_dict)
    # persist_to_pickle(operator_dict)
