"""
scheduler.py
------------
Wraps the full pipeline (organise → clean → visualise) in a `schedule`
job so it runs automatically at a defined interval.

Usage
─────
  python scheduler.py            # runs every 2 minutes (default)
  python scheduler.py --once     # run once immediately, then exit
  python scheduler.py --interval 5   # run every 5 minutes
"""

import argparse
import logging
import time
from datetime import datetime

import schedule

from organizer     import run_organizer
from data_processor import process_csvs
from visualizer    import generate_all_charts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def full_pipeline() -> None:
    """
    Execute the three-stage automation pipeline:
      1. File organiser  — scan & move files
      2. Data processor  — clean CSVs, export reports
      3. Visualiser      — generate charts
    """
    run_id = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info("=" * 60)
    logger.info("▶  Pipeline run started  [%s]", run_id)
    logger.info("=" * 60)

    # Stage 1 — organise files
    logger.info("── Stage 1: File Organiser ──")
    records = run_organizer("watch_folder")

    # Stage 2 — clean CSVs
    logger.info("── Stage 2: Data Processor ──")
    summary_df = process_csvs()

    # Stage 3 — charts
    logger.info("── Stage 3: Visualiser ──")
    chart_paths = generate_all_charts(records, summary_df)

    # summary
    logger.info("=" * 60)
    logger.info("✅  Pipeline complete")
    logger.info("   Files processed : %d", len(records))
    logger.info("   Charts generated: %d", len(chart_paths))
    logger.info("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(description="File Organiser Scheduler")
    parser.add_argument(
        "--once", action="store_true",
        help="Run the pipeline once and exit (no scheduling).",
    )
    parser.add_argument(
        "--interval", type=int, default=2, metavar="MINUTES",
        help="How often to run the pipeline (default: 2 minutes).",
    )
    args = parser.parse_args()

    if args.once:
        full_pipeline()
        return

    logger.info("Scheduler started — pipeline runs every %d minute(s).", args.interval)
    logger.info("Press Ctrl+C to stop.\n")

    # run immediately on start, then on schedule
    full_pipeline()
    schedule.every(args.interval).minutes.do(full_pipeline)

    try:
        while True:
            schedule.run_pending()
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user.")


if __name__ == "__main__":
    main()
