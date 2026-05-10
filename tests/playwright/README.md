# Playwright tests

End-to-end checks for the click-to-focus interaction on the project knowledge graph
(`/explore/` and the home-page constellation).

## Run locally

```bash
# 1. install deps
npm ci

# 2. install the Chromium binary (one-time, ~120 MB)
npx playwright install chromium

# 3. serve the repo root in another terminal
cd ../..
python3 -m http.server 4000

# 4. run the suite
cd tests/playwright
npm test
```

## Run against the deployed site

```bash
npm run test:prod
# or
BASE_URL=https://jayds22.github.io/Portfolio node test.mjs
```

## What it asserts

- The legend renders with at least 9 domain chips after the data fetch.
- Clicking a chip activates it, sets `.has-selection` on the legend, and shows the "Show all" button.
- Clicking another chip switches focus cleanly (the previous chip deactivates).
- Clicking the same chip twice toggles selection off.
- The "Show all" button clears any active selection.
- No feature-related console errors fire during the run.

The same scenario runs once on `/explore/` (full-screen graph) and once on the home page constellation.
