import pickle

with open('../../data-explorer/helmcharts-data-paper/counters_with_dup.pickle', 'rb') as f:
    cve_counter, cve_fixable_counter, cve_unfixable_counter, cve_pkg_id_map = pickle.load(f)

print(cve_pkg_id_map)
print(f'From {len(cve_counter)} cves')
for cve, count in cve_counter.most_common(n=20):
    print(f'{cve}: {count} - {cve_pkg_id_map[cve]["severity"]}')
    print(f'type of package impacted by {cve}: {cve_pkg_id_map[cve]["pkg_info"]}')


print('-------FIXABLE--------------')

print(f'From {len(cve_fixable_counter)} fixable cves')
for cve, count in cve_fixable_counter.most_common(n=200):
    print(f'{cve}: {count} - {cve_pkg_id_map[cve]["severity"]}')

print('--------UNFIXABLE-------------')
print(f'From {len(cve_unfixable_counter)} unfixable cves')
for cve, count in cve_unfixable_counter.most_common(n=20):
    print(f'{cve}: {count} - {cve_pkg_id_map[cve]["severity"]}')
    print(f'type of package impacted by {cve}: {cve_pkg_id_map[cve]["pkg_info"]}')

print('---------------------')
# a set of all impacted packages
all_impacted_packages = set()
for cve in cve_pkg_id_map.keys():
    all_impacted_packages.add(cve_pkg_id_map[cve]['pkg_info'].split(' || ')[1])
# print(f'All impacted packages: \n {(all_impacted_packages)}')
