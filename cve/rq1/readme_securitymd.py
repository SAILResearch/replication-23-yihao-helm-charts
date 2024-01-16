import pickle
import sqlite3
import pickle
import time

import requests

with open('../rq2/official_links_with_category.pickle', 'rb') as f:
    official_links = pickle.load(f)
# with open('unofficial_links.pickle', 'rb') as f:
#     official_links = pickle.load(f)
#


# EXTRACT GITHUB ORG REPO PAIRS
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

security_md = {}
for idx, org_repo_pairs in enumerate(set(extracted_official)):
    time.sleep(0.5)
    # readme = f'https://api.github.com/repos/{org_repo_pairs}/contents/README.md'
    category = org_repo_pairs[0]
    org_repo_pairs = org_repo_pairs[1]
    security = f'https://api.github.com/repos/{org_repo_pairs}/contents/SECURITY.md'

    try:
        print(f'working on {idx}, progress: {len(security_md.keys())}/{idx} unofficial')
        # readme_response = requests.get(readme,headers=headers)
        security_response = requests.get(security,headers=headers)
        res = security_response.json()
        print(security)
        if "name" in res and res["name"] == "SECURITY.md":
            security_md[org_repo_pairs] = (category, res)
    except Exception as e:
        time.sleep(60)
        print(e)
        with open(f'official-security-{idx}.pickle', 'wb') as f:
            pickle.dump(security_md, f)

print(f'Count of official-security-md: {len(security_md)}')
print(f'full data: {security_md}')
with open('../rq2/official-security.pickle', 'wb') as f:
    pickle.dump(security_md, f)
"""
['https://github.com/PrefectHQ/prefect-helm', 'https://eginnovations.github.io/helm-charts', 'https://github.com/truecharts/charts/tree/master/charts/stable/minetest', 'https://github.com/andrcuns/charts', 'https://github.com/jfrog/charts', 'https://github.com/cosmo-workspace/charts', 'https://github.com/stevehipwell/helm-charts/', 'https://github.com/one-acre-fund/oaf-public-charts/tree/main/charts/metabase', 'https://github.com/adfinis/helm-charts', 'https://github.com/itsmethemojo/helm-hetzner-dyndns', 'https://github.com/paradeum-team/geth-charts', 'https://github.com/kubernetes/charts/tree/master/stable/openvpn', 'https://github.com/VictoriaMetrics/helm-charts', 'https://github.com/k3s-io/helm-controller', 'https://github.com/Aguafrommars/helm/tree/main/charts/theidserver', 'https://github.com/prometheus-community/helm-charts', 'https://github.com/softonic/mysql-backup-chart', 'https://github.com/teutonet/teutonet-helm-charts', 'https://github.com/kubeshop/helm-charts/tree/main/charts', 'https://github.com/prometheus-community/helm-charts', 'https://github.com/snowplow-devops/helm-charts', 'https://github.com/aws/eks-charts', 'https://github.com/startxfr/helm-repository/tree/master/charts/cluster-nexus', 'https://github.com/apache/pulsar-helm-chart', 'https://pages.git.viasat.com/ATG/charts', 'https://github.com/steadybit/helm-charts', 'https://github.com/traefik/traefik-helm-chart', 'https://github.com/jdstone/helm-charts', 'https://github.com/broadinstitute/datarepo-helm/tree/master/charts', 'https://github.com/k8s-at-home/charts/tree/master/charts/uptimerobot-prometheus', 'https://github.com/Kong/charts/tree/main/charts/kong', 'https://github.com/keyporttech/charts']
"""