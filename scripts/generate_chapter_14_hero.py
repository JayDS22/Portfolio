"""
Hero chart for post/chapter-14 (replit-agent-bench).

Horizontal grouped layout:
  - Agent name (left column)
  - Overall pass rate bar
  - 7-dot per-task indicator (filled = pass, outlined = fail)

Illustrative data. The real run lives in the repo.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle

INDIGO = "#1d4ed8"
BRONZE = "#b88746"
MUTED  = "#475467"
TEXT   = "#0c1424"
PALE   = "#ecf0f6"

for font_name in ["JetBrains Mono", "SF Mono", "DejaVu Sans Mono"]:
    try:
        font_manager.findfont(font_name, fallback_to_default=False)
        plt.rcParams["font.family"] = font_name
        break
    except Exception:
        continue

plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False
plt.rcParams["axes.edgecolor"] = MUTED
plt.rcParams["axes.labelcolor"] = TEXT
plt.rcParams["xtick.color"] = MUTED
plt.rcParams["ytick.color"] = MUTED
plt.rcParams["axes.titlecolor"] = TEXT
plt.rcParams["savefig.transparent"] = True


# Illustrative data: 7 tasks per agent, True = pass.
AGENTS = [
    ("Replit Agent",            [1, 1, 0, 1, 0, 1, 0]),
    ("Cursor + Sonnet 4.6",     [1, 1, 1, 1, 1, 0, 1]),
    ("Claude API (raw)",        [1, 1, 1, 0, 1, 1, 0]),
]
TASKS = ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]


def build_figure():
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    fig.patch.set_alpha(0)

    # Two axes: bar panel (left), dot matrix (right).
    gs = fig.add_gridspec(
        nrows=1, ncols=2,
        width_ratios=[1.35, 1.0],
        left=0.07, right=0.96, top=0.82, bottom=0.12,
        wspace=0.12,
    )
    ax_bar = fig.add_subplot(gs[0, 0])
    ax_dot = fig.add_subplot(gs[0, 1])

    for ax in (ax_bar, ax_dot):
        ax.patch.set_alpha(0)

    # ---- Bar panel ----
    names = [a[0] for a in AGENTS]
    rates = [sum(a[1]) / len(a[1]) * 100 for a in AGENTS]
    y_pos = list(range(len(AGENTS)))[::-1]  # top-down ordering

    ax_bar.barh(
        y_pos, rates,
        color=INDIGO, height=0.42,
        edgecolor="none", zorder=3,
    )
    # Faint reference track to 100
    ax_bar.barh(
        y_pos, [100] * len(AGENTS),
        color=PALE, height=0.42, zorder=2,
    )
    # Redraw real bars on top (barh order issue)
    ax_bar.barh(
        y_pos, rates,
        color=INDIGO, height=0.42,
        edgecolor="none", zorder=3,
    )

    for yi, name, r in zip(y_pos, names, rates):
        ax_bar.text(
            -2.0, yi, name,
            ha="right", va="center",
            fontsize=18, color=TEXT, fontweight="bold",
        )
        ax_bar.text(
            r + 1.5, yi, f"{r:.0f}%",
            ha="left", va="center",
            fontsize=18, color=BRONZE, fontweight="bold",
        )

    ax_bar.set_xlim(0, 112)
    ax_bar.set_ylim(-0.6, len(AGENTS) - 0.4)
    ax_bar.set_yticks([])
    ax_bar.set_xticks([0, 25, 50, 75, 100])
    ax_bar.set_xticklabels(["0", "25", "50", "75", "100"], fontsize=13)
    ax_bar.set_xlabel("Overall pass rate (%)", fontsize=15, color=MUTED, labelpad=12)
    ax_bar.tick_params(axis="x", length=0)
    ax_bar.spines["left"].set_visible(False)
    ax_bar.spines["bottom"].set_color(MUTED)
    ax_bar.spines["bottom"].set_linewidth(0.8)
    ax_bar.grid(axis="x", color=MUTED, alpha=0.12, linewidth=0.6, zorder=1)

    # ---- Dot matrix panel ----
    ax_dot.set_xlim(-0.6, len(TASKS) - 0.4)
    ax_dot.set_ylim(-0.6, len(AGENTS) - 0.4)
    ax_dot.set_aspect("equal")
    ax_dot.set_yticks([])
    ax_dot.set_xticks(range(len(TASKS)))
    ax_dot.set_xticklabels(TASKS, fontsize=13, color=MUTED)
    ax_dot.tick_params(axis="x", length=0, pad=10)
    ax_dot.spines["left"].set_visible(False)
    ax_dot.spines["bottom"].set_visible(False)

    for yi, (_, results) in zip(y_pos, AGENTS):
        for xi, passed in enumerate(results):
            if passed:
                c = Circle(
                    (xi, yi), radius=0.26,
                    facecolor=INDIGO, edgecolor="none", zorder=3,
                )
            else:
                c = Circle(
                    (xi, yi), radius=0.26,
                    facecolor="none", edgecolor=MUTED,
                    linewidth=1.4, zorder=3,
                )
            ax_dot.add_patch(c)

    ax_dot.text(
        (len(TASKS) - 1) / 2, len(AGENTS) - 0.1,
        "Per-task result (7 tasks)",
        ha="center", va="bottom",
        fontsize=15, color=MUTED,
    )

    # ---- Title + legend + caption ----
    fig.text(
        0.07, 0.92,
        "replit-agent-bench: coding-agent pass rate across 7 tasks",
        fontsize=26, color=TEXT, fontweight="bold",
        ha="left", va="top",
    )
    fig.text(
        0.07, 0.87,
        "Three agents, same prompts, same acceptance tests.",
        fontsize=16, color=MUTED, ha="left", va="top",
    )

    # Legend row (bottom)
    lx = 0.07
    ly = 0.05
    # Pass swatch
    ax_leg = fig.add_axes([0, 0, 1, 1])
    ax_leg.set_axis_off()
    ax_leg.set_xlim(0, 1)
    ax_leg.set_ylim(0, 1)
    ax_leg.patch.set_alpha(0)

    ax_leg.add_patch(Circle((lx, ly), 0.008, facecolor=INDIGO, edgecolor="none"))
    ax_leg.text(lx + 0.015, ly, "pass",
                fontsize=13, color=MUTED, va="center")

    ax_leg.add_patch(Circle((lx + 0.08, ly), 0.008,
                            facecolor="none", edgecolor=MUTED, linewidth=1.2))
    ax_leg.text(lx + 0.095, ly, "fail",
                fontsize=13, color=MUTED, va="center")

    fig.text(
        0.96, 0.05,
        "ILLUSTRATIVE. SEE REPO FOR LIVE RUN.",
        fontsize=12, color=BRONZE, ha="right", va="center",
        fontweight="bold", alpha=0.9,
    )

    return fig


def main():
    out_dir = Path(__file__).resolve().parent.parent / "images" / "project-heros"
    out_dir.mkdir(parents=True, exist_ok=True)

    fig = build_figure()
    png_path = out_dir / "chapter-14-hero.png"
    svg_path = out_dir / "chapter-14-hero.svg"

    fig.savefig(png_path, dpi=100, transparent=True,
                bbox_inches=None, pad_inches=0)
    fig.savefig(svg_path, transparent=True,
                bbox_inches=None, pad_inches=0)
    plt.close(fig)

    # Self-check: both files exist with reasonable size.
    assert png_path.exists(), f"missing {png_path}"
    assert svg_path.exists(), f"missing {svg_path}"
    png_sz = png_path.stat().st_size
    svg_sz = svg_path.stat().st_size
    assert png_sz > 20_000, f"PNG too small: {png_sz} bytes"
    assert svg_sz > 5_000,  f"SVG too small: {svg_sz} bytes"

    print(f"PNG: {png_path} ({png_sz:,} bytes)")
    print(f"SVG: {svg_path} ({svg_sz:,} bytes)")


if __name__ == "__main__":
    main()
