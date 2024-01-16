import json
import pickle
import time

from db_store import persist_package
from artifacthub_scraper_cve import get_helm_versions


def persist_to_sqlite():
    with open('artifacthub_landscape.pickle', 'rb') as f:
        from db_store import init_db
        init_db()
        data = pickle.load(f)
        for helm in data:
            org_name = helm['repository']['name']
            helm_name = helm['name']
            helm_id = helm['package_id']

            # two duplicates
            # total valid 9382 as of 2022 12
            """
            UNIQUE constraint failed: OperatorHubHelmCharts.uuid
            ('87650315-e31d-41c3-b1f5-1d8c1a8f6201', 'kube-prometheus-stack', 'prometheus-worawutchan', '{"package_id": "87650315-e31d-41c3-b1f5-1d8c1a8f6201", "name": "kube-prometheus-stack", "normalized_name": "kube-prometheus-stack", "logo_image_id": "0503add5-3fce-4b63-bbf3-b9f649512a86", "stars": 1, "description": "kube-prometheus-stack collects Kubernetes manifests, Grafana dashboards, and Prometheus rules combined with documentation and scripts to provide easy to operate end-to-end Kubernetes cluster monitoring with Prometheus using the Prometheus Operator.", "version": "12.8.0", "app_version": "0.44.0", "deprecated": false, "signed": false, "production_organizations_count": 0, "ts": 1607676926, "repository": {"url": "https://worawutchan.github.io/helm-charts", "kind": 0, "name": "prometheus-worawutchan", "official": false, "user_alias": "worawutchan", "display_name": "prometheus-worawutchan", "repository_id": "fd7f4268-c6ec-4196-a94d-3e8af6758127", "scanner_disabled": false, "verified_publisher": false}}')
            UNIQUE constraint failed: OperatorHubHelmCharts.uuid
            ('b2904e15-1624-4f6a-b042-96b412c605f3', 'base', 'nn-co', '{"package_id": "b2904e15-1624-4f6a-b042-96b412c605f3", "name": "base", "normalized_name": "base", "stars": 0, "description": "A Base or general chart for Kubernetes", "version": "0.1.0", "app_version": "1.0.0", "license": "Apache-2.0", "deprecated": false, "signed": false, "security_report_summary": {"low": 95, "high": 16, "medium": 15, "unknown": 0, "critical": 4}, "all_containers_images_whitelisted": false, "production_organizations_count": 0, "ts": 1631181901, "repository": {"url": "https://urbanindo.github.io/99-charts", "kind": 0, "name": "nn-co", "official": false, "display_name": "99 Group", "repository_id": "4f1c5ad0-57f9-4123-966d-94f8c57b47b2", "scanner_disabled": false, "organization_name": "99", "verified_publisher": true, "organization_display_name": "99 Group"}}')
            """
            available_versions = len(get_helm_versions(org_name, helm_name))
            time.sleep(0.5)
            persist_package((helm_id, helm_name, org_name, f'{org_name}/{helm_name}', json.dumps(helm),
                             str(available_versions), len(available_versions)), 'OperatorHubHelmCharts')


if __name__ == '__main__':
    persist_to_sqlite()
