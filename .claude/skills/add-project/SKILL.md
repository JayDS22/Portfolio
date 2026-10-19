---
name: add-project
description: Scaffold a new case-study chapter in Jay's Portfolio repo at /Users/DELL/Documents/Portfolio (or wherever the repo lives). Produces a chapter page, finds and installs a real tech-savvy thumbnail (never a hand-crafted SVG), adds inline figures, wires the card into /post/ listing in chronological reverse order, considers home-featured placement, and visually verifies via shot-scraper before commit. Triggered only inside the Portfolio repo when the user explicitly says "/add-project", "scaffold a new case study", "add new case-study chapter", or "add chapter N to the portfolio". Does NOT fire on bare "add project" or "new chapter" (too generic for other contexts).
---

# Add a project to Jay's Portfolio

Encoded from a long iterative session that reinvented itself multiple times. The rules in this skill are the ones hard-earned, not the ones that seemed reasonable at the start. Read the anti-patterns section first.

## Hard rules (anti-patterns — do not repeat)

These failed in session on 2026-10-16/17 and must not be re-attempted:

- **No hand-authored SVG thumbnails.** Every SVG thumb we shipped got rejected ("fuck all SVG", "look AI-generated"). Only real polished graphics belong in the `/post/` listing thumbnail and home featured card. SVG is fine for inline figures inside the chapter body.
- **No `[TODO: measured number]` or any TODO fragment on the live site.** Fill every placeholder with real-or-illustrative content before the first push. Grep for `TODO` and `[TODO` in every chapter file before commit.
- **No fabricated metrics.** If you have no measured number, either describe methodology without the number, or mark the number explicitly as "illustrative" in-image and in-caption.
- **No AI-generated stock images.** Avoid Unsplash post-2023 renders, Pexels AI feeds. Prefer: vendor blog hero graphics (Anthropic, OpenAI), live product screenshots (SWE-bench, Chatbot Arena), Wikimedia Commons real photos, Taylor Vick / early-era Unsplash hardware photos.
- **No em-dashes anywhere.** Not in prose, not in commit messages, not in alt text. Use periods, commas, colons, parentheses. The portfolio has been systematically scrubbed; do not re-introduce.
- **No `Co-Authored-By: Claude` trailer** on commits. The user has banned AI-attribution markers from this repo. Pass `--no-gpg-sign` is fine (user already has config).
- **No AI-tell phrases.** No "Great question", "I'd be happy to", "Let me know if you need anything else" in prose or commit messages.
- **No `git push` without `git pull --rebase -X theirs origin main` first.** The `.github/workflows/sync-github-projects.yml` cron writes to main daily; local pushes always hit remote-ahead and need rebase.
- **No shipping without visual verification.** HTTP 200 does not mean the page looks right. Use shot-scraper + Read tool to view each affected page.

## The aesthetic bar

Reference image: `images/llm-serving.png`. Dark navy background, iconic shapes, dashed connections, high visual density, hand-designed feel. Any new thumbnail should feel of a piece with it. The chapter-8 LLM-serving thumbnail is the aesthetic the user has repeatedly held up as the target.

## The workflow

### 1. Gather inputs

Ask or infer:

- `REPO`: GitHub repo name under `JayDS22/<repo>` (verify with `gh repo view JayDS22/<repo>` or similar)
- `TITLE`: one-line project title (use for h1 and card)
- `KICKER`: category + date, e.g. `Agent Systems · October 2026` (goes in page-header kicker)
- `DOMAIN`: one of the existing /explore/ domains or "Other"
- `SUMMARY`: 2-3 sentence project description, no marketing adjectives
- `METRICS`: 3-4 metric chips, each short enough for a card (e.g., `Sonnet 4.6`, `3 novel evals`, `make bench`)
- `TECH_TAGS`: 3-5 technology tags
- `DECK`: whether this project goes on home featured (reserve for credential-tier: external validation, hackathon win, named internship, selected program)

### 2. Pick the next chapter number

Current max: run `/bin/ls post/ | /usr/bin/grep -oE 'chapter-[0-9]+' | /usr/bin/sort -V | /usr/bin/tail -1`. Increment by 1. Skip numbers already taken.

**Idempotency check (REQUIRED before any file creation):** confirm `post/chapter-<N>/` does NOT already exist. If it does, STOP and ask the user whether to pick a higher number, overwrite, or abort. Do not blindly scaffold on top of an existing chapter.

### 3. Find a real tech-savvy thumbnail

Fan out a research agent (general-purpose, has WebSearch + WebFetch) with this brief:

```
Find a real tech-savvy image for <PROJECT TITLE>. The project is about <SUMMARY>.

Constraints:
- Real polished graphic, screenshot, or infographic. NOT AI-generated. NOT a hand-crafted SVG.
- Minimum 1600x900, prefer 16:9 aspect.
- License allows personal portfolio use (public domain, CC BY, CC BY-SA, Unsplash license, vendor press/promo imagery fair-use for editorial reference).
- Aesthetic: dark-background designed graphics with iconic elements (like the LLM-serving reference at images/llm-serving.png).

Priority sources:
1. Vendor engineering blog hero graphics (Anthropic news/research, OpenAI blog) matching the project's model stack
2. Live product/leaderboard screenshots (SWE-bench, Chatbot Arena, HELM) if the project is comparative
3. GitHub social preview of the project itself or a related open-source project
4. Wikimedia Commons real photos (prefer high-res, non-AI-era)
5. Pre-2022 Flickr Creative Commons tech photos
6. Taylor Vick / early-era Unsplash hardware photos

Return 4 to 6 candidates with: direct image URL, source page URL, license, resolution, 1-line rationale.
VERIFY each URL fetches with WebFetch before returning.
```

Pick the top candidate. Download, resize to 1920x1080 center-crop, save to `images/project-heros/chapter-<N>-thumb.jpg`:

```bash
cd /Users/DELL/Documents/Portfolio
mkdir -p images/project-heros/raw
curl -sL -A "Mozilla/5.0" "<IMAGE_URL>" -o images/project-heros/raw/thumb.jpg
# or .png depending on source
file images/project-heros/raw/thumb.*
```

If the downloaded file is HTML not image (vendor blocked hotlinking), try alternates:
- Different User-Agent: `-A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15"`
- Fetch the vendor page and extract the actual `og:image` URL from HTML
- Live screenshot the page with shot-scraper (install if needed: `pip3 install --user --break-system-packages shot-scraper playwright && python3 -m playwright install chromium`)

Resize + crop (PIL comes with matplotlib dep):

```python
from PIL import Image
import os
src = "images/project-heros/raw/thumb.jpg"
TW, TH = 1920, 1080
im = Image.open(src)
if im.mode == "RGBA":
    bg = Image.new("RGB", im.size, (26, 34, 54))
    bg.paste(im, mask=im.split()[3])
    im = bg
elif im.mode != "RGB":
    im = im.convert("RGB")
w, h = im.size
scale = max(TW / w, TH / h)
nw, nh = int(round(w*scale)), int(round(h*scale))
im = im.resize((nw, nh), Image.LANCZOS)
left = (nw - TW) // 2
top = (nh - TH) // 2
im = im.crop((left, top, left+TW, top+TH))
im.save("images/project-heros/chapter-<N>-thumb.jpg", "JPEG", quality=85, optimize=True, progressive=True)
```

Add attribution to `images/project-heros/CREDITS.md`.

### 4. Scaffold the chapter page

Copy chapter-11 as template, do not copy chapter-12 or later (they may have accumulated TODOs or structural drift):

```bash
mkdir -p post/chapter-<N>
cp post/chapter-11/index.html post/chapter-<N>/index.html
```

Edit the following in `post/chapter-<N>/index.html`:

1. **Head**: `<title>` and `<meta name="description">`
2. **Chapter hero section**: swap `src` to `../../images/project-heros/chapter-<N>-thumb.jpg` (yes, same image as /post/ listing — the mismatch-tolerance earlier work tried was abandoned)
3. **Page-header**: section-kicker (text matches `KICKER`), h1 (matches `TITLE`), paragraph (summary), metric chip row
4. **Back + Repository buttons** in page-header toolbar: match the pattern from chapter-12/13/14/15:
   ```html
   <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:24px;">
     <a href="../../post/" class="btn btn-secondary">
       <svg><use href="#i-back"/></svg> All projects
     </a>
     <a href="https://github.com/JayDS22/<REPO>" class="btn btn-primary" target="_blank" rel="noopener">
       <svg><use href="#i-github"/></svg> Repository
     </a>
   </div>
   ```
5. **Article body**: strong-prefixed section headers (`<strong>What it is :</strong>`, `<strong>Why I built it :</strong>`, `<strong>Architecture :</strong>`, etc.). Match the voice of chapter-12. No em-dashes.
6. **Inline figures**: see step 5.
7. **Tech stack block** at end
8. **Repository CTA** at bottom + back + about buttons

### 5. Add inline figures to the chapter body

Each chapter should carry 2-4 inline `<figure>` elements. These CAN be SVG (hand-authored is fine for inline, just not thumbnails). Typical set:

- Architecture or flow diagram (SVG, ~800-900 x 400-450, dark-panel or transparent canvas, hand-authored, matches portfolio token palette)
- Code snippet card (PNG via matplotlib text-rendering, dark panel #1a2236, JetBrains Mono, 1200x680)
- Result table (styled HTML with `<table><thead><tbody>`; CSS already in modern.css)
- Optional: UI mockup for projects with a live surface (SVG, 1600x900, rendered through cairosvg if PNG needed)

Figure pattern:

```html
<figure>
  <img src="../../images/project-heros/chapter-<N>-<slug>.svg" alt="<descriptive alt>">
  <figcaption>One-line caption. "Illustrative" if the data is not measured.</figcaption>
</figure>
```

Design tokens for figures:
- `#1d4ed8` indigo (primary accent)
- `#b88746` bronze (highlight / warning / safety-critical callout)
- `#475467` muted (secondary text)
- `#0c1424` strong text
- `#ecf0f6` pale background
- `#1a2236` dark panel
- `#f7f8fb` near-white (dark panel text)
- `#8899aa` dim text on dark panel
- Code highlighting only: `#a3d9a5` soft green (strings), `#88c0d0` soft blue (types)
- Font: JetBrains Mono preferred, SF Mono fallback, DejaVu Sans Mono last; Space Grotesk for headlines

### 6. Wire into /post/ listing

Insert a new card into `post/index.html` in chronological reverse order. The current post order after the AWS flagship is 15, 12, 14, 13, 10. Place the new chapter in the right spot by pushed_at date. Card template:

```html
<article class="project-card">
  <div class="project-thumb">
    <img src="../images/project-heros/chapter-<N>-thumb.jpg" alt="<descriptive alt>">
  </div>
  <div class="project-body">
    <div class="project-meta"><span><DATE></span> <span>·</span> <span><DOMAIN></span></div>
    <h3 class="project-title">
      <a href="../post/chapter-<N>/"><TITLE></a>
    </h3>
    <p class="project-desc"><SUMMARY></p>
    <div class="project-metrics">
      <span class="metric-chip"><METRIC 1></span>
      <span class="metric-chip"><METRIC 2></span>
      <span class="metric-chip"><METRIC 3></span>
    </div>
    <div class="project-tech">
      <span class="tech-tag"><TAG 1></span><span class="tech-tag"><TAG 2></span><span class="tech-tag"><TAG 3></span><span class="tech-tag"><TAG 4></span>
    </div>
    <a class="project-link" href="../post/chapter-<N>/">View case study <svg><use href="#i-arrow"/></svg></a>
  </div>
</article>
```

### 7. Home featured decision

Only add to home featured if the project is credential-tier: external validation (hackathon win, selected program like GSoC, named internship), concrete metrics with real measurements, or safety/eval work that aligns with the Anthropic-targeted strategy.

Current home featured: `chapter-11`, `chapter-15`, `chapter-8`, `chapter-13`.

If adding, decide which existing card to bump (not simply prepend; keep 4 cards). Bump the weakest fit for "best projects". Edit `index.html` featured section.

### 8. Sitemap

Add `<url><loc>https://jayds22.github.io/Portfolio/post/chapter-<N>/</loc>...` entry to `sitemap.xml`.

### 9. Fill all TODOs with real content

**Grep for TODOs:**

```bash
/usr/bin/grep -rn "TODO\|\[TODO" post/chapter-<N>/ && echo "FOUND TODO" || echo "clean"
```

Replace every TODO with real or illustrative content:
- Numeric placeholders: fill with illustrative numbers labeled "illustrative" OR replace with methodology prose
- List placeholders: enumerate the actual list (invent plausible per-project items if the user has not shared)
- Table placeholders: fill with illustrative data labeled "illustrative" in caption

### 10. Visual verification

Install if missing (portable, works on macOS/Linux):

```bash
python3 -m pip install --user --break-system-packages shot-scraper playwright
python3 -m playwright install chromium
```

Serve + screenshot. Invoke shot-scraper via `python3 -m shot_scraper` so no hardcoded install path is needed:

```bash
cd $PORTFOLIO_ROOT  # the repo root, wherever it lives
python3 -m http.server 4000 --bind 127.0.0.1 >/dev/null 2>&1 &
PID=$!
sleep 2

mkdir -p /tmp/portfolio-audit
python3 -m shot_scraper "http://127.0.0.1:4000/post/chapter-<N>/" -o /tmp/portfolio-audit/new-chapter.png --width 1440 --wait 2500
python3 -m shot_scraper "http://127.0.0.1:4000/post/" -o /tmp/portfolio-audit/post.png --width 1440 --wait 2500
python3 -m shot_scraper "http://127.0.0.1:4000/" -o /tmp/portfolio-audit/home.png --width 1440 --height 2800 --wait 3500 --javascript "window.scrollTo(0, 1800);"

# ALSO capture dark mode and mobile for the chapter page (hero hides below 640px, verify page still readable)
python3 -m shot_scraper "http://127.0.0.1:4000/post/chapter-<N>/" -o /tmp/portfolio-audit/new-chapter-dark.png --width 1440 --wait 2500 --javascript "document.documentElement.dataset.theme = 'dark'; localStorage.setItem('theme', 'dark');"
python3 -m shot_scraper "http://127.0.0.1:4000/post/chapter-<N>/" -o /tmp/portfolio-audit/new-chapter-mobile.png --width 400 --wait 2500

kill $PID
```

Then use Read tool to view each PNG. Confirm:
- Hero image renders at full width, not stretched/clipped
- Thumbnail renders in /post/ grid without overlap
- Home featured card (if added) renders with the new image
- Dark-mode screenshot: text contrast ok, dark-panel figures do not disappear into page bg
- Mobile screenshot (400px): hero is hidden by media query, title + article body readable
- No visible TODO text
- No em-dashes
- No stretched text / overlapping headlines (the AWS SVG issue was exactly this)

### 11. Smoke test URLs

```bash
python3 -m http.server 4000 --bind 127.0.0.1 >/dev/null 2>&1 &
PID=$!
sleep 1
for p in "" post/ post/chapter-<N>/ images/project-heros/chapter-<N>-thumb.jpg; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:4000/$p")
  echo "  $p -> $code"
done
kill $PID
```

All should return 200.

### 12. Commit + checkpoint + push

**Hard-fail enforcement (REQUIRED before `git add`):** run the three checks below. If any fails, STOP and fix. Do not proceed to commit.

```bash
# a) No TODO fragments
if /usr/bin/grep -rn "TODO\|\[TODO\|\[Hero.*placeholder" post/chapter-<N>/ ; then
  echo "ABORT: TODO or placeholder fragment still visible" >&2 ; exit 1 ; fi
# b) No em-dashes anywhere in files you touched
python3 -c "import pathlib,sys; bad=[f for f in [pathlib.Path('post/chapter-<N>/index.html'),pathlib.Path('post/index.html'),pathlib.Path('index.html')] if any(c in f.read_text() for c in [chr(8212),chr(8211)])]; sys.exit(0 if not bad else (print('ABORT: em/en-dash in',bad) or 1))"
# c) Thumbnail is a real image, not an HTML error page
/usr/bin/file images/project-heros/chapter-<N>-thumb.jpg | /usr/bin/grep -qE 'JPEG|PNG' || { echo "ABORT: thumb is not a real image" >&2 ; exit 1 ; }
```

Commit style: neutral, factual, no AI tells, no `Co-Authored-By`. Example:

```bash
git add post/chapter-<N> images/project-heros/chapter-<N>-thumb.jpg \
        images/project-heros/CREDITS.md post/index.html index.html sitemap.xml

git commit --no-gpg-sign -m "Add chapter-<N>: <TITLE>

Scaffolded from chapter-11 template. Hero and listing thumbnail use
<SOURCE> graphic, see CREDITS.md for attribution. Inline figures:
<brief list>. Added card to /post/ listing in chronological order,
<added to home featured | not on home>. Sitemap entry added."
```

**Checkpoint before push (REQUIRED):** show the user `git log -1 --stat` and `git diff HEAD~1 -- post/index.html index.html` (the two most-visible-to-visitors files). Ask explicitly:

> "Ready to push to `main` (goes live on jayds22.github.io/Portfolio within ~45s). Confirm?"

Only after the user confirms, run the rebase and push:

```bash
git pull --rebase -X theirs origin main 2>&1 | tail -3
git push origin main 2>&1 | tail -3
```

The `-X theirs` on rebase: the daily `sync-github-projects.yml` workflow may have landed a `chore: refresh GitHub project data` commit since your last pull. Taking "theirs" (your local commit's version, in rebase semantics) on `data/github.json` preserves anything you intended; the next cron run reconciles.

## Content voice

Match chapter-12 as the canonical voice:

- Section headers in `<strong>What it is :</strong>` pattern
- Short declarative sentences
- No marketing adjectives ("blazing fast", "production-ready", "enterprise-grade")
- Honest limitations in a `What this does not do :` section
- "What's next :" section listing concrete planned work
- Illustrative numbers labeled as such

## Verification checklist (before `git push`)

- [ ] `grep -rn "TODO\|\[TODO" post/chapter-<N>/` returns nothing
- [ ] No em-dashes anywhere in new content (`grep "—" post/chapter-<N>/index.html index.html post/index.html` returns nothing)
- [ ] Thumbnail JPG is real image, not HTML (`file images/project-heros/chapter-<N>-thumb.jpg` reports JPEG)
- [ ] Thumbnail is 1920x1080 (`python3 -c "from PIL import Image; print(Image.open('images/project-heros/chapter-<N>-thumb.jpg').size)"`)
- [ ] shot-scraper screenshot of new chapter viewed via Read tool, no visual issues
- [ ] shot-scraper screenshot of /post/ viewed, new card renders in right position
- [ ] All five target URLs return 200 (home, /post/, chapter page, thumbnail, sitemap)
- [ ] CREDITS.md updated with attribution
- [ ] If added to home featured, decision on which card to bump is explicit
- [ ] Commit message is neutral, no "Co-Authored-By: Claude", no AI-tell phrases

## Deleted an older chapter from /post/ listing?

Four chapters were pruned from the listing in Oct 2026 (0, 1, 4, 5) but their source files remain for direct URL access. If you add a new chapter and want to re-promote an older one, add its `<article class="project-card">` back to `post/index.html`. If you want to actually delete a chapter, delete the directory and the sitemap entry.

## Related skills

- `/claude-api` for anything that touches the Anthropic SDK in a new project
- `/ui-ux-pro-max` for design-system questions on new UI mockups
- `/ponytail-review` to audit a new chapter page for over-engineering before shipping

## Reference pointers (do not rely on live counts here, they rot)

- Current chapter count: run `/bin/ls post/ | /usr/bin/grep -cE '^chapter-[0-9]+$'`
- Current /post/ listing cards: run `/usr/bin/grep -c '<article class="project-card' post/index.html`
- Home featured order: read the `.featured-projects` block in `index.html`
- Flagship: whichever card carries the `project-card--flagship` class on `/post/`
- Design tokens: defined in `css/modern.css`:root; dark theme at `html[data-theme="dark"]`
- Sitemap entries: hand-maintained in `sitemap.xml` (add on new chapter, remove on delete)
- CLAUDE.md itself is gitignored and must stay that way
