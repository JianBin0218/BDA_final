from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import PROCESSED_DIR, PROJECT_ROOT
from src.pipeline.build_dataset import build_dataset


CLUSTER_ZH = {
    "Backend / Full-stack": "後端 / 全端",
    "Frontend": "前端",
    "Data / AI": "資料 / AI",
    "Cloud / DevOps / SRE": "雲端 / DevOps / SRE",
    "Cybersecurity": "資安",
    "Firmware / Embedded": "韌體 / 嵌入式",
    "QA / Test": "QA / 測試",
    "MIS / IT Support": "MIS / IT 支援",
    "Mobile": "行動應用",
    "Other CS": "其他科技職缺",
}


FRONTEND_COLUMNS = [
    "job_id",
    "title",
    "company",
    "city",
    "district",
    "location",
    "experience",
    "seniority",
    "job_type",
    "salary_monthly_min",
    "salary_monthly_max",
    "source_platform",
    "source_url",
    "source_updated_at",
    "skills",
    "career_cluster",
]


def build_frontend_payload(df: pd.DataFrame) -> dict[str, Any]:
    jobs = df[FRONTEND_COLUMNS].copy()
    jobs["skills"] = jobs["skills"].apply(_normalize_skills)
    jobs["career_cluster_zh"] = jobs["career_cluster"].map(CLUSTER_ZH).fillna(jobs["career_cluster"])
    jobs = jobs.where(pd.notna(jobs), None)

    latest = pd.to_datetime(df["source_updated_at"], errors="coerce").max()
    salary_count = int(df["salary_monthly_min"].notna().sum())
    city_count = int(df[df["city"].fillna("").ne("")]["city"].nunique())

    skill_values = sorted({skill for skills in jobs["skills"] for skill in skills})
    cluster_values = sorted(
        [
            {"value": cluster, "label": CLUSTER_ZH.get(cluster, cluster)}
            for cluster in df["career_cluster"].dropna().unique()
        ],
        key=lambda item: item["label"],
    )

    payload = {
        "generated_at": pd.Timestamp.now("UTC").isoformat(),
        "summary": {
            "job_count": int(len(df)),
            "city_count": city_count,
            "source_count": int(df["source_platform"].nunique()),
            "salary_count": salary_count,
            "latest_source_update": latest.date().isoformat() if pd.notna(latest) else None,
        },
        "facets": {
            "sources": sorted(df["source_platform"].dropna().unique().tolist()),
            "cities": sorted(city for city in df["city"].dropna().unique().tolist() if city),
            "clusters": cluster_values,
            "skills": skill_values,
        },
        "cluster_labels": CLUSTER_ZH,
        "jobs": jobs.to_dict(orient="records"),
    }
    return _json_safe(payload)


def export_frontend_data(*, output_path: Path | None = None, rebuild_dataset: bool = False) -> Path:
    dataset_path = PROCESSED_DIR / "all_taiwan_jobs.parquet"
    if rebuild_dataset or not dataset_path.exists():
        df = build_dataset()
    else:
        df = pd.read_parquet(dataset_path)

    output_path = output_path or PROJECT_ROOT / "web" / "public" / "data" / "skillscope-taiwan.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_frontend_payload(df)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    print(f"Wrote frontend payload with {len(payload['jobs']):,} jobs to {output_path}")
    return output_path


def _normalize_skills(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if hasattr(value, "tolist"):
        return [str(item) for item in value.tolist() if str(item)]
    return [str(value)] if str(value) else []


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if value is None:
        return None
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if hasattr(value, "item") and not isinstance(value, (str, bytes)):
        try:
            return _json_safe(value.item())
        except (AttributeError, TypeError, ValueError):
            pass
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Export processed SkillScope data for the Next.js frontend.")
    parser.add_argument("--output", type=Path, default=None, help="Output JSON path.")
    parser.add_argument("--rebuild-dataset", action="store_true", help="Run ingestion before exporting JSON.")
    args = parser.parse_args()
    export_frontend_data(output_path=args.output, rebuild_dataset=args.rebuild_dataset)


if __name__ == "__main__":
    main()
