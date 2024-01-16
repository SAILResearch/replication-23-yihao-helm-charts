import pickle
import time

header = {'Accept': 'application/json',
          'X-API-KEY-ID': '<api_id1>',
          'X-API-KEY-SECRET': '<api_secret1>='
          }

header_gmail = {'Accept': 'application/json',
                'X-API-KEY-ID': '<api_id2>',
                'X-API-KEY-SECRET': '<api_secret2>'
                }

with open('../../data-explorer/helmcharts-data-paper/artifacthub_landscape_may2023_official.pickle', 'rb') as f:
    official_landscape = pickle.load(f)

# get all package ids
all_official_pkgs = set()
for package in official_landscape:
    all_official_pkgs.add(package['package_id'])

print(all_official_pkgs)
# print(all_official_pkgs)
import random

random.seed(42)

DB = 'cve2023.sqlite'
with open('../../data-explorer/helmcharts-data-paper/artifacthub_landscape_may2023.pickle', 'rb') as f:
    overall_landscape = pickle.load(f)

candidates = []
official_candidates = []
for helm in overall_landscape:
    package_id = helm['package_id']
    if package_id in all_official_pkgs:
        official_candidates.append(helm)
    else:
        candidates.append(helm)

print(f'official: {len(official_candidates)} unofficial: {len(candidates)}')

import requests

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

# print(official_links)

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

non_empty = {}
for idx, org_repo_pairs in enumerate(set(extracted_official)):
    time.sleep(0.25)
    try:
        category = org_repo_pairs[0]
        org_repo_pairs = org_repo_pairs[1]
        api = f'https://api.github.com/repos/{org_repo_pairs}/security-advisories'

        print(f'working on category - {category} {api}, progress: {len(non_empty.keys())}/{idx} unofficial')
        response = requests.get(api, headers=headers)
        res = response.json()
        if res != {} and res != []:
            non_empty[org_repo_pairs] = (category, res)
    except Exception as e:
        time.sleep(60)
        print(e)
        with open(f'unofficial_org_repo_pairs_with_security_advisories-{idx}.pickle', 'wb') as f:
            pickle.dump(non_empty, f)
print(f'Count of unofficial github org repo pairs with security advisories: {len(non_empty)}')
print(f'full data: {non_empty}')
with open('unofficial_org_repo_pairs_with_security_advisories.pickle', 'wb') as f:
    pickle.dump(non_empty, f)
"""
['https://github.com/PrefectHQ/prefect-helm', 'https://eginnovations.github.io/helm-charts', 'https://github.com/truecharts/charts/tree/master/charts/stable/minetest', 'https://github.com/andrcuns/charts', 'https://github.com/jfrog/charts', 'https://github.com/cosmo-workspace/charts', 'https://github.com/stevehipwell/helm-charts/', 'https://github.com/one-acre-fund/oaf-public-charts/tree/main/charts/metabase', 'https://github.com/adfinis/helm-charts', 'https://github.com/itsmethemojo/helm-hetzner-dyndns', 'https://github.com/paradeum-team/geth-charts', 'https://github.com/kubernetes/charts/tree/master/stable/openvpn', 'https://github.com/VictoriaMetrics/helm-charts', 'https://github.com/k3s-io/helm-controller', 'https://github.com/Aguafrommars/helm/tree/main/charts/theidserver', 'https://github.com/prometheus-community/helm-charts', 'https://github.com/softonic/mysql-backup-chart', 'https://github.com/teutonet/teutonet-helm-charts', 'https://github.com/kubeshop/helm-charts/tree/main/charts', 'https://github.com/prometheus-community/helm-charts', 'https://github.com/snowplow-devops/helm-charts', 'https://github.com/aws/eks-charts', 'https://github.com/startxfr/helm-repository/tree/master/charts/cluster-nexus', 'https://github.com/apache/pulsar-helm-chart', 'https://pages.git.viasat.com/ATG/charts', 'https://github.com/steadybit/helm-charts', 'https://github.com/traefik/traefik-helm-chart', 'https://github.com/jdstone/helm-charts', 'https://github.com/broadinstitute/datarepo-helm/tree/master/charts', 'https://github.com/k8s-at-home/charts/tree/master/charts/uptimerobot-prometheus', 'https://github.com/Kong/charts/tree/main/charts/kong', 'https://github.com/keyporttech/charts']
"""
