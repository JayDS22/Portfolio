"""Generate chapter-15 hero: cross-model scorecard heatmap.

Project: openai-evals-enterprise-pack (20 enterprise scenarios + 3 novel evals).
The heatmap tells the story that the three NOVEL evals surface failure modes
the enterprise scenarios miss, especially PII leakage via tool arguments.

ILLUSTRATIVE DATA. Repo has the measured scores.

Outputs:
    images/project-heros/chapter-15-hero.png  (1920x1080, transparent)
    images/project-heros/chapter-15-hero.svg
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap

# Shared palette for all 5 hero images.
INDIGO = "#1d4ed8"
BRONZE = "#b88746"
MUTED  = "#475467"
TEXT   = "#0c1424"
PALE   = "#ecf0f6"

# Prefer a mono face; fall back cleanly if none installed.
for font_name in ["JetBrains Mono", "SF Mono", "DejaVu Sans Mono"]:
    try:
        font_manager.findfont(font_name, fallback_to_default=False)
        plt.rcParams["font.family"] = font_name
        break
    except Exception:
        continue

plt.rcParams["savefig.transparent"] = True


# Indigo gradient: pale -> mid -> full indigo.
# Intermediate stops picked so mid-range cells still read as "indigo family",
# not grey, and so the pale end has enough contrast for dark text.
CMAP = LinearSegmentedColormap.from_list(
    "indigo_scorecard",
    [
        (0.00, PALE),       # #ecf0f6
        (0.35, "#c7d2fe"),  # soft indigo
        (0.65, "#6366f1"),  # mid indigo
        (1.00, INDIGO),     # #1d4ed8
    ],
    N=256,
)


# Rows: 3 novel evals first, then 5 enterprise scenarios.
# PII row is the safety-critical one; it is colored bronze on the y-axis.
ROWS = [
    ("TOOL-USE TRAJECTORY",       "novel"),
    ("STREAMING CANCEL VALIDITY", "novel"),
    ("PII VIA TOOL ARGS",         "pii"),
    ("SQL AGENT ROUTING",         "enterprise"),
    ("SCHEMA DRIFT RECOVERY",     "enterprise"),
    ("DOC QA GROUNDING",          "enterprise"),
    ("TOOL CHAIN FIDELITY",       "enterprise"),
    ("STREAM REPLAY CORRECTNESS", "enterprise"),
]

COLS = ["CLAUDE SONNET 4.6", "CLAUDE OPUS 4.7", "GPT-4.X"]

# Illustrative pass-rate percentages.
# Story:
#   - Enterprise rows: all three models mostly 80-95, GPT-4.X slightly behind
#     on routing / schema drift (its common weak spot in practice).
#   - Novel rows expose real gaps:
#       * tool-use trajectory: GPT-4.X dips to mid-60s.
#       * streaming cancel validity: everyone drops into 60-80s;
#         Opus 4.7 wins, GPT-4.X worst.
#       * PII via tool args: THE SAFETY-CRITICAL ROW. All models struggle.
#         Opus best at 71, Sonnet 62, GPT-4.X 38 (fails open).
DATA = np.array([
    # Sonnet 4.6, Opus 4.7, GPT-4.X
    [81, 86, 64],   # tool-use trajectory
    [74, 83, 61],   # streaming cancel validity
    [62, 71, 38],   # PII via tool args    <-- bronze callout
    [92, 94, 85],   # SQL agent routing
    [87, 91, 79],   # schema drift recovery
    [90, 93, 88],   # doc QA grounding
    [89, 92, 83],   # tool chain fidelity
    [85, 89, 82],   # stream replay correctness
], dtype=float)

assert DATA.shape == (len(ROWS), len(COLS))


def text_color_for(value: float) -> str:
    """Dark text on pale cells, white on dark cells.

    Threshold picked so the mid-indigo band (around 60-70) reads with white.
    """
    return "white" if value >= 55 else TEXT


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    out_dir = repo_root / "images" / "project-heros"
    out_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
    fig.patch.set_alpha(0.0)
    ax.set_facecolor("none")

    # Vmin/vmax pin the color scale to 0..100 so values are comparable
    # across future heroes using the same cmap.
    im = ax.imshow(
        DATA,
        cmap=CMAP,
        vmin=0,
        vmax=100,
        aspect="auto",
    )

    # Thin cell borders.
    n_rows, n_cols = DATA.shape
    ax.set_xticks(np.arange(n_cols + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(n_rows + 1) - 0.5, minor=True)
    ax.grid(which="minor", color=PALE, linewidth=1.2)
    ax.tick_params(which="minor", bottom=False, left=False)

    # Primary ticks: no marks, just labels.
    ax.set_xticks(np.arange(n_cols))
    ax.set_yticks(np.arange(n_rows))
    ax.set_xticklabels(COLS, fontsize=15, color=TEXT, weight="bold")
    ax.set_yticklabels([r[0] for r in ROWS], fontsize=13, color=TEXT)
    ax.tick_params(axis="both", which="major", length=0, pad=10)

    # Highlight the PII row label in bronze.
    for tick_label, (_, kind) in zip(ax.get_yticklabels(), ROWS):
        if kind == "pii":
            tick_label.set_color(BRONZE)
            tick_label.set_weight("bold")

    # Put x labels on top (reads like a scorecard header).
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")

    # Hide spines; grid provides structure.
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Cell values with contrast-aware color.
    for i in range(n_rows):
        for j in range(n_cols):
            v = DATA[i, j]
            ax.text(
                j, i, f"{int(v)}",
                ha="center", va="center",
                fontsize=22, weight="bold",
                color=text_color_for(v),
            )

    # Title and subtitle.
    fig.text(
        0.5, 0.955,
        "CROSS-MODEL SCORECARD",
        ha="center", va="top",
        fontsize=22, color=TEXT, weight="bold",
    )
    fig.text(
        0.5, 0.918,
        "openai-evals-enterprise-pack  //  pass rate %, higher is better",
        ha="center", va="top",
        fontsize=13, color=MUTED,
    )

    # Bronze legend row for the safety-critical callout.
    fig.text(
        0.5, 0.08,
        "ROW IN BRONZE: SAFETY-CRITICAL EVAL (PII LEAK VIA TOOL ARGS)",
        ha="center", va="center",
        fontsize=12, color=BRONZE, weight="bold",
    )

    # Caption: required verbatim text.
    fig.text(
        0.5, 0.045,
        "ILLUSTRATIVE. SEE REPO FOR MEASURED RESULTS.",
        ha="center", va="center",
        fontsize=11, color=MUTED,
    )

    # Keep the heatmap breathing but not floating.
    plt.subplots_adjust(left=0.22, right=0.88, top=0.86, bottom=0.14)

    png_path = out_dir / "chapter-15-hero.png"
    svg_path = out_dir / "chapter-15-hero.svg"

    fig.savefig(png_path, dpi=100, transparent=True, bbox_inches=None)
    fig.savefig(svg_path, transparent=True, bbox_inches=None)
    plt.close(fig)

    for p in (png_path, svg_path):
        print(f"{p}  {p.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
