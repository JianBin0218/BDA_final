from __future__ import annotations

import argparse

import duckdb
import pandas as pd

from src.config import DB_DIR, PROCESSED_DIR, ensure_data_dirs
from src.pipeline.build_dataset import build_dataset
from src.skills import skill_categories


def build_database(*, rebuild_dataset: bool = False) -> None:
    ensure_data_dirs()
    dataset_path = PROCESSED_DIR / "all_taiwan_jobs.parquet"
    if rebuild_dataset or not dataset_path.exists():
        df = build_dataset()
    else:
        df = pd.read_parquet(dataset_path)

    jobs = df.copy()
    job_skills = jobs[["job_id", "skills"]].explode("skills").dropna()
    job_skills = job_skills.rename(columns={"skills": "skill_name"})
    job_skills = job_skills[job_skills["skill_name"].astype(str).str.len() > 0]

    categories = skill_categories(job_skills["skill_name"].drop_duplicates().tolist())
    skills = pd.DataFrame(
        [
            {"skill_id": idx + 1, "skill_name": skill, "skill_category": categories.get(skill, "Other")}
            for idx, skill in enumerate(sorted(categories))
        ]
    )

    if not job_skills.empty and not skills.empty:
        job_skills = job_skills.merge(skills[["skill_id", "skill_name"]], on="skill_name", how="left")
        job_skills = job_skills[["job_id", "skill_id", "skill_name"]]

    clusters = (
        jobs.groupby("career_cluster", dropna=False)
        .agg(job_count=("job_id", "count"))
        .reset_index()
        .rename(columns={"career_cluster": "cluster_name"})
    )

    db_path = DB_DIR / "skillscope.duckdb"
    with duckdb.connect(str(db_path)) as con:
        con.execute("CREATE OR REPLACE TABLE job_postings AS SELECT * FROM jobs")
        con.execute("CREATE OR REPLACE TABLE skills AS SELECT * FROM skills")
        con.execute("CREATE OR REPLACE TABLE job_skills AS SELECT * FROM job_skills")
        con.execute("CREATE OR REPLACE TABLE career_clusters AS SELECT * FROM clusters")
    print(f"Wrote DuckDB analytics database to {db_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build SkillScope DuckDB database.")
    parser.add_argument("--rebuild-dataset", action="store_true", help="Run ingestion before writing DuckDB.")
    args = parser.parse_args()
    build_database(rebuild_dataset=args.rebuild_dataset)


if __name__ == "__main__":
    main()
