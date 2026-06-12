from __future__ import annotations

import html
import json
import re
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlencode

import pandas as pd

from src.config import CAKE_ALGOLIA_MAX_PAGES, CAKE_TAIWAN_IT_URL, PROCESSED_DIR, RAW_DIR, ensure_data_dirs
from src.http import get_text, post_json
from src.normalization import normalize_cake_jobs


class CakeSchemaWarning(RuntimeError):
    pass


def parse_next_data(text: str) -> dict[str, Any]:
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">\s*(.*?)\s*</script>', text, flags=re.S)
    if not match:
        raise CakeSchemaWarning("Cake __NEXT_DATA__ script not found")
    return json.loads(html.unescape(match.group(1)))


def extract_algolia_credentials(next_data: dict[str, Any]) -> tuple[str, str]:
    try:
        algolia = next_data["props"]["pageProps"]["initialState"]["auth"]["kickoff"]["algolia"]
        app_id = algolia["id"]
        api_key = algolia["key_global_search"]
    except KeyError as exc:
        raise CakeSchemaWarning("Cake Algolia credentials not found") from exc
    if not app_id or not api_key:
        raise CakeSchemaWarning("Cake Algolia credentials are empty")
    return str(app_id), str(api_key)


def extract_bootstrap_records(next_data: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    try:
        entities = next_data["props"]["pageProps"]["initialState"]["jobSearch"]["entityByPathId"]
    except KeyError as exc:
        raise CakeSchemaWarning("Cake jobSearch.entityByPathId not found") from exc

    if not isinstance(entities, dict):
        raise CakeSchemaWarning("Cake entityByPathId is not a dict")

    return [(path, record) for path, record in entities.items() if isinstance(record, dict)]


def fetch_algolia_page(app_id: str, api_key: str, page: int) -> dict[str, Any]:
    endpoint = f"https://{app_id}-dsn.algolia.net/1/indexes/*/queries"
    params = urlencode(
        {
            "query": "",
            "page": page,
            "hitsPerPage": 10,
            "facetFilters": json.dumps([["location_list:Taiwan"], ["profession:it"]]),
        }
    )
    return post_json(
        endpoint,
        timeout=45,
        headers={
            "Content-Type": "application/json",
            "X-Algolia-API-Key": api_key,
            "X-Algolia-Application-Id": app_id,
        },
        json={
            "appID": app_id,
            "apiKey": api_key,
            "requests": [{"indexName": "Job", "params": params}],
        },
    )


def _first_result(response: dict[str, Any]) -> dict[str, Any]:
    results = response.get("results") or []
    if not results or not isinstance(results[0], dict):
        raise CakeSchemaWarning("Cake Algolia response missing first result")
    return results[0]


def fetch_algolia_records(app_id: str, api_key: str, *, max_pages: int = CAKE_ALGOLIA_MAX_PAGES) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    first_response = fetch_algolia_page(app_id, api_key, 0)
    first_result = _first_result(first_response)
    total_pages = int(first_result.get("nbPages") or 0)
    page_count = min(total_pages, max_pages)
    pages = [first_response]
    records = [record for record in first_result.get("hits", []) if isinstance(record, dict)]

    for page in range(1, page_count):
        response = fetch_algolia_page(app_id, api_key, page)
        result = _first_result(response)
        pages.append(response)
        records.extend(record for record in result.get("hits", []) if isinstance(record, dict))

    return records, pages


def fetch_records() -> tuple[list[dict[str, Any]] | list[tuple[str, dict[str, Any]]], str, list[dict[str, Any]], str | None]:
    text = get_text(CAKE_TAIWAN_IT_URL, timeout=45)
    next_data = parse_next_data(text)
    try:
        app_id, api_key = extract_algolia_credentials(next_data)
        records, pages = fetch_algolia_records(app_id, api_key)
        return records, text, pages, None
    except Exception as exc:
        warning = f"Cake Algolia fetch failed; falling back to __NEXT_DATA__: {exc}"
        return extract_bootstrap_records(next_data), text, [], warning


def run() -> pd.DataFrame:
    ensure_data_dirs()
    fetched_at = datetime.now(UTC).isoformat()
    try:
        records, raw_text, raw_pages, warning = fetch_records()
    except CakeSchemaWarning as warning:
        warning_path = RAW_DIR / "cake_warning.txt"
        warning_path.write_text(str(warning), encoding="utf-8")
        df = pd.DataFrame()
        df.to_parquet(PROCESSED_DIR / "cake_taiwan_it.parquet", index=False)
        return df

    (RAW_DIR / "cake_taiwan_it_bootstrap.html").write_text(raw_text or "", encoding="utf-8")
    (RAW_DIR / "cake_taiwan_it_algolia.json").write_text(json.dumps(raw_pages, ensure_ascii=False, indent=2), encoding="utf-8")
    if warning:
        (RAW_DIR / "cake_warning.txt").write_text(warning, encoding="utf-8")
    df = normalize_cake_jobs(records, fetched_at=fetched_at)
    df.to_parquet(PROCESSED_DIR / "cake_taiwan_it.parquet", index=False)
    return df


def main() -> None:
    df = run()
    print(f"Wrote {len(df):,} Cake Taiwan IT jobs")


if __name__ == "__main__":
    main()
