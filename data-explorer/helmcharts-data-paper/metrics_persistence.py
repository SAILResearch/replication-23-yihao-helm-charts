# read database sqlite
import json
import pickle
import random
import sqlite3
from collections import defaultdict
from datetime import datetime

"""
This script persists the metrics from cve reports to sqlite db, this is the major script for the CVE report analysis
Uncomment the line 223+ to persist the metrics to the cve2023.sqlite db
"""
random.seed(42)
DB = 'cve2023.sqlite'
possible_pkgs = set()
possible_artifacttypes = set()
possible_artifactnames = set()
involved_pkgs = dict()  # How many os-pkg and lang-pkg are involved in a helm chart
involved_cves = dict()  # How many cves are involved in a helm chart
involved_fixable_cves = dict()  # How many fixable cves are involved in a helm chart
involved_images = dict()  # How many images are involved in a helm chart
involved_releases = dict()


def cve_report_parse_metrics(uuid, name, json_data):
    data = json.loads(json_data)
    true_uuid = '-'.join(uuid.split('-')[:5])
    # search for category in OperatorHubHelmCharts table column 4
    connection = sqlite3.connect(DB)
    cursor = connection.cursor()
    cursor.execute(f'select additional_info from OperatorHubHelmCharts where uuid="{true_uuid}"')
    row = cursor.fetchall()
    try:
        cate_json = json.loads(row[0][0])
    except IndexError as e:
        print(row)
        quit()
    if 'category' in cate_json:
        chart_category = cate_json['category']
    else:
        chart_category = 'MISC'
    metrics = {
        'category': chart_category,
        'cves': dict(),
        'severity_distribution': defaultdict(int),
        'severity_distribution_fixable': defaultdict(int),
        'severity_distribution_unfixable': defaultdict(int),
        'fixable_vulnerabilities': list(),
        'fixed_versions': list(),
        'fixable_severity': list(),
        'unfixable_vulnerabilities': list(),
        'unfixable_severity': list(),
        'vulnerabilities_per_package': defaultdict(int),
        'cves_per_year': defaultdict(int),
        'cves_per_year_fixable': defaultdict(int),
        'cves_per_year_unfixable': defaultdict(int),
    }
    global possible_pkgs
    total_pkgs, total_cves, total_images = 0, 0, 0
    fixable_count = 0  # < This indicates the chart is considered safe from maintenance prospective,
    # no fixable vulnerabilities

    for key in data.keys():
        total_images += 1
        # metadata = data[key].get('Metadata', {})
        try:
            artifact_name = data[key].get('ArtifactName', '')
            artifact_type = data[key].get('ArtifactType', '')
        except AttributeError as e:
            # Shouldn't happen, it's a sqlite error
            artifact_type = 'NA'
            artifact_name = 'NA'
            print(f'data is {data[key]}')
        global possible_artifactnames, possible_artifacttypes
        possible_artifactnames.add(artifact_name)
        possible_artifacttypes.add(artifact_type)
        print(f'Processing {artifact_name} {artifact_type}')
        try:
            results = data[key].get('Results', [])
        except AttributeError as e:
            continue
        for result in results:
            total_pkgs += len(result.get('Packages', []))
            total_cves += len(result.get('Vulnerabilities', []))
            type = result.get('Type', '')
            result_class = result.get('Class', '')
            possible_pkgs.add(result_class)
            target = result.get('Target', '')

            # print(f'Processing {type} {result_class} {target}')
            vulnerabilities = result.get('Vulnerabilities', [])
            for vulnerability in vulnerabilities:
                cve = vulnerability.get('VulnerabilityID')
                if not cve.startswith('CVE-'):
                    ...
                    # print(f'detected non CVE id - {cve}')
                pkg_id = vulnerability.get('PkgID')
                pkg_name = vulnerability.get('PkgName')

                metrics['cves'][cve] = dict()
                metrics['cves'][cve]['pkg_info'] = f'{pkg_id} || {pkg_name} || {result_class}'
                metrics['cves'][cve]['severity'] = vulnerability.get('Severity')
                try:
                    score = vulnerability.get('CVSS')['nvd']['V3Score']
                    vector = vulnerability.get('CVSS')['nvd']['V3Vector']
                except Exception as e:
                    score = 'NA'  # TODO handle -1 exclude from violins
                    vector = 'NA'
                metrics['cves'][cve]['cvss_nvd'] = score
                metrics['cves'][cve]['cvss_nvd_vector'] = vector
                metrics['cves'][cve]['artifact_name'] = artifact_name
                metrics['cves'][cve]['artifact_type'] = artifact_type
                severity = vulnerability.get('Severity')
                if not severity:
                    severity = 'no severity detected'
                # if severity == 'CRITICAL':
                #     print('critical found!! CVE ID: ', cve)
                metrics['severity_distribution'][severity] += 1

                fixed_version = vulnerability.get('FixedVersion')
                published_date = vulnerability.get('PublishedDate')

                if published_date:
                    year = datetime.strptime(published_date, '%Y-%m-%dT%H:%M:%SZ').year
                    metrics['cves_per_year'][f'{year}'] += 1
                else:
                    year = 'no year detected'
                if fixed_version:
                    fixable_count += 1
                    metrics['fixable_vulnerabilities'].append(cve)
                    metrics['fixed_versions'] = fixed_version
                    metrics['severity_distribution_fixable'][severity] += 1
                    metrics['cves_per_year_fixable'][f'{year}'] += 1
                    metrics['fixable_severity'].append(severity)
                else:
                    metrics['unfixable_vulnerabilities'].append(cve)
                    metrics['severity_distribution_unfixable'][severity] += 1
                    metrics['cves_per_year_unfixable'][f'{year}'] += 1
                    metrics['unfixable_severity'].append(severity)

                pkg_name = vulnerability.get('PkgName')
                if pkg_name:
                    metrics['vulnerabilities_per_package'][pkg_name] += 1

    global involved_cves
    global involved_pkgs
    global involved_images
    global involved_fixable_cves
    global involved_releases
    if name in involved_cves:
        # could be more than one
        name = f'{name}____{random.randint(1, 999999)}__{random.randint(1, 999)}'
    involved_cves[name] = total_cves
    involved_pkgs[name] = total_pkgs
    involved_images[name] = total_images
    involved_fixable_cves[name] = fixable_count

    print(f'Processed {total_images} images, {total_pkgs} packages, {total_cves} cves')
    printed_metrics = {
        'category': metrics['category'],
        'cves': (metrics['cves']),
        'severity_distribution': metrics['severity_distribution'],
        'fixable_vulnerabilities': (metrics['fixable_vulnerabilities']),
        'fixed_version': metrics['fixed_versions'],
        'fixable_severity': (metrics['fixable_severity']),
        'severity_distribution_fixable': metrics['severity_distribution_fixable'],
        'unfixable_vulnerabilities': (metrics['unfixable_vulnerabilities']),
        'unfixable_severity': (metrics['unfixable_severity']),
        'severity_distribution_unfixable': metrics['severity_distribution_unfixable'],
        'vulnerabilities_per_package': metrics['vulnerabilities_per_package'],
        'cves_per_year': metrics['cves_per_year'],
        'cves_per_year_fixable': metrics['cves_per_year_fixable'],
        'cves_per_year_unfixable': metrics['cves_per_year_unfixable'],
    }

    # print(json.dumps(printed_metrics, indent=4))

    return printed_metrics, fixable_count


def read_db(table_name: str):
    connection = sqlite3.connect(DB)
    cursor = connection.cursor()
    cursor.execute(f'select * from {table_name}')
    row = cursor.fetchone()
    counter = 1
    empty_cve_reports = []
    total_vul_aggregated = []
    persist_metrics: [tuple[str, str]] = []
    non_empty_counter = 0
    has_no_fixables = []

    while row is not None:
        # if counter< 6167:
        #     counter += 1
        #     row = cursor.fetchone()
        #     continue
        # Process the row to see how many fixable CVEs in it
        print(f'working on No.{counter}, {row[0]} - {row[1]}')
        if row[2] == '{}' or row[2] == '{"message": ""}':
            counter += 1
            empty_cve_reports.append(row[0])

            print('empty cve report')
            row = cursor.fetchone()

            continue
        non_empty_counter += 1
        parsed_metrics, fixable_count = cve_report_parse_metrics(row[0], row[1], row[2])
        if fixable_count == 0:
            print(f'no fixable cves for {row[0]}')
            has_no_fixables.append(row[0])
        persist_metrics.append((row[0], json.dumps(parsed_metrics)))
        print(f'appended counter: {non_empty_counter}')
        total_vul_aggregated.extend(parsed_metrics['cves'])
        # Fetch the next row
        row = cursor.fetchone()
        counter += 1

        # if counter > 10:
        #     print(len(set(total_vul_aggregated)))
        #     break
    print(f'has no fixables: {has_no_fixables}')
    print(f'total unique cves: {len(set(total_vul_aggregated))}')
    print(f'empty cve reports: {len(empty_cve_reports)}')
    print(f'non empty cve reports: {counter - 1 - len(empty_cve_reports)}')

    connection.close()
    with open('metadatarq1.pickle', 'wb') as f:
        pickle.dump((involved_cves, involved_fixable_cves, involved_pkgs, involved_images), f)
    # () # QUITED HERE
    # # persist results to metrics db
    # for index, row in enumerate(persist_metrics):
    #     print(f'working on row {index+1}')
    #     persist_cve_metrics(data=row,
    #                        table_name='OperatorHubHelmChartsCVEReportsLatestOnlyMetrics')

    # pickle
    # with open('total_meta.pkl', 'wb') as f:
    #     pickle.dump((involved_cves, involved_pkgs, involved_images), f)
    print(f'possible packages: {possible_pkgs}')
    print(f'possible artifact names: {possible_artifactnames}')
    print(f'possible artifact types: {possible_artifacttypes}')

    print(f'involved cves: {involved_cves}')
    print(f'involved pkgs: {involved_pkgs}')
    print(f'involved images: {involved_images}')


if __name__ == '__main__':
    read_db('OperatorHubHelmChartsCVEReportsLatestOnly')
    #
    # # GET MEDIANS
    # import statistics
    #
    # with open('metadatarq1.pickle', 'rb') as f:
    #     total_meta = pickle.load(f)
    #     # sort based on value
    #     print(dict(sorted(total_meta[3].items(), key=lambda item: item[1])))
    #     for i in range(4):
    #         # print(sum(list(total_meta[i].values())))
    #         values_cleaned = [x for x in list(total_meta[i].values()) if x > 0]
    #         print(statistics.median(values_cleaned))
    #         print(statistics.mean(values_cleaned))
    #         print('-----------------')
    # # with open('total_meta.pkl', 'rb') as f:
    # #     total_meta = pickle.load(f)
    # #     print(total_meta)
