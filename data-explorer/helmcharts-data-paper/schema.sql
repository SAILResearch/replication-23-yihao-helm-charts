-- DROP TABLE IF EXISTS OperatorHubHelmCharts;
-- DROP TABLE IF EXISTS OperatorHubHelmChartsCVEReports;
-- DROP TABLE IF EXISTS OperatorHubHelmChartsCVEReportsLatestOnly;

CREATE TABLE if not exists OperatorHubHelmCharts (
    uuid varchar primary key,
    name Text,
    org Text,
    org_and_name Text,
    additional_info Text,
    available_versions TEXT,
    count_versions integer,
    uuid_version_ref TEXT, -- temp field to store the uuid of the latest version to join tables
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE if not exists OperatorHubHelmChartsCVEReports (
    uuid varchar primary key UNIQUE, -- make sure we don't have duplicates
    name varchar not null,
    cve_report_json Text NOT NULL,
    version VARCHAR NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (name) REFERENCES OperatorHubHelmCharts (name)
);

CREATE TABLE if not exists OperatorHubHelmChartsCVEReportsLatestOnly (
    uuid varchar primary key UNIQUE, -- make sure we don't have duplicates
    name varchar not null,
    cve_report_json Text NOT NULL,
    version VARCHAR NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (name) REFERENCES OperatorHubHelmCharts (name)
);


CREATE TABLE if not exists OperatorHubHelmChartsCVEReportsLatestOnlyMetrics (
    uuid varchar primary key UNIQUE, -- make sure we don't have duplicates
    metrics varchar not null,
    FOREIGN KEY (uuid) REFERENCES OperatorHubHelmChartsCVEReportsLatestOnly (uuid)
);