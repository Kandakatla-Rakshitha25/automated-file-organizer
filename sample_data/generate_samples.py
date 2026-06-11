"""
generate_samples.py
-------------------
Creates sample files in watch_folder/ to demo the organizer.
Run this once before starting the organizer.
"""

import os
import csv
import random
import shutil
from pathlib import Path

BASE = Path(__file__).parent.parent
WATCH = BASE / "watch_folder"

# ── sample CSV files ──────────────────────────────────────────────────────────
HEADERS = ["id", "name", "department", "salary", "join_date", "status"]
DEPARTMENTS = ["Engineering", "Marketing", "HR", "Finance", "Operations", None]
STATUSES = ["Active", "Inactive", "On Leave", "", None]

def make_csv(filename: str, rows: int = 30):
    path = WATCH / filename
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        for i in range(1, rows + 1):
            # intentionally add nulls / duplicates for cleaning demo
            writer.writerow([
                i,
                f"Employee_{i}" if i % 7 != 0 else None,
                random.choice(DEPARTMENTS),
                random.randint(30_000, 120_000) if i % 5 != 0 else None,
                f"202{random.randint(0,4)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                random.choice(STATUSES),
            ])
        # add a duplicate row
        writer.writerow([1, "Employee_1", "Engineering", 75000, "2022-03-15", "Active"])
    print(f"  Created: {path.name}")

# ── dummy PDF placeholders (text files renamed .pdf) ─────────────────────────
def make_pdf(filename: str):
    path = WATCH / filename
    path.write_text(f"%PDF-1.4 placeholder — {filename}\n")
    print(f"  Created: {path.name}")

# ── dummy image placeholders (tiny files renamed .jpg / .png) ────────────────
def make_image(filename: str):
    path = WATCH / filename
    path.write_bytes(bytes([0xFF, 0xD8, 0xFF, 0xE0] + [0x00] * 12))  # minimal JPEG header
    print(f"  Created: {path.name}")

# ── misc files ────────────────────────────────────────────────────────────────
def make_misc(filename: str, content: str = "sample content"):
    path = WATCH / filename
    path.write_text(content)
    print(f"  Created: {path.name}")

if __name__ == "__main__":
    print("\n🗂  Generating sample files in watch_folder/ ...\n")
    make_csv("employees_q1.csv", 35)
    make_csv("sales_report.csv", 20)
    make_csv("inventory.csv", 25)
    make_pdf("invoice_001.pdf")
    make_pdf("contract_2024.pdf")
    make_pdf("annual_report.pdf")
    make_image("logo.jpg")
    make_image("banner.png")
    make_image("profile.jpeg")
    make_misc("readme.txt", "Project notes go here.")
    make_misc("config.json", '{"version": "1.0"}')
    make_misc("notes.docx", "Word doc placeholder")
    print(f"\n✅  {len(list(WATCH.glob('*')))} sample files ready.\n")
