from __future__ import annotations

import json
from datetime import UTC, datetime

import pandas as pd

from src.config import MEETJOBS_TAIWAN_API_URL, PROCESSED_DIR, RAW_DIR, ensure_data_dirs
from src.http import get_json
from src.normalization import normalize_meetjobs


def fetch_page(page: int, *, per_page: int = 20) -> dict:
    return get_json(
        MEETJOBS_TAIWAN_API_URL,
        timeout=45,
        params={"location": "Taiwan", "per_page": per_page, "page": page},
        headers={"Accept": "application/json"},
    )


def fetch_records() -> tuple[list[dict], list[dict]]:
    first_page = fetch_page(1)
    pages = [first_page]
    records = [record for record in first_page.get("collection", []) if isinstance(record, dict)]
    paginator = first_page.get("paginator") or {}
    total_pages = int(paginator.get("total_pages") or 1)

    for page in range(2, total_pages + 1):
        payload = fetch_page(page)
        pages.append(payload)
        records.extend(record for record in payload.get("collection", []) if isinstance(record, dict))

    return [record for record in records if record.get("title")], pages


def run() -> pd.DataFrame:
    ensure_data_dirs()
    fetched_at = datetime.now(UTC).isoformat()
    records, raw_pages = fetch_records()
    (RAW_DIR / "meetjobs_taiwan_api.json").write_text(json.dumps(raw_pages, ensure_ascii=False, indent=2), encoding="utf-8")
    df = normalize_meetjobs(records, fetched_at=fetched_at)
    df.to_parquet(PROCESSED_DIR / "meetjobs_taiwan.parquet", index=False)
    return df


def main() -> None:
    df = run()
    print(f"Wrote {len(df):,} Meet.jobs Taiwan CS/IT jobs")


if __name__ == "__main__":
    main()
