api = '/repos/{owner}/{repo}/vulnerability-alerts'

import statistics
import time
import pickle

import requests
from utils.day_parser import parse_days

with open('urls.txt') as f:
    urls = f.readlines()

urls = ['/'.join(url.strip().split('/')[-2:]) for url in urls]
print(urls)
# Set the headers with the authentication token
headers = {
    "Authorization": f"bearer <your_github_token_with_read_permission>",
    "Accept": "application/vnd.github.v3+json"
}
url_with_no_issues = []
url_with_no_prs = []
for idx, url in enumerate(urls):
    print(f'working on {url}. {idx}/{len(urls)}')
    if idx < 30:
        continue
    time.sleep(4)
    api = f'https://api.github.com/search/issues?q=repo:{url}+type:issue&per_page=1&page=1'
    print(api)
    res = requests.get(api, headers=headers)
    res_json = res.json()
    if 'total_count' not in res_json.keys():
        print(res_json)
        quit()
        res = requests.get(api, headers=headers)
    if res_json['total_count'] == 0:
        print(f'{url} has no issues')
        url_with_no_issues.append(url)
        continue

    api = f'https://api.github.com/search/issues?q=repo:{url}+type:pull-request&per_page=1&page=1'
    print(api)
    res = requests.get(api, headers=headers)

    # print(res.json())
    res_json = res.json()
    if 'total_count' not in res_json.keys():
        print(res_json)
        quit()
        res = requests.get(api, headers=headers)
    if res_json['total_count'] == 0:
        print(f'{url} has no PRs')
        url_with_no_prs.append(url)
        continue
    # alert_api = f'https://api.github.com/repos/{url}/vulnerability-alerts'
    # This cannot be check by outsiders, only admin

with open('url_with_no_issues.txt', 'w') as f:
    for url in url_with_no_issues:
        f.write(url + '\n')

with open('url_with_no_prs.txt', 'w') as f:
    for url in url_with_no_prs:
        f.write(url + '\n')
