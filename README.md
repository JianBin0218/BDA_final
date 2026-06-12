# SkillScope

Taiwan-first CS career intelligence for the Big Data Systems final project.

SkillScope turns current Taiwan job postings into a career market dashboard and personalized skill-gap report. The main source is the Ministry of Labor TaiwanJobs open-data feed, with Cake and Meet.jobs used as optional tech/startup supplements.

## Setup

Use the course conda environment:

```bash
conda activate bitda
python -m pip install -r requirements.txt
```

## Reproduce Data Collection

Build the processed Taiwan-first dataset:

```bash
python -m src.pipeline.build_dataset
```

Build the DuckDB analytics database:

```bash
python -m src.pipeline.build_database
```

Run only the government open-data source:

```bash
python -m src.pipeline.build_dataset --skip-live-optional
```

## Run Dashboard

The official demo UI is the Next.js dashboard in `web/`.

Export frontend data:

```bash
python -m src.pipeline.export_frontend_data
```

Run the Next.js app:

```bash
cd web
npm install
npm run dev
```

The legacy Streamlit dashboard is still available for fallback:

```bash
streamlit run app/streamlit_app.py
```

The app opens with Taiwan CS Market Overview and supports filtering by source, career cluster, city, skill, and salary. It also includes a personalized skill-gap report generator.

The dashboard UI is written in Traditional Chinese for Taiwan users. Skill names remain in their common English form, such as Python, React, Docker, and SQL, because these are the terms most often used in resumes and job descriptions.

## Data Sources

Primary source:

- TaiwanJobs open data, dataset `44062`: https://apiservice.mol.gov.tw/OdService/rest/dataset/44062
- The pipeline filters IT/CS jobs mainly through `CJOB1_COUNT = 08` / `CJOB_NAME1 = 資訊／軟體／系統`, then supplements obvious CS postings by title/description keywords.

Optional tech-focused sources:

- Cake Taiwan software engineer jobs: https://www.cake.me/jobs/for-it_software-engineer/in-Taiwan?locale=en
- Meet.jobs Taiwan software jobs: https://meet.jobs/en/jobs?location=Taiwan&keyword=software

Evidence-only sources:

- 104: https://www.104.com.tw/jobs/search/?keyword=JSON
- 1111: https://www.1111.com.tw/search/job?ks=api%2F

104 and 1111 are not used as the main automated pipeline because 104's structured endpoint currently triggers a Cloudflare challenge, and both sources are better treated as market evidence/cross-checks for this project.

## Repository Structure

```text
web/                 Next.js dashboard used for the official demo
app/                 Legacy Streamlit dashboard fallback
src/ingest/          TaiwanJobs, Cake, and Meet.jobs ingestion
src/pipeline/        dataset and DuckDB builders
src/normalization.py shared schema, salary, location, and parsing logic
src/skills.py        bilingual skill dictionary
src/clusters.py      Taiwan CS career cluster rules
tests/               parser and normalization tests
data/                generated raw, processed, and DuckDB outputs
```

## Tests

```bash
pytest
```

## Notes

Generated files under `data/` are reproducible from the pipeline and are intentionally not required before first run.
