"""
organizer.py
------------
Scans watch_folder/, categorises every file by extension, moves it into
the matching sub-folder, and returns a structured log for reporting.
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime

# ── logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── category → extensions map ─────────────────────────────────────────────────
CATEGORIES: dict[str, list[str]] = {
    "PDFs":   [".pdf"],
    "CSVs":   [".csv"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".svg"],
    "Others": [],          # catch-all
}

def _resolve_category(suffix: str) -> str:
    """Return the folder name for a given file extension."""
    suffix = suffix.lower()
    for category, extensions in CATEGORIES.items():
        if suffix in extensions:
            return category
    return "Others"


def _ensure_dirs(watch_dir: Path) -> None:
    """Create sub-folders if they don't already exist."""
    for category in CATEGORIES:
        (watch_dir / category).mkdir(parents=True, exist_ok=True)


def _safe_move(src: Path, dst_dir: Path) -> Path:
    """
    Move *src* into *dst_dir*.
    If a file with the same name already exists, append a timestamp.
    Returns the final destination path.
    """
    dst = dst_dir / src.name
    if dst.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dst = dst_dir / f"{src.stem}_{ts}{src.suffix}"
    shutil.move(str(src), str(dst))
    return dst


def run_organizer(watch_dir: str | Path = "watch_folder") -> list[dict]:
    """
    Main entry-point.  Scans *watch_dir* (top level only), moves every
    qualifying file into its sub-folder, and returns a list of log records.

    Each record is a dict with keys:
        filename, extension, category, size_kb, status, timestamp, destination
    """
    watch_dir = Path(watch_dir).resolve()
    _ensure_dirs(watch_dir)

    records: list[dict] = []
    files = [p for p in watch_dir.iterdir() if p.is_file()]

    if not files:
        logger.info("No files found in %s — nothing to organise.", watch_dir)
        return records

    logger.info("Found %d file(s) in %s", len(files), watch_dir)

    for filepath in files:
        category  = _resolve_category(filepath.suffix)
        size_kb   = round(filepath.stat().st_size / 1024, 2)
        timestamp = datetime.now().isoformat(timespec="seconds")

        try:
            dst = _safe_move(filepath, watch_dir / category)
            status = "moved"
            logger.info("  ✔  %-30s  →  %s/", filepath.name, category)
        except Exception as exc:
            dst = filepath          # stays in place
            status = f"error: {exc}"
            logger.error("  ✘  %-30s  error: %s", filepath.name, exc)

        records.append({
            "filename":    filepath.name,
            "extension":   filepath.suffix.lower() or "(none)",
            "category":    category,
            "size_kb":     size_kb,
            "status":      status,
            "timestamp":   timestamp,
            "destination": str(dst),
        })

    moved = sum(1 for r in records if r["status"] == "moved")
    logger.info("Organiser complete — %d/%d file(s) moved.", moved, len(records))
    return records
