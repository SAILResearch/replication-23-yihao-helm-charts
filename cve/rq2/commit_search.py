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

repo_commits = {}
raw_response = {}
# with open('repo_commits.pickle', 'rb') as f:
#     repo_commits, raw = pickle.load(f)
for url in urls:
    if url in repo_commits.keys():
        print(f'{url} already in repo_issues')
        continue
    time.sleep(3)
    print(f'working on {url}')
    api = f'https://api.github.com/search/commits?q=is:issue%20CVE%20OR%20cves%20OR%20cve%20OR%20CVSS%20OR%20GHSA%20OR%20vulnerability%20repo:{url}'
    try:
        print(api)
        quit()
        response = requests.get(api, headers=headers)
        raw_response[url] = response.json()
        total_count = response.json()['total_count']
        if total_count == 0:
            repo_commits[url] = {}
            continue
        incomplete_results = response.json()['incomplete_results']
        items = response.json()['items']
        comments_receiveds = []
        days_list = []
        issue_urls = []
        author_associations = []
        for item in items:
            html_url = item['html_url']
            comments_received = int(item['comments'])
            comments_receiveds.append(comments_received)
            issue_urls.append(html_url)
            author_association = item['author_association']
            author_associations.append(author_association)
            if item['state'] == 'closed':
                days = parse_days(item['created_at'], item['closed_at'])
                days_list.append(days)
        print(f'Mean comments received: {sum(comments_receiveds) / len(comments_receiveds)}')
        if len(days_list) != 0:
            print(f'Mean/median Time to close:  {sum(days_list) / len(days_list)} vs {statistics.median(days_list)}')
        repo_commits[url] = {'total_count': total_count, 'incomplete_results': incomplete_results,
                             'comments_receiveds': comments_receiveds, 'days_list': days_list, 'issue_urls': issue_urls,
                             'author_associations': author_associations}
    except Exception as e:
        print(f'Error: {e}')
        print('crashed saving')
        print(response.json())

        with open('repo_issues.pickle', 'wb') as f:
            pickle.dump((repo_commits, raw_response), f)
        quit()
with open('repo_issues.pickle', 'wb') as f:
    pickle.dump((repo_commits, raw_response), f)
