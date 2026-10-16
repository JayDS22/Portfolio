#!/usr/bin/env python3
"""
Generate the chapter-12 hero image: a styled terminal / server-log trace for
the "enterprise-assistant-reference" case study.

Output:
  images/project-heros/chapter-12-hero.png  (1920 x 1080, transparent canvas)
  images/project-heros/chapter-12-hero.svg

The terminal panel itself is dark; the surrounding figure canvas is
transparent so the hero drops cleanly onto any page background.

Run from repo root:
  python3 scripts/generate_chapter_12_hero.py
"""
from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# Silence per-text findfont warnings when the preferred mono fonts are not
# installed. Fallback resolution still works via the family list.
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

# --- palette (shared across the 5 hero images) --------------------------------
BG_PANEL = "#1a2236"       # terminal panel background
BORDER = "#2a3148"         # 1px panel border
TIMESTAMP = "#8899aa"      # muted gray timestamps
COMPONENT = "#1d4ed8"      # orch.*, worker.* component names (indigo)
BODY = "#f7f8fb"           # near-white body text
RLS = "#b88746"            # bronze: RLS annotation line
CAPTION = "#475467"        # muted caption below panel

# JetBrains Mono preferred, SF Mono fallback, DejaVu Sans Mono last.
# matplotlib will walk the family list and use the first installed match.
MONO_FAMILY = ["JetBrains Mono", "SF Mono", "DejaVu Sans Mono", "monospace"]

# --- log content (verbatim per spec) ------------------------------------------
# Each entry: (timestamp, component, body_lines, is_rls)
# body_lines is a list so the SQL block can wrap onto a continuation line
# without a timestamp/component prefix. is_rls colors the whole body in bronze.
LOG = [
    ("[12:04:03.221]", "orch.route",
     ['{ intent: "lookup_customer_billing", session: s_a3f2e9 }'], False),
    ("[12:04:03.287]", "worker.ret",
     ["retrieving customer context from vector store"], False),
    ("[12:04:03.891]", "worker.sql",
     ["SELECT b.* FROM billing b WHERE b.customer_id = $1"], False),
    ("",               "",
     ["-- RLS policy enforced: session_user = s_a3f2e9"], True),
    ("[12:04:04.102]", "worker.sql",
     ["rows: 12  (RLS filtered from 2,847 raw)"], False),
    ("[12:04:04.198]", "worker.out",
     ["composing response (schema: BillingSummary)"], False),
    ("[12:04:04.456]", "orch.reply",
     ["200 OK  (chain: orch -> ret -> sql -> out)"], False),
]


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    out_dir = repo_root / "images" / "project-heros"
    out_dir.mkdir(parents=True, exist_ok=True)
    png_path = out_dir / "chapter-12-hero.png"
    svg_path = out_dir / "chapter-12-hero.svg"

    # 1920 x 1080 at dpi=100
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    fig.patch.set_alpha(0.0)  # transparent canvas

    # Use the whole figure as a unit square so coordinates are easy.
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1920)
    ax.set_ylim(0, 1080)
    ax.set_axis_off()
    ax.patch.set_alpha(0.0)

    # --- terminal panel geometry ---------------------------------------------
    # Sized to actually fit the content: 7 log rows at ~56px line height plus
    # 2 * pad vertical padding ≈ 500px. Width widened to 1720 so the longest
    # row (`{ intent: "lookup_customer_billing", session: s_a3f2e9 }`) does
    # not spill off the right edge.
    panel_w = 1720
    panel_h = 520
    panel_x = (1920 - panel_w) / 2        # 100
    panel_y = (1080 - panel_h) / 2 + 30   # a little above center; caption sits below
    pad = 60                               # internal padding (per spec: generous ~60px)

    panel = FancyBboxPatch(
        (panel_x, panel_y),
        panel_w, panel_h,
        boxstyle="round,pad=0,rounding_size=12",
        linewidth=1.0,
        edgecolor=BORDER,
        facecolor=BG_PANEL,
        joinstyle="round",
    )
    ax.add_patch(panel)

    # --- log lines ------------------------------------------------------------
    # Font sizing: at 19.2in / 1920px, matplotlib fontsize is in points
    # (1 pt = 1/72 in). dpi=100 => 1 pt ≈ 1.389 px. Target ~28–36 source-pixel
    # text => ~20–26 pt. We use 22 pt body, which measures ~30 px tall.
    body_pt = 22
    line_h = 56  # vertical pixel spacing between log lines (comfortable)

    # Column anchors inside the panel. Tightened so the widest body line fits
    # inside panel_w - 2*pad = 1600px at 22pt mono.
    ts_x = panel_x + pad
    comp_x = panel_x + pad + 290
    body_x = panel_x + pad + 500

    # Start text near top of panel. Top of first line of text sits
    # 'pad' below panel top edge.
    text_top_y = panel_y + panel_h - pad - 10  # minor nudge for baseline

    for i, (ts, comp, body_lines, is_rls) in enumerate(LOG):
        y = text_top_y - i * line_h

        if ts:
            ax.text(
                ts_x, y, ts,
                color=TIMESTAMP,
                family=MONO_FAMILY,
                fontsize=body_pt,
                va="top", ha="left",
            )
        if comp:
            ax.text(
                comp_x, y, comp,
                color=COMPONENT,
                family=MONO_FAMILY,
                fontsize=body_pt,
                fontweight="bold",
                va="top", ha="left",
            )

        for j, line in enumerate(body_lines):
            ax.text(
                body_x, y - j * line_h, line,
                color=RLS if is_rls else BODY,
                family=MONO_FAMILY,
                fontsize=body_pt,
                va="top", ha="left",
            )

    # --- caption below panel --------------------------------------------------
    caption_y = panel_y - 48
    ax.text(
        1920 / 2, caption_y,
        "ILLUSTRATIVE TRACE. SEE REPO FOR LIVE DEMO ON FLY.IO.",
        color=CAPTION,
        family=MONO_FAMILY,
        fontsize=16,
        va="top", ha="center",
    )

    # --- save ----------------------------------------------------------------
    plt.rcParams["savefig.transparent"] = True
    fig.savefig(png_path, dpi=100, transparent=True,
                facecolor="none", edgecolor="none")
    fig.savefig(svg_path, transparent=True,
                facecolor="none", edgecolor="none")
    plt.close(fig)

    for p in (png_path, svg_path):
        assert p.exists() and p.stat().st_size > 0, f"missing/empty: {p}"
        print(f"{p}  {p.stat().st_size} bytes")


# ponytail: self-check runs as part of main() via asserts above.
# No separate test file; the generated files are the artifact and the asserts
# fail-fast if matplotlib produces zero-byte output.
if __name__ == "__main__":
    main()
