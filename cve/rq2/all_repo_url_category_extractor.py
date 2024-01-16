import json
import pickle
import sqlite3

header = {'Accept': 'application/json',
          'X-API-KEY-ID': '<api_id1>',
          'X-API-KEY-SECRET': '<api_secret1>='
          }

header_gmail = {'Accept': 'application/json',
                'X-API-KEY-ID': '<api_id2>',
                'X-API-KEY-SECRET': '<api_secret2>'
                }

with open('../../data-explorer/helmcharts-data-paper/artifacthub_landscape_may2023.pickle', 'rb') as f:
    official_landscape = pickle.load(f)

DB = '../cve2023.sqlite'
connection = sqlite3.connect(DB)
cursor = connection.cursor()
cursor.execute('SELECT * FROM OperatorHubHelmCharts')

print(len(official_landscape))
# get all package ids
all_official_pkgs = []  # ordered set

for package in official_landscape:
    all_official_pkgs.append(package['package_id'])

for package_id in all_official_pkgs:
    print(package_id)
    cursor.execute('SELECT * FROM main.OperatorHubHelmCharts WHERE uuid=?', (package_id,))
    res = cursor.fetchone()
    additional_info_field = json.loads(res[4])
    print(additional_info_field['repository']['name'], additional_info_field['normalized_name'])
    repo_name = additional_info_field['repository']['name']
    normalized_name = additional_info_field['normalized_name']
    officiality = additional_info_field['official'] if 'official' in additional_info_field else False
    category = additional_info_field['category'] if 'category' in additional_info_field else -1
    print((repo_name, normalized_name, officiality, category))
quit()

DB = 'cve2023.sqlite'
with open('../../data-explorer/helmcharts-data-paper/artifacthub_landscape_may2023.pickle', 'rb') as f:
    overall_landscape = pickle.load(f)

with open('../rq1/overall_with_report.pickle', 'rb') as f:
    over_all_with_report = pickle.load(f)

with open('../rq1/overall_without_report.pickle', 'rb') as f:
    over_all_without_report = pickle.load(f)
candidates = []
candidates_without_report = []
official_candidates_with_report = []
for helm in overall_landscape:
    package_id = helm['package_id']
    if package_id in all_official_pkgs and package_id in over_all_with_report:
        official_candidates_with_report.append(helm)
    elif package_id in over_all_with_report:
        unofficial_candidates_with_report.append(helm)
    else:
        candidates_without_report.append(helm)
print(len(candidates), len(official_candidates_with_report))

print(f'official: {len(official_candidates)} unofficial: {len(candidates)}')

api = "https://artifacthub.io/api/v1/packages/helm/{repoName}/{packageName}"
official_links = []
unofficial_links = []


# for candidate in official_candidates:
#     time.sleep(0.5)
#     res = requests.get(api.format(repoName=candidate['repository']['name'], packageName=candidate['normalized_name']))
#     if 'links' in res.json():
#         category = res.json()['category'] if 'category' in res.json() else -1
#         print(res.json()['links'])
#         tupled = (category, res.json()['links'])  # left side is category
#         official_links.append(tupled)
def save_links_to_pickle(name, links):
    with open(name, 'wb') as f:
        pickle.dump(links, f)


# # save_links_to_pickle('official_links_with_category.pickle', official_links)
# with open('unofficial_with_category_checkpoint_BEFORE3629.pickle', 'rb') as f:
#     unofficial_links =  pickle.load(f)
# for i, candidate in enumerate(candidates):
#     if i<=3629:
#         continue
#     try:
#         time.sleep(1)
#         res = requests.get(api.format(repoName=candidate['repository']['name'], packageName=candidate['normalized_name']),
#                            headers=header_gmail if i % 2 == 0 else header)
#         if 'links' in res.json():
#             category = res.json()['category'] if 'category' in res.json() else -1
#             tupled = (category, res.json()['links'])  # left side is category
#             unofficial_links.append(tupled)
#             print(tupled)
#             print(f'got {i}, progress: {len(unofficial_links)}/{i} unofficial, category: {category}')
#         print(f'working on {i}, progress: {len(unofficial_links)}/{i} unofficial \n'
#               f"{api.format(repoName=candidate['repository']['name'], packageName=candidate['normalized_name'])}")
#
#     except Exception as e:
#         print(e)
#         save_links_to_pickle(f'unofficial_with_category_checkpoint_BEFORE{i}.pickle', unofficial_links)
#         print('stopped at: ', i)
#         quit()
#     except KeyboardInterrupt:
#         save_links_to_pickle(f'unofficial_with_category_checkpoint_BEFORE{i}.pickle', unofficial_links)
#         print('stopped at: ', i)
#         quit()
#
#
# # # save_links_to_pickle('official_links.pickle', official_links)
# save_links_to_pickle('unofficial_links_with_category.pickle', unofficial_links)


with open('unofficial_links_with_category.pickle', 'rb') as f:
    official_links = pickle.load(f)

import re


def extract_github_org_repo(urls):
    # Regular expression to match GitHub repository URLs
    github_url_pattern = re.compile(r'https://github\.com/([^/]+)/([^/]+)')

    org_repo_pairs = []

    for url_unit in urls:
        category = url_unit[0]
        url_unit = url_unit[1]
        for url_small_unit in url_unit:
            url = url_small_unit['url']
            match = github_url_pattern.match(url)
            if match:
                org, repo = match.groups()
                tupled = (category, f'{org}/{repo}')
                org_repo_pairs.append(tupled)

    return org_repo_pairs


extracted_official = extract_github_org_repo(official_links)
print(f'Count of official github org repo pairs: {len(extracted_official)}, {len(set(extracted_official))}')

headers = {
    "Authorization": f"bearer <your_github_token_with_read_permission>",  # 202312
    "Accept": "application/vnd.github.v3+json"
}

import requests
import time
import pickle


def fetch_github(extracted_pairs, generate_api_url, headers, output_filename, print_progress=True):
    non_empty = {}
    for idx, org_repo_pairs in enumerate(set(extracted_pairs)):
        time.sleep(0.25)
        try:
            category, org_repo_pair = org_repo_pairs
            api_url = generate_api_url(org_repo_pair)

            if print_progress:
                print(f'Working on category - {category} {api_url}, progress: {len(non_empty.keys())}/{idx} unofficial')

            response = requests.get(api_url, headers=headers)
            res = response.json()
            # if "name" in res and res["name"] == "SECURITY.md":
            #     non_empty[org_repo_pair] = (category, res)
            if res not in [[], {}, None]:
                if 'message' in res and res['message'] == 'Not Found':
                    continue
                non_empty[org_repo_pair] = (category, res)
            # for release in res:
            #     #if 'body' in release and ('cve' in release['body'].lower() or 'vulnerab' in release['body'].lower()):
            #         non_empty[org_repo_pair] = (category, res)
            #         break
        except Exception as e:
            if print_progress:
                print(e)
            with open(f'{output_filename}-{idx}.pickle', 'wb') as f:
                pickle.dump(non_empty, f)
            quit()

    if print_progress:
        print(f'Count of official GitHub org repo pairs with security advisories: {len(non_empty)}')

    with open(f'{output_filename}.pickle', 'wb') as f:
        pickle.dump(non_empty, f)


# Example usage:
generate_api_url = lambda org_repo_pair: f'https://api.github.com/repos/{org_repo_pair}/releases?per_page=100'
# f'https://api.github.com/repos/{org_repo_pair}/contents/README.md'
# f"https://api.github.com/repos/{org_repo_pair}/security-advisories"
#     readme = f'https://api.github.com/repos/{org_repo_pairs}/contents/README.md'
# fetch_github(extracted_official, generate_api_url, headers, output_filename='unofficial-security-md')
# fetch_github(extracted_official, generate_api_url, headers, output_filename='official-releases')

mapping_total = {
    '1': 0,
    '2': 0,
    '3': 0,
    '4': 0,
    '5': 0,
    '6': 0,
    '7': 0,
    '8': 0,
    '-1': 0,  # This is an estimation of baseline since category is a mixture of all categories
}
for link in extracted_official:
    print(link)
    if str(link[0]) in mapping_total:
        mapping_total[str(link[0])] += 1
print(mapping_total)
print(f'got {len(extracted_official)} official links')
with open('unofficial-security-md.pickle', 'rb') as f:
    unofficial_security_advisories = pickle.load(f)
    print(len(unofficial_security_advisories.keys()))
    categories_mapping = {
        '1': 'AI/ML',
        '2': 'Database',
        '3': 'Integration',
        '4': 'Monitoring',
        '5': 'Networking',
        '6': 'Security',
        '7': 'Storage',
        '8': 'Streaming',
        '-1': 'MISC',  # This is an estimation of baseline since category is a mixture of all categories
        'BASELINE': 'Aggregated'
    }
    categories_mapping = {
        '1': 0,
        '2': 0,
        '3': 0,
        '4': 0,
        '5': 0,
        '6': 0,
        '7': 0,
        '8': 0,
        '-1': 0,  # This is an estimation of baseline since category is a mixture of all categories
    }
    for key in unofficial_security_advisories.keys():
        if str(unofficial_security_advisories[key][0]) in categories_mapping:
            categories_mapping[str(unofficial_security_advisories[key][0])] += 1
    print(categories_mapping)

print(f'percentage of security md in each category: diving two dicts above')
dic_new = {k: categories_mapping[k] / mapping_total[k] for k in mapping_total.keys() & categories_mapping}
print(dic_new)
