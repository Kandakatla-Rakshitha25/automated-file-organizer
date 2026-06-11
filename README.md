# 📁 Automated File Organizer & Report Generator

A lightweight Python RPA bot that scans a directory, sorts files into
structured sub-folders, cleans CSV data, generates summary reports, and
produces insight charts — all on a recurring schedule.

---

## Tech Stack
| Library | Role |
|---------|------|
| `os` / `shutil` / `pathlib` | File scanning, moving, path management |
| `pandas` | CSV cleaning, null handling, report export |
| `matplotlib` / `seaborn` | Bar charts, pie charts, visualisations |
| `schedule` | Recurring background job (lightweight RPA) |

---

## Project Structure

```
file_organizer/
│
├── watch_folder/          ← drop files here; organiser moves them
│   ├── PDFs/
│   ├── CSVs/
│   ├── Images/
│   └── Others/
│
├── reports/               ← cleaned CSVs + summary_report.csv (auto-created)
├── charts/                ← PNG charts (auto-created)
├── sample_data/           ← helpers to seed demo files
│
├── organizer.py           ← Stage 1: scan & move
├── data_processor.py      ← Stage 2: clean CSVs, export reports
├── visualizer.py          ← Stage 3: generate charts
├── scheduler.py           ← Orchestrator + schedule runner
└── requirements.txt
```

---

## Quick Start

### 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### 2 — Generate sample files (demo only)
```bash
python sample_data/generate_samples.py
```
This seeds `watch_folder/` with sample PDFs, CSVs, images, and misc files.

### 3a — Run once
```bash
python scheduler.py --once
```

### 3b — Run on a schedule (every N minutes)
```bash
python scheduler.py --interval 2    # default: every 2 minutes
```
Press **Ctrl + C** to stop.

---

## What Happens Each Run

```
Stage 1 — File Organiser
  Scans watch_folder/ (top level)
  Detects extension → assigns category (PDFs / CSVs / Images / Others)
  Moves file into matching sub-folder (safe rename on collision)
  Returns a structured log (list of dicts)

Stage 2 — Data Processor
  Reads every CSV in watch_folder/CSVs/
  Cleans: strips whitespace, normalises column names,
          drops duplicates, fills nulls (median / "Unknown")
  Exports:  <name>_cleaned.csv   → reports/
            summary_report.csv  → reports/

Stage 3 — Visualiser
  01_file_distribution.png  — bar chart: files per category
  02_category_pie.png        — pie chart: % share per category
  03_cleaning_stats.png      — grouped bar: raw vs clean rows per CSV
  04_size_by_category.png    — horizontal bar: KB per category
  All saved to charts/
```

---

## Extending the Project

| Goal | Where to edit |
|------|---------------|
| Add a new file category (e.g. Videos) | `organizer.py → CATEGORIES` |
| Change cleaning rules | `data_processor.py → _clean_dataframe()` |
| Add a new chart | `visualizer.py` — add a function, call it in `generate_all_charts()` |
| Change schedule interval | `scheduler.py --interval <minutes>` |
| Point to a different watch folder | `scheduler.py → full_pipeline()` → `run_organizer("your/path")` |

---

## Output Sample

```
reports/
  employees_q1_cleaned.csv
  sales_report_cleaned.csv
  inventory_cleaned.csv
  summary_report.csv          ← one row per CSV with cleaning statistics

charts/
  01_file_distribution.png
  02_category_pie.png
  03_cleaning_stats.png
  04_size_by_category.png
```
