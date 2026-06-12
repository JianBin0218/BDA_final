from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from bs4 import BeautifulSoup

from src.config import (
    PROCESSED_DIR,
    RAW_DIR,
    TAIWANJOBS_DATASET_URL,
    TAIWANJOBS_JSON_URL,
    TAIWANJOBS_WEBSERVICE_URL,
    ensure_data_dirs,
)
from src.http import get_json, get_text
from src.normalization import normalize_taiwanjobs


MAJOR_TAIWAN_ZIP_CODES = (
    "100",  # Taipei Zhongzheng
    "105",  # Taipei Songshan
    "114",  # Taipei Neihu
    "220",  # New Taipei Banqiao
    "231",  # New Taipei Xindian
    "235",  # New Taipei Zhonghe
    "330",  # Taoyuan
    "300",  # Hsinchu City
    "302",  # Hsinchu County Zhubei
    "350",  # Miaoli Zhunan
    "400",  # Taichung Central
    "407",  # Taichung Xitun
    "700",  # Tainan Central West
    "710",  # Tainan Yongkang
    "800",  # Kaohsiung Xinxing
    "806",  # Kaohsiung Qianzhen
)


def fetch_metadata() -> dict[str, Any]:
    return get_json(TAIWANJOBS_DATASET_URL)


def fetch_records() -> list[dict[str, Any]]:
    payload = get_json(TAIWANJOBS_JSON_URL, timeout=90)
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        records = payload.get("result", {}).get("records")
        if isinstance(records, list):
            return records
    raise ValueError("Unexpected TaiwanJobs payload shape")


def fetch_webservice_records(zip_codes: tuple[str, ...] = MAJOR_TAIWAN_ZIP_CODES) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for zip_code in zip_codes:
        text = get_text(TAIWANJOBS_WEBSERVICE_URL, timeout=45, params={"zipno": zip_code, "count": "1000"})
        records.extend(parse_webservice_xml(text))
    return records


def parse_webservice_xml(text: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(text, "xml")
    parsed: list[dict[str, Any]] = []
    for data_node in soup.find_all("Data"):
        record = {}
        for child in data_node.find_all(recursive=False):
            record[child.name] = child.get_text(strip=True)
        if record:
            parsed.append(record)
    return parsed


def run() -> pd.DataFrame:
    ensure_data_dirs()
    fetched_at = datetime.now(UTC).isoformat()
    metadata = fetch_metadata()
    records = fetch_records()
    webservice_records = fetch_webservice_records()
    records = _dedupe_records(records + webservice_records)
    source_updated_at = metadata.get("modifiedDate")

    raw_path = RAW_DIR / "taiwanjobs_raw.json"
    raw_path.write_text(
        json.dumps(
            {
                "fetched_at": fetched_at,
                "source_modified_at": source_updated_at,
                "metadata": metadata,
                "webservice_zip_codes": MAJOR_TAIWAN_ZIP_CODES,
                "records": records,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    all_df = normalize_taiwanjobs(records, fetched_at=fetched_at, source_updated_at=source_updated_at)
    all_df.to_parquet(PROCESSED_DIR / "taiwanjobs_all.parquet", index=False)

    cs_records = [
        record
        for record in records
        if _is_cs_record(record)
        or _looks_like_cs(record.get("OCCU_DESC（職務名稱）"), record.get("JOB_DETAIL（工作內容）"))
    ]
    cs_df = normalize_taiwanjobs(cs_records, fetched_at=fetched_at, source_updated_at=source_updated_at)
    cs_df = cs_df[
        cs_df["career_cluster"].ne("Other CS")
        | cs_df["title"].str.contains("工程師|程式|軟體|資料|資安|MIS|系統|網路|韌體", case=False, na=False)
        | cs_df["description"].str.contains("Python|Java|JavaScript|SQL|API|雲端|資料庫|前端|後端|資安|韌體", case=False, na=False)
    ].copy()
    cs_df.to_parquet(PROCESSED_DIR / "taiwan_cs_jobs.parquet", index=False)
    return cs_df


def _is_cs_record(record: dict[str, Any]) -> bool:
    return (
        str(record.get("CJOB1_COUNT（職務大類別代碼）", "")).zfill(2) == "08"
        or str(record.get("CJOB_NAME1（職務大類別名稱）", "")).strip() == "資訊／軟體／系統"
    )


def _looks_like_cs(title: Any, description: Any) -> bool:
    text = f"{title or ''} {description or ''}"
    keywords = ("工程師", "程式", "軟體", "資料庫", "資料工程", "前端", "後端", "全端", "資安", "韌體", "Python", "JavaScript", "SQL", "API", "K8S")
    return any(keyword.lower() in text.lower() for keyword in keywords)


def _dedupe_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    deduped = []
    for record in records:
        key = (
            record.get("URL_QUERY（職缺資料URL）"),
            record.get("OCCU_DESC（職務名稱）"),
            record.get("COMPNAME（公司名稱）"),
            record.get("CITYNAME（工作地點）"),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record)
    return deduped


def main() -> None:
    df = run()
    print(f"Wrote {len(df):,} Taiwan CS jobs to {Path(PROCESSED_DIR / 'taiwan_cs_jobs.parquet')}")


if __name__ == "__main__":
    main()
