"""Generate chapter-14 code harness card.

Renders a styled Python code snippet (bench/runner.py) as a dark-panel PNG.
Pure matplotlib text rendering, no syntax highlighter library.

Output:
    images/project-heros/chapter-14-code-harness.png (1200x680)
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib import font_manager

# Palette.
PANEL = "#1a2236"
TEXT = "#f7f8fb"
MUTED = "#8899aa"
KEYWORD = "#b88746"
STRING = "#a3d9a5"
BUILTIN = "#88c0d0"

# Prefer JetBrains Mono.
for font_name in ["JetBrains Mono", "SF Mono", "DejaVu Sans Mono"]:
    try:
        font_manager.findfont(font_name, fallback_to_default=False)
        plt.rcParams["font.family"] = font_name
        break
    except Exception:
        continue

plt.rcParams["savefig.transparent"] = True

KEYWORDS = {"from", "import", "def", "return", "if", "for", "in", "as"}
BUILTINS = {"list", "dict", "Path", "time", "json", "yaml", "str", "int", "float", "print"}

# (text, color) tokens per line. Line numbers added automatically.
CODE_LINES = [
    [("# bench/runner.py", MUTED)],
    [("from", KEYWORD), (" pathlib ", TEXT), ("import", KEYWORD), (" ", TEXT), ("Path", BUILTIN)],
    [("import", KEYWORD), (" ", TEXT), ("yaml", BUILTIN), (", ", TEXT), ("json", BUILTIN), (", ", TEXT), ("time", BUILTIN)],
    [("from", KEYWORD), (" bench.agents ", TEXT), ("import", KEYWORD), (" REPLIT, CURSOR_SONNET, CLAUDE_API", TEXT)],
    [("", TEXT)],
    [("TASKS = ", TEXT), ("yaml", BUILTIN), (".safe_load(", TEXT), ("Path", BUILTIN), ("(", TEXT), ('"tasks/catalog.yaml"', STRING), (").read_text())", TEXT)],
    [("", TEXT)],
    [("def", KEYWORD), (" run_task(agent, task):", TEXT)],
    [("    t0 = ", TEXT), ("time", BUILTIN), (".monotonic()", TEXT)],
    [("    result = agent.solve(task.prompt, workdir=task.workdir)", TEXT)],
    [("    passed = task.score(result)   ", TEXT), ("# scripted test, no LLM judge", MUTED)],
    [("    ", TEXT), ("return", KEYWORD), (" {", TEXT)],
    [("        ", TEXT), ('"agent"', STRING), (": agent.name, ", TEXT), ('"task"', STRING), (": task.id, ", TEXT), ('"pass"', STRING), (": passed,", TEXT)],
    [("        ", TEXT), ('"seconds"', STRING), (": ", TEXT), ("time", BUILTIN), (".monotonic() - t0, ", TEXT), ('"tokens"', STRING), (": result.tokens,", TEXT)],
    [("    }", TEXT)],
    [("", TEXT)],
    [("if", KEYWORD), (" __name__ == ", TEXT), ('"__main__"', STRING), (":", TEXT)],
    [("    rows = [run_task(a, t) ", TEXT), ("for", KEYWORD), (" a ", TEXT), ("in", KEYWORD), (" [REPLIT, CURSOR_SONNET, CLAUDE_API]", TEXT)],
    [("                           ", TEXT), ("for", KEYWORD), (" t ", TEXT), ("in", KEYWORD), (" TASKS]", TEXT)],
    [("    ", TEXT), ("Path", BUILTIN), ("(", TEXT), ('"results.json"', STRING), (").write_text(", TEXT), ("json", BUILTIN), (".dumps(rows, indent=", TEXT), ("2", TEXT), ("))", TEXT)],
]


def render() -> Path:
    # Figure sized to 1200x680 at 100 dpi.
    fig = plt.figure(figsize=(12, 6.8), dpi=100)
    fig.patch.set_alpha(0.0)

    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1200)
    ax.set_ylim(0, 680)
    ax.axis("off")
    ax.invert_yaxis()

    # Dark rounded panel. 48px padding on all sides.
    panel = patches.FancyBboxPatch(
        (24, 24),
        1152,
        632,
        boxstyle="round,pad=0,rounding_size=18",
        linewidth=0,
        facecolor=PANEL,
    )
    ax.add_patch(panel)

    # Layout inside panel: 48px padding on all sides.
    code_x0 = 24 + 48
    code_y0 = 24 + 48
    line_height = 26
    gutter_width = 42  # line number column
    font_size = 12.5

    for i, tokens in enumerate(CODE_LINES):
        y = code_y0 + i * line_height
        # Line number in muted gray.
        ax.text(
            code_x0,
            y,
            f"{i + 1:>2}",
            color=MUTED,
            fontsize=font_size,
            family="monospace",
            va="top",
            ha="left",
        )
        # Walk tokens, placing each after the previous via a running pixel offset.
        # Monospace char width approximation at fontsize 12.5 is ~7.5px.
        char_w = 7.52
        offset = 0
        for text, color in tokens:
            if not text:
                continue
            ax.text(
                code_x0 + gutter_width + offset,
                y,
                text,
                color=color,
                fontsize=font_size,
                family="monospace",
                va="top",
                ha="left",
            )
            offset += len(text) * char_w

    out = Path("images/project-heros/chapter-14-code-harness.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100, transparent=True, bbox_inches=None, pad_inches=0)
    plt.close(fig)
    return out


if __name__ == "__main__":
    path = render()
    size = path.stat().st_size
    print(f"wrote {path} ({size} bytes)")
    assert size > 30_000, f"PNG too small: {size} bytes"
