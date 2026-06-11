"""
visualizer.py
-------------
Generates charts from organizer + processor results:
  1. Bar chart  — file count per category
  2. Pie chart  — % share by category
  3. Bar chart  — data-cleaning stats (rows before vs after) per CSV
  4. Horizontal bar — file sizes per category
Saves all charts to charts/.
"""

import logging
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")            # non-interactive backend (safe for scripts)
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

logger = logging.getLogger(__name__)

BASE_DIR   = Path(__file__).parent
CHARTS_DIR = BASE_DIR / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# ── shared theme ──────────────────────────────────────────────────────────────
PALETTE    = ["#4F86C6", "#F4A261", "#2EC4B6", "#E76F51", "#A8DADC"]
FONT_COLOR = "#1a1a2e"
BG_COLOR   = "#F8F9FA"

sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams.update({
    "figure.facecolor": BG_COLOR,
    "axes.facecolor":   BG_COLOR,
    "axes.edgecolor":   "#cccccc",
    "axes.titlepad":    14,
    "axes.titlesize":   14,
    "axes.titleweight": "bold",
    "axes.titlecolor":  FONT_COLOR,
    "axes.labelcolor":  FONT_COLOR,
    "xtick.color":      FONT_COLOR,
    "ytick.color":      FONT_COLOR,
    "text.color":       FONT_COLOR,
    "grid.color":       "#e0e0e0",
    "grid.linestyle":   "--",
})


# ── chart helpers ─────────────────────────────────────────────────────────────

def _save(fig: plt.Figure, name: str) -> Path:
    path = CHARTS_DIR / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("  Chart saved → %s", path.name)
    return path


def chart_file_distribution(records: list[dict]) -> Path | None:
    """Bar chart: number of files moved per category."""
    if not records:
        logger.warning("No records — skipping file-distribution chart.")
        return None

    df = pd.DataFrame(records)
    counts = df["category"].value_counts().reset_index()
    counts.columns = ["category", "count"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(
        counts["category"], counts["count"],
        color=PALETTE[:len(counts)], edgecolor="white", linewidth=0.8, width=0.55,
    )
    ax.bar_label(bars, padding=4, fontsize=11, fontweight="bold")
    ax.set_title("Files Organised by Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("File Count")
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.margins(y=0.15)
    fig.tight_layout()
    return _save(fig, "01_file_distribution.png")


def chart_category_pie(records: list[dict]) -> Path | None:
    """Pie chart: percentage share of each category."""
    if not records:
        return None

    df = pd.DataFrame(records)
    counts = df["category"].value_counts()

    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=PALETTE[:len(counts)],
        startangle=140,
        pctdistance=0.82,
        wedgeprops=dict(linewidth=1.5, edgecolor="white"),
    )
    for at in autotexts:
        at.set_fontsize(10)
        at.set_fontweight("bold")
    ax.set_title("File Distribution — Category Share")
    fig.tight_layout()
    return _save(fig, "02_category_pie.png")


def chart_cleaning_stats(summary_df: pd.DataFrame) -> Path | None:
    """Grouped bar chart: raw rows vs clean rows per CSV file."""
    if summary_df is None or summary_df.empty:
        logger.warning("No summary data — skipping cleaning-stats chart.")
        return None

    df = summary_df[["source", "raw_rows", "clean_rows"]].copy()
    df = df.melt(id_vars="source", var_name="stage", value_name="rows")

    fig, ax = plt.subplots(figsize=(9, 5))
    bar_palette = {"raw_rows": "#4F86C6", "clean_rows": "#2EC4B6"}
    sns.barplot(data=df, x="source", y="rows", hue="stage",
                palette=bar_palette, edgecolor="white", ax=ax)

    for container in ax.containers:
        ax.bar_label(container, padding=3, fontsize=9, fontweight="bold")

    ax.set_title("CSV Cleaning — Rows Before vs After")
    ax.set_xlabel("File")
    ax.set_ylabel("Row Count")
    ax.legend(title="Stage", labels=["Raw rows", "Clean rows"])
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.margins(y=0.15)
    fig.tight_layout()
    return _save(fig, "03_cleaning_stats.png")


def chart_size_by_category(records: list[dict]) -> Path | None:
    """Horizontal bar chart: total KB per category."""
    if not records:
        return None

    df = pd.DataFrame(records)
    size_df = df.groupby("category")["size_kb"].sum().sort_values(ascending=True).reset_index()

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.barh(
        size_df["category"], size_df["size_kb"],
        color=PALETTE[:len(size_df)], edgecolor="white", height=0.5,
    )
    ax.bar_label(bars, fmt="%.2f KB", padding=4, fontsize=10)
    ax.set_title("Total File Size per Category")
    ax.set_xlabel("Size (KB)")
    ax.set_ylabel("")
    ax.margins(x=0.2)
    fig.tight_layout()
    return _save(fig, "04_size_by_category.png")


# ── public API ────────────────────────────────────────────────────────────────

def generate_all_charts(records: list[dict], summary_df: pd.DataFrame) -> list[Path]:
    """Call all chart functions and return a list of saved paths."""
    logger.info("Generating charts …")
    paths = [
        chart_file_distribution(records),
        chart_category_pie(records),
        chart_cleaning_stats(summary_df),
        chart_size_by_category(records),
    ]
    saved = [p for p in paths if p is not None]
    logger.info("%d chart(s) saved to %s/", len(saved), CHARTS_DIR)
    return saved
