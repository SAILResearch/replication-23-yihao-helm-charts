import pickle
import statistics
from datetime import datetime

with open('../../data-explorer/helmcharts-data-paper/counters_with_dup.pickle', 'rb') as f:
    pkg_map_lookup = pickle.load(f)[-1]

with open('uuid_release_age.pickle', 'rb') as f:
    uuid_release_age = pickle.load(f)

print(len(uuid_release_age))  # this is a small superset of those with cves, iterate cves first then look up here

lookup_table = uuid_release_age

with open('helm_to_fixable_cves.pickle', 'rb') as f:
    helm_to_fixable_cves = pickle.load(f)

print(len(helm_to_fixable_cves))

with open('actually_fixables_age.pickle', 'rb') as f:
    actually_fixables_age = pickle.load(f)

print(len(actually_fixables_age), 'actually fixable cves age')


def days_between(d1, d2):
    # YYYY-MM-DD
    date_obj = datetime.strptime(d1, '%Y-%m-%d').date()
    date_obj2 = datetime.strptime(d2, '%Y-%m-%d').date()
    delta = date_obj - date_obj2
    days_in_between = delta.days
    if days_in_between < 0:
        return -1  # This can happen if security report is redone later
    return days_in_between


# print(actually_fixables_age)
helm_has_security_fix_count = 0
aggregated_fix_time = []
unique_cves = set()
safe_helm_charts = []
for key, value in helm_to_fixable_cves.items():
    # print(lookup_table[key], value)

    # CHeck for official helm chart
    from cve.rq2.get_official_only import all_official_pkgs

    if key not in all_official_pkgs:
        # print('non official')
        ...
        continue
    else:
        ...
        # continue
    lookedup = lookup_table[key]
    if lookedup:  # It can be none if the helm chart is deleted
        # Turn timestamp to Year-Month-Day from epoch
        timestamp_of_helm_release = lookedup[0]
        version_of_helm_release = lookedup[1]
        time_human = datetime.fromtimestamp(timestamp_of_helm_release).strftime('%Y-%m-%d')
        # print(f'published: {time_human}')
        if_has_security_fix = lookup_table[key][-1]
        if if_has_security_fix:
            helm_has_security_fix_count += 1
        high_critical_cve_fix_time = []
        if helm_to_fixable_cves[key] == []:
            # Among 6202
            print(f'no fixable cve for this helm chart {key, value}')
            safe_helm_charts.append(key)
        for cve in helm_to_fixable_cves[key]:
            if cve in actually_fixables_age:
                if pkg_map_lookup[cve]['severity'] in [
                    'CRITICAL']:  # 'MEDIUM', 'LOW', 'NONE','UNKNOWN','HIGH', 'CRITICAL',
                    ...
                    # continue
                else:
                    ...
                    continue
                high_critical_cve_fix_time.append(actually_fixables_age[cve])
                unique_cves.add(cve)
                # print(f'CVE: {cve}, published: {actually_fixables_age[cve]}')
        median_fix_time = 0
        each_fix_time = []
        for each in high_critical_cve_fix_time:
            if each != 'UNKNOWN':
                time_between = days_between(time_human, each)
                if time_between != -1:
                    each_fix_time.append(time_between)
        if len(each_fix_time) > 0:
            median_fix_time = statistics.median(each_fix_time)
            # print(f'high_critical_cve_fix_time: {high_critical_cve_fix_time}')
            # print(f'average_fix_time: {average_fix_time}, median_fix_time: {median_fix_time}')

            aggregated_fix_time.extend(each_fix_time)

print(f'safe_helm_charts: {safe_helm_charts}')
print(len(aggregated_fix_time))
print(f'unique_cves: {len(unique_cves)}')
print(f'average_fix_time: {sum(aggregated_fix_time) / len(aggregated_fix_time)}')
print(f'median_fix_time: {statistics.median(aggregated_fix_time)}')
print(f'has security fix: {helm_has_security_fix_count} out of {len(helm_to_fixable_cves)}')
