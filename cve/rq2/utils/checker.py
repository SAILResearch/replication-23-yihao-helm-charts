import pickle

with open('../repo_issues.pickle', 'rb') as f:
    repo_issues, raw_data = pickle.load(f)

print(raw_data.keys())


for key, value in raw_data.items():
    print(key)    # print(value['items'])

    for item in value['items']:
        body = item['body']

        if 'cve' in body.lower():
            print(f'yes for {key}')

    print('---------------------')