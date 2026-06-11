"""
data_processor.py
-----------------
Reads every CSV that was moved into watch_folder/CSVs/, cleans it
(nulls, duplicates, whitespace), and exports:
  • an individual cleaned CSV per file
  • a combined summary report (reports/summary_report.csv)
"""

import logging
from pathlib import Path
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)

# ── paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
CSV_DIR     = BASE_DIR / "watch_folder" / "CSVs"
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# ── helpers ───────────────────────────────────────────────────────────────────

def _clean_dataframe(df: pd.DataFrame, source_name: str) -> tuple[pd.DataFrame, dict]:
    """
    Apply a standard cleaning pipeline and return (cleaned_df, stats_dict).

    Cleaning steps
    ──────────────
    1. Strip leading/trailing whitespace from string columns.
    2. Normalise column names to snake_case.
    3. Drop fully duplicate rows.
    4. Fill remaining nulls in numeric columns with column median.
    5. Fill remaining nulls in object columns with "Unknown".
    """
    stats = {
        "source":          source_name,
        "raw_rows":        len(df),
        "raw_cols":        len(df.columns),
        "null_cells_before": int(df.isnull().sum().sum()),
        "duplicate_rows":  int(df.duplicated().sum()),
    }

    # 1 — strip strings
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda c: c.str.strip())

    # 2 — normalise column names
    df.columns = (
        df.columns.str.strip()
                  .str.lower()
                  .str.replace(r"\s+", "_", regex=True)
                  .str.replace(r"[^\w]", "", regex=True)
    )

    # 3 — drop duplicates
    df = df.drop_duplicates()

    # 4 — numeric nulls → median
    num_cols = df.select_dtypes(include="number").columns
    for col in num_cols:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())

    # 5 — string nulls → "Unknown"
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].fillna("Unknown")

    stats["clean_rows"]         = len(df)
    stats["null_cells_after"]   = int(df.isnull().sum().sum())
    stats["rows_removed"]       = stats["raw_rows"] - stats["clean_rows"]
    stats["cleaned_at"]         = datetime.now().isoformat(timespec="seconds")

    return df, stats


def process_csvs() -> pd.DataFrame:
    """
    Iterate over every CSV in CSV_DIR, clean it, save a cleaned copy,
    and accumulate a summary.  Returns a summary DataFrame (one row per file).
    """
    csv_files = sorted(CSV_DIR.glob("*.csv"))

    if not csv_files:
        logger.warning("No CSV files found in %s.", CSV_DIR)
        return pd.DataFrame()

    logger.info("Processing %d CSV file(s) …", len(csv_files))
    summary_rows: list[dict] = []

    for csv_path in csv_files:
        logger.info("  Reading: %s", csv_path.name)
        try:
            df = pd.read_csv(csv_path)
        except Exception as exc:
            logger.error("  Could not read %s: %s", csv_path.name, exc)
            continue

        cleaned_df, stats = _clean_dataframe(df, csv_path.stem)

        # save cleaned file
        out_path = REPORTS_DIR / f"{csv_path.stem}_cleaned.csv"
        cleaned_df.to_csv(out_path, index=False)
        logger.info("  ✔  Cleaned → %s", out_path.name)

        summary_rows.append(stats)

    if not summary_rows:
        return pd.DataFrame()

    summary_df = pd.DataFrame(summary_rows)

    # export combined summary
    summary_path = REPORTS_DIR / "summary_report.csv"
    summary_df.to_csv(summary_path, index=False)
    logger.info("Summary report → %s", summary_path)

    return summary_df
