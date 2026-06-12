# Taiwan-First Data Sources

## Primary: TaiwanJobs Open Data

The main data source is the Ministry of Labor TaiwanJobs website job listing dataset.

- Dataset title: 台灣就業通網站職缺清單
- Dataset ID: `44062`
- Source URL: https://apiservice.mol.gov.tw/OdService/rest/dataset/44062
- JSON resource: `A17000000J-030144-nkP`
- Key fields: job title, job type, occupational category, headcount, deadline, description, city, experience, work time, salary type, salary range, education, job URL, company, update date.

The system keeps a raw snapshot in `data/raw/taiwanjobs_raw.json`, then writes:

- `data/processed/taiwanjobs_all.parquet`
- `data/processed/taiwan_cs_jobs.parquet`

## Optional Supplements

Cake is used for Taiwan software-engineering postings with richer tags and salary metadata when available:

https://www.cake.me/jobs/for-it_software-engineer/in-Taiwan?locale=en

Meet.jobs is used for Taiwan/software search results with visible salary and skill tags:

https://meet.jobs/en/jobs?location=Taiwan&keyword=software

Both are optional. If either source changes schema or blocks automated access, the pipeline logs a warning and continues with TaiwanJobs.

## Evidence-Only Sources

104 and 1111 are used in the written report as market evidence and cross-checks, but not as primary automated data sources.

- 104 JSON keyword search: https://www.104.com.tw/jobs/search/?keyword=JSON
- 1111 API keyword search: https://www.1111.com.tw/search/job?ks=api%2F

This keeps the implementation reproducible and avoids depending on protected or unstable scraping paths.
