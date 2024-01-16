﻿# Replication package and data scrapers for Artifact Hub and Helm Charts Vulnerability

This repository contains the replication package for the [paper](https://www.semanticscholar.org/paper/Why-Not-Mitigate-Vulnerabilities-in-Helm-Charts-Chen-Lin/c7e05229738b1a63a53775c14cc95944ff31c4d9) "Why Not Mitigate Vulnerabilities in Helm Charts?" submitted to Empirical Software Engineering (EMSE).

Repository structure:

- `rq1` contains the data collection, analysis, and misc scripts for RQ1
- `rq2` contains the data collection, analysis, and misc scripts for RQ2
- `data-explorer` containers the data collection/conversion scripts for the paper.

Actual database is large (8GB) and stored in a sqlite database, it will be open-sourced to a dedicated repository.
The data explorer folder scripts can be used to reconstruct the sqlite database since core data is available in a pickled form.

The constructed database should be named `cve2023.sqlite` and placed in the cve folder.
