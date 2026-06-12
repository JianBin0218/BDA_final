from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urljoin

import pandas as pd
import urllib3
from bs4 import BeautifulSoup

from src.config import ONE1111_KEYWORDS, ONE1111_MAX_PAGES_PER_KEYWORD, ONE1111_SEARCH_URL, PROCESSED_DIR, RAW_DIR, ensure_data_dirs
from src.http import get_text
from src.normalization import normalize_one1111


def fetch_page(keyword: str, page: int) -> str:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    return get_text(
        ONE1111_SEARCH_URL,
        timeout=45,
        params={"ks": keyword, "page": page, "col": "ab", "sort": "desc"},
        verify=False,
    )


def parse_records(html: str, *, keyword: str, page: int) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")
    records = []
    seen_urls = set()

    for link in soup.select("a[href*='/job/']"):
        title = link.get_text(" ", strip=True)
        href = link.get("href", "")
        if not title or not href:
            continue
        url = urljoin("https://www.1111.com.tw", href.split("?", 1)[0])
        if url in seen_urls:
            continue
        seen_urls.add(url)

        card = link.find_parent(["article", "section", "div", "li"]) or link.parent
        card_text = card.get_text(" ", strip=True) if card else title
        records.append(
            {
                "title": title,
                "url": url,
                "snippet": card_text,
                "keyword": keyword,
                "page": page,
            }
        )

    return records


def fetch_records(
    *,
    keywords: list[str] | None = None,
    max_pages_per_keyword: int = ONE1111_MAX_PAGES_PER_KEYWORD,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records = []
    snapshots = []
    for keyword in keywords or ONE1111_KEYWORDS:
        for page in range(1, max_pages_per_keyword + 1):
            html = fetch_page(keyword, page)
            page_records = parse_records(html, keyword=keyword, page=page)
            snapshots.append(
                {
                    "keyword": keyword,
                    "page": page,
                    "record_count": len(page_records),
                    "html": html,
                }
            )
            records.extend(page_records)
            if not page_records:
                break
    return records, snapshots


def run() -> pd.DataFrame:
    ensure_data_dirs()
    fetched_at = datetime.now(UTC).isoformat()
    records, snapshots = fetch_records()
    (RAW_DIR / "1111_taiwan_search_pages.json").write_text(json.dumps(snapshots, ensure_ascii=False, indent=2), encoding="utf-8")
    df = normalize_one1111(records, fetched_at=fetched_at)
    df.to_parquet(PROCESSED_DIR / "1111_taiwan.parquet", index=False)
    return df


def main() -> None:
    df = run()
    print(f"Wrote {len(df):,} 1111 Taiwan CS/IT jobs")


if __name__ == "__main__":
    main()
