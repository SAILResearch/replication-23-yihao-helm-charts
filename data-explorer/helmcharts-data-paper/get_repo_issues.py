import re

# get issues from repo

import requests
import json
import time
import random

repo_url = 'https://api.github.com/repos/org/rep/issues?page=0&per_page=5'


def get_issues(repo_url):
    # print(repo_url)
    with open('../operator-unused-data/repo_urls.txt') as f:
        repo_urls = f.readlines()
    repo_urls = [url.strip() for url in repo_urls]
    number_of_issues_list = []
    number_of_commits_list = []
    for url in repo_urls:
        if url.startswith('https://github.com'):
            print(s := url.split('/')[-2:])
            try:
                time.sleep(2)
                response = requests.get(f'https://api.github.com/repos/{s[0]}/{s[1]}/issues?page=0&per_page=5',
                                        auth=('superskyyy', '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'))
                print(issue_count := response.json()[0]['number'])
                number_of_issues_list.append(issue_count)
                u = s[0]
                r = s[1]

                def commitCount(u, r):
                    try:
                        return re.search('\d+$', requests.get(
                            'https://api.github.com/repos/{}/{}/commits?per_page=1'.format(u, r),
                            auth=('superskyyy', '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')).links['last'][
                            'url']).group()
                    except Exception as e:
                        print(e)
                        return -1

                print(commit_count := commitCount(u, r))
                number_of_commits_list.append(commit_count)
            except Exception as e:
                print(e)
                print(response.json())
                print('Error')
                continue
    print(number_of_issues_list)
    print(number_of_commits_list)
    print(sum(number_of_issues_list), sum(number_of_commits_list))
    return number_of_issues_list, number_of_commits_list


if __name__ == '__main__':
    # get_issues(repo_url)
    issues = [1046, 6, 1112, 71, 9, 407, 163, 213, 94, 221, 207, 1179, 524, 192, 147, 99, 76, 53, 8, 1, 110, 314, 85,
              437, 87, 191, 1714, 2139, 58, 60, 492, 1642, 1245, 84, 1201, 305, 6, 38, 15, 423, 824, 3310, 3456, 8, 243,
              451, 315, 93, 501, 5577, 108, 2106, 780, 211, 435, 249, 317, 412, 637, 443, 102, 98, 519, 22, 1190, 4,
              3808, 645, 235, 81, 45, 25, 619, 845, 1285, 43, 2587, 1, 235, 5, 100, 241, 1319, 131, 1072, 4778, 1124,
              228, 1119, 2339, 4439, 106, 104, 311, 319, 624, 738, 2168, 2116, 34, 1528, 137, 229, 969, 1295, 93, 18,
              800, 765, 186, 1341, 5, 7611, 5154, 1298, 122, 203, 1154, 86, 1244, 299, 6169, 32, 121, 11, 3, 23, 39, 1,
              26, 205, 223, 4, 1306, 190, 166, 250, 88, 11, 5, 44, 680, 30, 47, 5626, 133, 764, 50, 56, 98, 35, 1, 282,
              7, 992, 590, 5334, 5, 103, 552, 28, 139, 116, 15469, 485, 226, 59, 36, 42, 352, 366, 24, 780, 11297, 1221,
              281, 678, 277, 190, 219, 280, 215, 1266, 1025, 363, 11, 272, 1905, 32]

    commits = ['4370', '202', '763', '147', '82', '626', '144', '221', '145', '171', '207', '2418', '603', '114', '849',
               '199', '89', '818', '21', '46', '73', '450', '280', '506', '229', '322', '995', '1344', '1272', '118',
               '613', '850', '1824', '199', '1629', '842', '5', '42', '99', '327', '908', '2425', '3641', '20', '416',
               '775', '303', '357', '200', '7280', '221', '1181', '1039', '362', '462', '1440', '177', '337', '571',
               '576', '83', '220', '309', '61', '1946', '19', '4710', '11102', '544', '89', '151', '67', '1365', '1093',
               '807', '373', '4400', '23', '607', '265', '196', '60', '980', '376', '1576', '1879', '716', '290',
               '1038', '1594', '7180', '146', '99', '3161', '353', '706', '653', '2637', '1062', '61', '3997', '248',
               '123', '1198', '1332', '512', '61', '673', '873', '411', '847', '14', '4866', '5338', '709', '277',
               '430', '831', '168', '655', '374', '3692', '109', '129', '69', '3', '24', '207', '19', '63', '228',
               '290', '34', '930', '274', '220', '279', '541', '714', '119', '446', '439', '251', '48', '6507', '121',
               '460', '459', '53', '177', '223', '34', '328', '9', '1108', '423', '7568', '6', '126', '609', '115',
               '183', '250', '14960', '259', '382', '120', '76', '61', '783', '467', '72', '1125', '9319', '752', '257',
               '442', '382', '271', '381', '179', '217', '1833', '800', '377', '40', '373', '3932', '270']

    # include number if they > 100
    issues = [i for i in issues if i > 500]
    commits = [i for i in commits if int(i) > 1000]
    print(len(issues), len(commits))
    print(sum(issues))
    print(sum([int(i) for i in commits]))
