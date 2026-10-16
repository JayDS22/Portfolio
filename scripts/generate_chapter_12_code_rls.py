#!/usr/bin/env python3
"""
Generate the chapter-12 RLS session code card.

Styled code card (dark panel, syntax-ish coloring) showing the TypeScript
helper that opens a per-request Postgres transaction, pins the session
identity via SET LOCAL, and hands the transaction back to the workers so
their queries route through the RLS-filtered agent_session role.

Output:
  images/project-heros/chapter-12-code-rls.png  (1200 x 680, transparent canvas)

Run from repo root:
  python3 scripts/generate_chapter_12_code_rls.py
"""
from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

# --- palette (shared across all chapter-12 artifacts) ------------------------
BG_PANEL = "#1a2236"
BORDER = "#2a3148"
LINENO = "#8899aa"
PUNCT = "#8899aa"
COMMENT = "#8899aa"
IDENT = "#f7f8fb"
KEYWORD = "#b88746"
STRING = "#a3d9a5"

MONO_FAMILY = ["JetBrains Mono", "SF Mono", "DejaVu Sans Mono", "monospace"]

# TypeScript keywords to colorize (bronze).
KEYWORDS = {"export", "function", "return", "async", "await", "const"}

# --- source lines (14 lines, matching spec) ----------------------------------
# Each line is a list of (text, kind) tokens. kind in:
#   "kw"     bronze keyword
#   "str"    soft green string / template literal content
#   "cmt"    muted gray comment
#   "id"     near-white identifier / function / variable
#   "pn"     muted punctuation / operators
LINES: list[list[tuple[str, str]]] = [
    [("// lib/db/session.ts", "cmt")],
    [
        ("export", "kw"), (" ", "pn"), ("function", "kw"), (" ", "pn"),
        ("makeSession", "id"), ("(", "pn"), ("req", "id"), (": ", "pn"),
        ("Request", "id"), (") {", "pn"),
    ],
    [
        ("  ", "pn"), ("const", "kw"), (" ", "pn"), ("user", "id"), (" = ", "pn"),
        ("requireUser", "id"), ("(", "pn"), ("req", "id"), (");", "pn"),
        ("                    ", "pn"),
        ("// session-token -> user", "cmt"),
    ],
    [
        ("  ", "pn"), ("return", "kw"), (" ", "pn"), ("db", "id"), (".", "pn"),
        ("transaction", "id"), ("(", "pn"), ("async", "kw"), (" (", "pn"),
        ("tx", "id"), (") => {", "pn"),
    ],
    [
        ("    ", "pn"), ("await", "kw"), (" ", "pn"), ("tx", "id"), (".", "pn"),
        ("execute", "id"), ("(", "pn"), ("sql", "id"), ("`", "str"),
    ],
    [("      SET LOCAL app.current_user_id = ${", "str"),
     ("user", "id"), (".", "pn"), ("id", "id"),
     ("};", "str")],
    [("      SET LOCAL ROLE agent_session;", "str")],
    [("    `", "str"), (");", "pn")],
    [
        ("    ", "pn"), ("return", "kw"), (" ", "pn"), ("tx", "id"), (";", "pn"),
    ],
    [("  });", "pn")],
    [("}", "pn")],
    [("", "pn")],
    [("// Workers run queries through makeSession(req), never the service account.", "cmt")],
    [("// RLS policies on billing, docs, and events tables filter by current_user_id.", "cmt")],
]


def color_for(kind: str) -> str:
    return {
        "kw": KEYWORD,
        "str": STRING,
        "cmt": COMMENT,
        "id": IDENT,
        "pn": PUNCT,
    }[kind]


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    out_dir = repo_root / "images" / "project-heros"
    out_dir.mkdir(parents=True, exist_ok=True)
    png_path = out_dir / "chapter-12-code-rls.png"

    # 1200 x 680 at dpi=100
    fig = plt.figure(figsize=(12.0, 6.8), dpi=100)
    fig.patch.set_alpha(0.0)

    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1200)
    ax.set_ylim(0, 680)
    ax.set_axis_off()
    ax.patch.set_alpha(0.0)

    # Full-bleed dark panel with 20px rounded corners and 1px border.
    panel = FancyBboxPatch(
        (6, 6),
        1200 - 12, 680 - 12,
        boxstyle="round,pad=0,rounding_size=20",
        linewidth=1.0,
        edgecolor=BORDER,
        facecolor=BG_PANEL,
        joinstyle="round",
    )
    ax.add_patch(panel)

    # Internal padding ~48px per spec.
    pad = 48
    # Line numbers in a left margin, body text to the right.
    lineno_x = pad
    body_x = pad + 60      # ~60px gutter after line numbers
    body_pt = 14           # fits 14 lines comfortably in 680 - 2*pad
    line_h = 36            # vertical spacing between lines (px)

    # Top of first line sits 'pad' below panel top.
    top_y = 680 - pad - 6

    for i, tokens in enumerate(LINES):
        y = top_y - i * line_h

        # Line number (1-indexed), muted gray, right-aligned in the gutter.
        ax.text(
            lineno_x + 40, y, f"{i + 1:>2}",
            color=LINENO,
            family=MONO_FAMILY,
            fontsize=body_pt,
            va="top", ha="right",
        )

        # Walk tokens left-to-right, placing each with its color.
        # We use character-advance based on fontsize * ~0.6 for mono width.
        # Mono character cell at 14pt / dpi=100 ~= 11.7px wide (empirically ~8.4px/char at 14pt).
        char_w = 8.4
        cursor_px = 0
        for text, kind in tokens:
            if not text:
                continue
            # Split "keyword" tokens into finer coloring if an "id" slips a reserved
            # word through; current LINES already pre-split so this is a no-op.
            color = color_for(kind)
            ax.text(
                body_x + cursor_px, y, text,
                color=color,
                family=MONO_FAMILY,
                fontsize=body_pt,
                va="top", ha="left",
            )
            cursor_px += len(text) * char_w

    plt.rcParams["savefig.transparent"] = True
    fig.savefig(png_path, dpi=100, transparent=True,
                facecolor="none", edgecolor="none")
    plt.close(fig)

    assert png_path.exists() and png_path.stat().st_size > 0, f"missing/empty: {png_path}"
    print(f"{png_path}  {png_path.stat().st_size} bytes")


# ponytail: character-advance width (8.4px/char at 14pt) is a mono-font
# heuristic, not a true text-metric measurement. Good enough for this card;
# upgrade to fig.canvas.get_renderer() + text.get_window_extent() if the
# source changes shape and columns start drifting.
if __name__ == "__main__":
    main()
