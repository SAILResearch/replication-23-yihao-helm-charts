import pickle
import sqlite3
import pickle
import time

import requests

header = {'Accept': 'application/json',
          'X-API-KEY-ID': '<api_id1>',
          'X-API-KEY-SECRET': '<api_secret1>='
          }

header_gmail = {'Accept': 'application/json',
                'X-API-KEY-ID': '<api_id2>',
                'X-API-KEY-SECRET': '<api_secret2>'
                }

# with open('../artifacthub_landscape_may2023_official.pickle', 'rb') as f:
#     official_landscape = pickle.load(f)
#
# # get all package ids
# all_official_pkgs = set()
# for package in official_landscape:
#     all_official_pkgs.add(package['package_id'])
#
# #print(all_official_pkgs)
# import random
# random.seed(42)
#
# DB = 'cve2023.sqlite'
# with open('../artifacthub_landscape_may2023.pickle', 'rb') as f:
#     overall_landscape = pickle.load(f)
#
# candidates = []
# official_candidates = []
# for helm in overall_landscape:
#     package_id = helm['package_id']
#     if package_id in all_official_pkgs:
#         official_candidates.append(helm)
#     else:
#         candidates.append(helm)
#
# print(f'official: {len(official_candidates)} unofficial: {len(candidates)}')
#
# import requests
#
# api = "https://artifacthub.io/api/v1/packages/helm/{repoName}/{packageName}"
# official_links = []
# unofficial_links = []
# # for candidate in official_candidates:
# #     time.sleep(0.5)
# #     res = requests.get(api.format(repoName=candidate['repository']['name'], packageName=candidate['normalized_name']))
# #     if 'links' in res.json():
# #         print(res.json()['links'])
# #         official_links.append(res.json()['links'])
# def save_links_to_pickle(name, links):
#
#     with open(name, 'wb') as f:
#         pickle.dump(links, f)
#
# for i, candidate in enumerate(candidates):
#     try:
#         if i <= 1196:
#             continue
#
#         elif i == 1197:
#             with open ('unofficial_checkpoint_BEFORE1196.pickle', 'rb') as f:
#                 unofficial_links = pickle.load(f)
#             print(f'loaded unofficial checkpoint {i}')
#         print(f'working on {i}/{len(candidates)}')
#
#         time.sleep(0.9)
#
#         res = requests.get(api.format(repoName=candidate['repository']['name'], packageName=candidate['normalized_name']),
#                            headers=header_gmail if i % 2 == 0 else header)
#         if 'links' in res.json():
#             print(res.json()['links'])
#             unofficial_links.append(res.json()['links'])
#
#     except Exception as e:
#         print(e)
#         save_links_to_pickle(f'unofficial_checkpoint_BEFORE{i}.pickle', unofficial_links)
#         print('stopped at: ', i)
#         quit()
#     except KeyboardInterrupt:
#         save_links_to_pickle(f'unofficial_checkpoint_BEFORE{i}.pickle', unofficial_links)
#         print('stopped at: ', i)
#         quit()
#
#
# # save_links_to_pickle('official_links.pickle', official_links)
# save_links_to_pickle('unofficial_links.pickle', unofficial_links)
# with open('official_links.pickle', 'rb') as f:
#     official_links = pickle.load(f)
with open('unofficial_links.pickle', 'rb') as f:
    links = pickle.load(f)

# EXTRACT GITHUB ORG REPO PAIRS
import re


def extract_github_org_repo(urls):
    # Regular expression to match GitHub repository URLs
    github_url_pattern = re.compile(r'https://github\.com/([^/]+)/([^/]+)')

    org_repo_pairs = []

    for url_unit in urls:
        for url_small_unit in url_unit:
            url = url_small_unit['url']
            match = github_url_pattern.match(url)
            if match:
                org, repo = match.groups()
                org_repo_pairs.append(f'{org}/{repo}')

    return org_repo_pairs


extracted_official = extract_github_org_repo(links)
print(f'Count of official github org repo pairs: {len(extracted_official)}, {len(set(extracted_official))}')

headers = {
    "Authorization": f"bearer <your_github_token_with_read_permission>",  # 202312
    "Accept": "application/vnd.github.v3+json"
}

non_empty = []
for idx, org_repo_pairs in enumerate(set(extracted_official)):
    time.sleep(3)
    api = f'https://api.github.com/repos/{org_repo_pairs}/security-advisories'
    try:
        print(f'working on {api}, progress: {len(non_empty)}/{idx} official')
        response = requests.get(api, headers=headers)
        res = response.json()
        if res != {} and res != []:
            non_empty.append(org_repo_pairs)
    except Exception as e:
        time.sleep(60)
        print(e)
        with open(f'unofficial_org_repo_pairs_with_security_advisories-{idx}.pickle', 'wb') as f:
            pickle.dump(non_empty, f)
        quit()
print(f'Count of unofficial github org repo pairs with security advisories: {len(non_empty)}')
print(f'full data: {non_empty}')
with open('unofficial_org_repo_pairs_with_security_advisories.pickle', 'wb') as f:
    pickle.dump(non_empty, f)
"""
['https://github.com/PrefectHQ/prefect-helm', 'https://eginnovations.github.io/helm-charts', 'https://github.com/truecharts/charts/tree/master/charts/stable/minetest', 'https://github.com/andrcuns/charts', 'https://github.com/jfrog/charts', 'https://github.com/cosmo-workspace/charts', 'https://github.com/stevehipwell/helm-charts/', 'https://github.com/one-acre-fund/oaf-public-charts/tree/main/charts/metabase', 'https://github.com/adfinis/helm-charts', 'https://github.com/itsmethemojo/helm-hetzner-dyndns', 'https://github.com/paradeum-team/geth-charts', 'https://github.com/kubernetes/charts/tree/master/stable/openvpn', 'https://github.com/VictoriaMetrics/helm-charts', 'https://github.com/k3s-io/helm-controller', 'https://github.com/Aguafrommars/helm/tree/main/charts/theidserver', 'https://github.com/prometheus-community/helm-charts', 'https://github.com/softonic/mysql-backup-chart', 'https://github.com/teutonet/teutonet-helm-charts', 'https://github.com/kubeshop/helm-charts/tree/main/charts', 'https://github.com/prometheus-community/helm-charts', 'https://github.com/snowplow-devops/helm-charts', 'https://github.com/aws/eks-charts', 'https://github.com/startxfr/helm-repository/tree/master/charts/cluster-nexus', 'https://github.com/apache/pulsar-helm-chart', 'https://pages.git.viasat.com/ATG/charts', 'https://github.com/steadybit/helm-charts', 'https://github.com/traefik/traefik-helm-chart', 'https://github.com/jdstone/helm-charts', 'https://github.com/broadinstitute/datarepo-helm/tree/master/charts', 'https://github.com/k8s-at-home/charts/tree/master/charts/uptimerobot-prometheus', 'https://github.com/Kong/charts/tree/main/charts/kong', 'https://github.com/keyporttech/charts']
"""
