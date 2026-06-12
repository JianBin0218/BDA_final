# SkillScope

Taiwan-first CS/IT career intelligence for the Big Data Systems final project.

- Live demo: https://bda-final.vercel.app/
- Frontend: Next.js, React, TypeScript, Tailwind CSS, Recharts
- Data pipeline: Python, pandas, Parquet, DuckDB-compatible outputs
- UI language: Traditional Chinese

SkillScope turns Taiwan job postings into a career market dashboard and personalized skill-gap report. It focuses on Taiwan CS/IT roles across backend, frontend, data/AI, cloud/DevOps/SRE, cybersecurity, firmware/embedded, QA, MIS/IT support, and mobile.

## Features

- Taiwan CS/IT market overview
- Source, city, cluster, skill, and salary filters
- Career cluster distribution
- Skill demand ranking
- Salary and location analysis
- Personalized skill-gap report
- Job detail table with source links
- Scheduled data refresh through GitHub Actions

## Data Sources

Automated pipeline sources:

- TaiwanJobs open data, dataset `44062`: https://apiservice.mol.gov.tw/OdService/rest/dataset/44062
- Cake Taiwan IT jobs: https://www.cake.me/jobs/for-it/in-Taiwan?locale=en
- Meet.jobs Taiwan API: https://api.meet.jobs/api/v1/jobs?location=Taiwan
- 1111 Taiwan CS/IT keyword search pages: https://www.1111.com.tw/search/job?ks=api%2F

Evidence-only source:

- 104 keyword search: https://www.104.com.tw/jobs/search/?keyword=JSON

104 is not part of the automated pipeline because its structured endpoints currently trigger bot-protection challenges in automated environments. See [docs/data_sources.md](docs/data_sources.md) for the full data-source strategy.

## Setup

Use the course conda environment:

```bash
conda activate bitda
python -m pip install -r requirements.txt
```

Install frontend dependencies:

```bash
cd web
npm install
```

## Reproduce Data

Build the processed dataset:

```bash
python -m src.pipeline.build_dataset
```

Export the JSON used by the Next.js dashboard:

```bash
python -m src.pipeline.export_frontend_data
```

Build the DuckDB analytics database:

```bash
python -m src.pipeline.build_database
```

Run only the government open-data source:

```bash
python -m src.pipeline.build_dataset --skip-live-optional
```

## Run Locally

Start the Next.js dashboard:

```bash
cd web
npm run dev
```

The local app opens at:

```text
http://localhost:3000/
```

## Test

Python tests:

```bash
pytest -q
python -m compileall -q src tests
```

Frontend checks:

```bash
cd web
npm run lint
npm run build
```

## Deployment

The production demo is deployed on Vercel:

```text
https://bda-final.vercel.app/
```

Vercel settings:

- Root directory: `web`
- Build command: `npm run build`
- Output: Next.js default

The frontend reads the static JSON snapshot at:

```text
web/public/data/skillscope-taiwan.json
```

GitHub Actions periodically rebuilds the processed dataset, exports the frontend JSON, validates required source coverage, runs tests, and commits the updated snapshot when data changes.

## Repository Structure

```text
.github/workflows/   scheduled data refresh workflow
docs/                project documentation
src/ingest/          TaiwanJobs, Cake, Meet.jobs, and 1111 ingestion
src/pipeline/        dataset, database, and frontend export builders
src/normalization.py shared schema, salary, location, and parser logic
src/skills.py        bilingual skill dictionary
src/clusters.py      Taiwan CS/IT career cluster rules
tests/               parser, normalization, and export tests
web/                 Next.js dashboard used for the official demo
data/                generated local raw, processed, and DuckDB outputs
```

Generated files under `data/` are reproducible from the pipeline and are ignored by git. The deployed dashboard keeps only the frontend-ready JSON snapshot under `web/public/data/`.
