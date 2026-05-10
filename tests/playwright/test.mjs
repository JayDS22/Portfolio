// End-to-end tests for the project-graph "click a domain chip to focus" feature.
//
// Runs on /explore/ (full-screen graph) and the home-page constellation.
// Asserts DOM state changes (chip.on / has-selection / Show all visibility),
// camera/filter behavior is exercised via the same accessors and verified
// indirectly through state.
//
// Targets BASE_URL (default http://127.0.0.1:4000). In CI a Python http.server
// serves the repo root; locally you can point at the live site via
//   BASE_URL=https://jayds22.github.io/Portfolio node test.mjs

import { chromium } from 'playwright';

const BASE = (process.env.BASE_URL || 'http://127.0.0.1:4000').replace(/\/$/, '');
const log  = (...a) => console.log(...a);

let pass = 0, fail = 0;
const ok   = (msg) => { log('  PASS  ' + msg); pass++; };
const bad  = (msg, extra) => { log('  FAIL  ' + msg + (extra ? '  ' + extra : '')); fail++; };
const sect = (msg) => log('\n=== ' + msg + ' ===');
const expect = (cond, msg, extra) => cond ? ok(msg) : bad(msg, extra);

const browser = await chromium.launch();
const ctx     = await browser.newContext({ viewport: { width: 1280, height: 900 } });
const page    = await ctx.newPage();

const consoleErrors = [];
page.on('console', m => {
  if (m.type() === 'error') {
    const loc = m.location();
    consoleErrors.push(m.text() + (loc.url ? '  @ ' + loc.url : ''));
  }
});
page.on('pageerror', e => consoleErrors.push('pageerror: ' + e.message));
page.on('requestfailed', r => consoleErrors.push('requestfailed: ' + r.url() + ' (' + r.failure()?.errorText + ')'));
page.on('response', r => { if (r.status() >= 400) consoleErrors.push('http ' + r.status() + ': ' + r.url()); });

const waitForChips = async (legendSel) =>
  page.waitForFunction(sel => document.querySelectorAll(sel + ' .chip').length >= 9, legendSel, { timeout: 30000 });

const runScenario = async (name, openPath, legendSel) => {
  sect(name);
  await page.goto(BASE + openPath, { waitUntil: 'networkidle' });

  if (legendSel.includes('constellation')) {
    await page.locator('#constellation-section').scrollIntoViewIfNeeded();
  }

  await waitForChips(legendSel);
  ok('legend rendered with >=9 domain chips');

  const initiallySelected = await page.locator(legendSel).evaluate(el => el.classList.contains('has-selection'));
  expect(!initiallySelected, 'legend has no .has-selection at start');

  const resetVisible = await page.locator(legendSel + ' .reset').isVisible();
  expect(!resetVisible, '"Show all" button hidden at start');

  const cvChip = page.locator(legendSel + ' .chip[data-domain="computer-vision"]');
  await cvChip.click();
  await page.waitForTimeout(300);

  expect(await cvChip.evaluate(el => el.classList.contains('on')),
         'CV chip gains .on class');
  expect(await page.locator(legendSel).evaluate(el => el.classList.contains('has-selection')),
         'legend gains .has-selection');
  expect(await page.locator(legendSel + ' .reset').isVisible(),
         '"Show all" button becomes visible');

  const llmChip = page.locator(legendSel + ' .chip[data-domain="llm-agents"]');
  expect(!(await llmChip.evaluate(el => el.classList.contains('on'))),
         'other chip (LLM) is not active');

  // Switch focus
  await llmChip.click();
  await page.waitForTimeout(300);
  expect(!(await cvChip.evaluate(el => el.classList.contains('on'))),
         'CV chip loses .on after switching');
  expect(await llmChip.evaluate(el => el.classList.contains('on')),
         'LLM chip gains .on after switching');

  // Toggle off
  await llmChip.click();
  await page.waitForTimeout(300);
  expect(!(await llmChip.evaluate(el => el.classList.contains('on'))),
         'LLM chip toggles off on second click');
  expect(!(await page.locator(legendSel).evaluate(el => el.classList.contains('has-selection'))),
         'legend loses .has-selection on toggle off');
  expect(!(await page.locator(legendSel + ' .reset').isVisible()),
         '"Show all" hides on toggle off');

  // "Show all" button reset
  await page.locator(legendSel + ' .chip[data-domain="stats-bayesian"]').click();
  await page.waitForTimeout(300);
  await page.locator(legendSel + ' .reset').click();
  await page.waitForTimeout(300);
  expect(!(await page.locator(legendSel).evaluate(el => el.classList.contains('has-selection'))),
         '"Show all" button resets selection state');

  // Capture a screenshot of the focused state for the artifact upload
  await page.locator(legendSel + ' .chip[data-domain="computer-vision"]').click();
  await page.waitForTimeout(1500);
  const shotPath = process.cwd() + '/screenshot-' + name.replace(/[^a-z0-9]/gi, '-') + '.png';
  await page.locator(legendSel.includes('constellation') ? '.constellation' : '.graph-stage')
            .screenshot({ path: shotPath });
  ok('captured focused-on-CV screenshot at ' + shotPath);
  await page.locator(legendSel + ' .reset').click();
};

try {
  await runScenario('Explore page',       '/explore/', '.graph-legend');
  await runScenario('Home constellation', '/',         '.constellation-legend');

  sect('Console errors during run');
  // Filter known harmless noise:
  // - favicon 404s (defensive: site has a favicon now, but browsers may probe alt paths)
  // - SwiftShader/WebGL warnings from the Playwright headless-shell GPU emulation
  const ignored = e =>
    /favicon\.ico/.test(e) ||
    /THREE\.WebGLProgram/.test(e) ||
    /VALIDATE_STATUS false/.test(e);
  const real = consoleErrors.filter(e => !ignored(e));
  if (real.length === 0) ok('no feature-related console errors (' + (consoleErrors.length - real.length) + ' ignored)');
  else {
    bad(real.length + ' console error(s)');
    real.forEach(e => log('    -> ' + e));
  }
} catch (e) {
  bad('test crashed: ' + e.message);
  console.error(e);
} finally {
  await browser.close();
}

log('\n' + '='.repeat(48));
log('  BASE=' + BASE);
log('  PASS=' + pass + '  FAIL=' + fail);
log('='.repeat(48));
process.exit(fail === 0 ? 0 : 1);
