from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.config import PROCESSED_DIR, ensure_data_dirs
from src.ingest import cake, meetjobs, one1111, taiwanjobs
from src.normalization import STANDARD_COLUMNS, standardize_dataframe


def build_dataset(*, skip_live_optional: bool = False) -> pd.DataFrame:
    ensure_data_dirs()
    frames: list[pd.DataFrame] = []

    taiwanjobs_df = taiwanjobs.run()
    frames.append(taiwanjobs_df)

    if not skip_live_optional:
        for name, runner in (("Cake", cake.run), ("Meet.jobs", meetjobs.run), ("1111", one1111.run)):
            try:
                source_df = runner()
            except Exception as exc:
                print(f"[warn] Optional source {name} failed: {exc}")
                source_df = pd.DataFrame(columns=STANDARD_COLUMNS)
            if not source_df.empty:
                frames.append(source_df)

    combined = standardize_dataframe(pd.concat(frames, ignore_index=True))
    combined = combined.drop_duplicates(subset=["source_platform", "source_url", "title", "company"])
    out_path = PROCESSED_DIR / "all_taiwan_jobs.parquet"
    combined.to_parquet(out_path, index=False)
    print(f"Wrote {len(combined):,} combined Taiwan jobs to {out_path}")
    return combined


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the SkillScope Taiwan-first processed dataset.")
    parser.add_argument("--skip-live-optional", action="store_true", help="Only ingest TaiwanJobs government data.")
    args = parser.parse_args()
    build_dataset(skip_live_optional=args.skip_live_optional)


if __name__ == "__main__":
    main()
