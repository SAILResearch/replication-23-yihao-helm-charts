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
    for offset in tqdm(range(0, 230, 60)):  # number of helm charts as of 2023
        print(f'Working on offset {offset}')
        artifacthub_url = f'https://artifacthub.io/api/v1/packages/search?kind=0&official=true&facets=true&sort=relevance&limit=60&offset={offset}'
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
            with open(f'artifacthub_landscape_may2023_official_backup_offset{offset}_failed.pickle', 'wb') as f:
                print(f'Writing to pickle file for {len(landscape)} helm charts')
                pickle.dump(landscape, f)
            continue
        landscape.extend(actual_helm_to_scrape)  # noqa
        print(f'Number of valid helm charts in batch {len(landscape)}')

        time.sleep(random.randint(1, 5))

    with open('artifacthub_landscape_may2023_official.pickle', 'wb') as f:
        print(f'Writing to pickle file for {len(landscape)} helm charts')
        pickle.dump(landscape, f)
    return landscape


if __name__ == '__main__':
    # helm_landscape_to_scrape = get_helm_landscape()
    # persist_to_sqlite(file_name='artifacthub_landscape_may2023.pickle')
    # check_missing()
    with open('artifacthub_landscape_may2023_official.pickle', 'rb') as f:
        helm_landscape_to_scrape = pickle.load(f)
        # persist_to_sqlite(file_name='artifacthub_landscape_may2023.pickle')
        print('loaded pickle')
        print(len(helm_landscape_to_scrape))
        categories_mapping = {
            '1': 'AI/ML',
            '2': 'Database',
            '3': 'Integration',
            '4': 'Monitoring',
            '5': 'Networking',
            '6': 'Security',
            '7': 'Storage',
            '8': 'Streaming',
            'None': 'MISC'
        }
        cve_yes = 0
        total = len(helm_landscape_to_scrape)
        for helm in helm_landscape_to_scrape:
            print(f'version: {helm["version"]}')
            # print(f'repository: {helm["repository"]}')
            print(helm['name'])
            category = categories_mapping[str(helm['category']) if 'category' in helm else 'None']
            # Check if has CVE report
            if 'security_report_summary' in helm:
                cve_yes += 1
            else:
                ...
        print(f'Number of helm charts with CVE: {cve_yes}, total: {total}, percentage: {cve_yes / total}')
    # print(operator_dict)
    # persist_to_pickle(operator_dict)
