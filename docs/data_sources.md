# SkillScope Data Sources

SkillScope is a Taiwan-first CS/IT career intelligence dashboard. The reproducible data pipeline combines public open data, public web/API endpoints, and clearly labeled optional sources.

Current live demo:

- https://bda-final.vercel.app/

## Automated Sources

### TaiwanJobs Open Data

TaiwanJobs is the government open-data base source.

- Dataset title: 台灣就業通網站職缺清單
- Dataset ID: `44062`
- Metadata URL: https://apiservice.mol.gov.tw/OdService/rest/dataset/44062
- Download URL: https://apiservice.mol.gov.tw/OdService/download/A17000000J-030144-nkP
- Ingestion module: `src/ingest/taiwanjobs.py`
- Raw snapshot: `data/raw/taiwanjobs_raw.json`
- Processed outputs:
  - `data/processed/taiwanjobs_all.parquet`
  - `data/processed/taiwan_cs_jobs.parquet`

The pipeline keeps the full raw dataset, then filters CS/IT roles mainly through `CJOB1_COUNT = 08` / `CJOB_NAME1 = 資訊／軟體／系統`. It also keeps obvious CS/IT postings found through role keywords.

Important fields include title, company, job category, city, district, description, experience, education, salary type, salary range, source URL, and update date.

### Cake

Cake supplements Taiwan tech/startup postings with richer skills, salary, seniority, and job-type metadata.

- Discovery URL: https://www.cake.me/jobs/for-it/in-Taiwan?locale=en
- Ingestion module: `src/ingest/cake.py`
- Raw snapshots:
  - `data/raw/cake_taiwan_it_bootstrap.html`
  - `data/raw/cake_taiwan_it_algolia.json`
- Processed output: `data/processed/cake_taiwan_it.parquet`

The collector reads Cake's public bootstrap data to discover Algolia credentials, then queries the job index with Taiwan/IT filters. If Cake changes schema or blocks access, the pipeline logs a warning and continues with the other sources.

### Meet.jobs

Meet.jobs supplements smaller but salary-transparent Taiwan tech postings.

- API URL: https://api.meet.jobs/api/v1/jobs?location=Taiwan
- Ingestion module: `src/ingest/meetjobs.py`
- Raw snapshot: `data/raw/meetjobs_taiwan_api.json`
- Processed output: `data/processed/meetjobs_taiwan.parquet`

The collector paginates the public API and normalizes title, employer, description, salary, skills, work type, published date, updated date, and source URL. Non-CS/IT records are filtered out during normalization.

### 1111

1111 is included as an automated supplementary source for broader Taiwan job-board coverage.

- Search URL: https://www.1111.com.tw/search/job
- Example query: https://www.1111.com.tw/search/job?ks=api%2F
- Ingestion module: `src/ingest/one1111.py`
- Raw snapshot: `data/raw/1111_taiwan_search_pages.json`
- Processed output: `data/processed/1111_taiwan.parquet`

The collector searches a fixed CS/IT keyword list, including software, frontend, backend, data, AI, DevOps, SRE, security, firmware, embedded, QA, MIS, system engineering, API, Python, and JavaScript. It extracts job cards and source URLs from the returned search pages, then normalizes them into the shared schema.

1111 can behave differently on GitHub Actions than on a local Taiwan development machine. The scheduled workflow therefore validates source coverage before committing a new frontend JSON snapshot.

## Evidence-Only Source

### 104

104 is kept as market evidence and cross-check material, but is not part of the automated pipeline.

- Search URL: https://www.104.com.tw/jobs/search/?keyword=JSON

The reason is practical reproducibility: 104's structured endpoints currently trigger bot-protection / Cloudflare-style challenges in automated environments. Including it as a required source would make the scheduled pipeline unstable.

## Shared Output Schema

All sources are normalized into a shared job schema with fields such as:

- `job_id`
- `title`
- `company`
- `country`
- `city`
- `district`
- `location`
- `description`
- `experience`
- `seniority`
- `job_type`
- `salary_min`
- `salary_max`
- `salary_monthly_min`
- `salary_monthly_max`
- `salary_period`
- `salary_currency`
- `source_platform`
- `source_url`
- `source_updated_at`
- `skills`
- `career_cluster`

The frontend export is generated at:

- `web/public/data/skillscope-taiwan.json`

The JSON contains `jobs`, `summary`, `facets`, and `cluster_labels`, and is what the deployed Next.js dashboard reads.

## Reproduction Commands

Build the processed dataset:

```bash
python -m src.pipeline.build_dataset
```

Export the frontend JSON:

```bash
python -m src.pipeline.export_frontend_data
```

Build only the government open-data source:

```bash
python -m src.pipeline.build_dataset --skip-live-optional
```

Run tests:

```bash
pytest -q
```
