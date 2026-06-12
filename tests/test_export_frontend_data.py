import json

import pandas as pd

from src.pipeline.export_frontend_data import build_frontend_payload


def test_frontend_export_schema_has_jobs_summary_and_facets():
    df = pd.DataFrame(
        [
            {
                "job_id": "job-1",
                "title": "後端工程師",
                "company": "Example",
                "city": "台北市",
                "district": "信義區",
                "location": "台北市信義區",
                "experience": "3年以上",
                "seniority": "Senior",
                "job_type": "全職",
                "salary_monthly_min": 60000,
                "salary_monthly_max": float("nan"),
                "source_platform": "TaiwanJobs",
                "source_url": "https://example.com",
                "source_updated_at": "2026-06-11",
                "skills": ["Python", "Docker"],
                "career_cluster": "Backend / Full-stack",
            }
        ]
    )

    payload = build_frontend_payload(df)
    encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False)

    assert set(["jobs", "summary", "facets"]).issubset(payload)
    assert payload["summary"]["job_count"] == 1
    assert payload["summary"]["latest_source_update"] == "2026-06-11"
    assert payload["jobs"][0]["career_cluster_zh"] == "後端 / 全端"
    assert payload["jobs"][0]["salary_monthly_max"] is None
    assert "Python" in payload["facets"]["skills"]
    assert "NaN" not in encoded
