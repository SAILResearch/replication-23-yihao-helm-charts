import pickle

with open('../../data-explorer/helmcharts-data-paper/counters_with_dup.pickle', 'rb') as f:
    total_meta = pickle.load(f)

(cve_counter, cve_fixable_counter, cve_unfixable_counter, cve_pkg_id_map) = total_meta
print(f'From {len(cve_counter)} cves')
counter = 0
for cve, count in cve_counter.most_common():
    if 'CVE' not in cve:
        continue
    year_of_cve = cve.split('-')[1]
    if int(year_of_cve) < 2022:
        counter += 1
    # print(f'{cve}: {count} - {cve_pkg_id_map[cve]["severity"]}')
    # print(f'type of package impacted by {cve}: {cve_pkg_id_map[cve]["pkg_info"]}')
print(f'older than 2022: {counter} percentage: {counter / len(cve_counter)}')
print('-------FIXABLE--------------')
count_fixable = 0
print(f'From {len(cve_fixable_counter)} fixable cves')
fixable_high_critical = 0
for cve, count in cve_fixable_counter.most_common():
    if 'CVE' not in cve:
        continue
    year_of_cve = cve.split('-')[1]
    if int(year_of_cve) < 2022:
        count_fixable += 1
        if cve_pkg_id_map[cve]["severity"] in ['HIGH', 'CRITICAL']:
            fixable_high_critical += 1
    # print(f'{cve}: {count} - {cve_pkg_id_map[cve]["severity"]}')
    # print(f'type of package impacted by {cve}: {cve_pkg_id_map[cve]["pkg_info"]}')

print(f'high or critical: {fixable_high_critical}, percentage: {fixable_high_critical / len(cve_fixable_counter)}')
print(f'older than 2022: {count_fixable}, percentage: {count_fixable / len(cve_fixable_counter)}')
print('--------UNFIXABLE-------------')
print(f'From {len(cve_unfixable_counter)} unfixable cves')
count_unfixable = 0
for cve, count in cve_unfixable_counter.most_common():
    if 'CVE' not in cve:
        continue
    year_of_cve = cve.split('-')[1]
    if int(year_of_cve) < 2022:
        count_unfixable += 1
    # print(f'{cve}: {count} - {cve_pkg_id_map[cve]["severity"]}')
    # print(f'type of package impacted by {cve}: {cve_pkg_id_map[cve]["pkg_info"]}')

print(f'older than 2022: {count_unfixable}, percentage: {count_unfixable / len(cve_unfixable_counter)}')

print('---------------------')
# a set of all impacted packages
all_impacted_packages = set()
for cve in cve_pkg_id_map.keys():
    all_impacted_packages.add(cve_pkg_id_map[cve]['pkg_info'].split(' || ')[1])
# print(f'All impacted packages: \n {(all_impacted_packages)}')
