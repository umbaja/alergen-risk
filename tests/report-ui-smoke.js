const assert = require('assert');
const path = require('path');
const { pathToFileURL } = require('url');
const { chromium } = require('playwright');

const root = path.resolve(__dirname, '..');
const appUrl = pathToFileURL(path.join(root, 'dist', 'index.html')).href;
const fixture = path.join(root, 'tests', 'fixtures', 'synthetic-all-panels.txt');
const qaDir = process.env.QA_DIR || path.join(root, 'test-artifacts');

async function uploadAndWait(page) {
  await page.goto(appUrl);
  await page.setInputFiles('#fileInput', fixture);
  await page.waitForSelector('#summaryDashboard:not([hidden])');
  assert.strictEqual(await page.locator('.summary-card').count(), 7);
}

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: process.env.BROWSER_EXECUTABLE || undefined,
  });
  try {
    const desktop = await browser.newPage({ viewport: { width: 1440, height: 1100 }, deviceScaleFactor: 1 });
    const errors = [];
    desktop.on('pageerror', error => errors.push(error.message));
    await uploadAndWait(desktop);
    await desktop.screenshot({ path: path.join(qaDir, 'overview-desktop.png'), fullPage: true });

    await desktop.locator('[data-summary-model="egg"]').click();
    await desktop.waitForSelector('#detailModal.open');
    assert.match(await desktop.locator('#detailModalTitle').innerText(), /vajce/i);
    assert.match(await desktop.locator('#resultLabel').innerText(), /predispozícia/i);
    await desktop.screenshot({ path: path.join(qaDir, 'detail-egg.png') });
    await desktop.locator('#detailModal').evaluate(element => { element.scrollTop = 850; });
    await desktop.screenshot({ path: path.join(qaDir, 'detail-egg-middle.png') });
    await desktop.locator('#detailModal').evaluate(element => { element.scrollTop = element.scrollHeight; });
    await desktop.screenshot({ path: path.join(qaDir, 'detail-egg-bottom.png') });
    await desktop.keyboard.press('Escape');
    await desktop.locator('#detailModal').waitFor({ state: 'hidden' });

    for (const key of ['peanut', 'milk', 'shared', 'lactose', 'celiac', 'histamine']) {
      await desktop.locator(`[data-summary-model="${key}"]`).click();
      await desktop.waitForSelector('#detailModal.open');
      assert.notStrictEqual((await desktop.locator('#detailModalTitle').innerText()).trim(), '');
      await desktop.keyboard.press('Escape');
      await desktop.locator('#detailModal').waitFor({ state: 'hidden' });
    }

    await desktop.locator('[data-lang="en"]').click();
    assert.strictEqual((await desktop.locator('#summaryTitle').innerText()).toLowerCase(), 'your genetic predispositions');
    assert.strictEqual(await desktop.locator('.summary-card').count(), 7);

    const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
    mobile.on('pageerror', error => errors.push(error.message));
    await uploadAndWait(mobile);
    await mobile.screenshot({ path: path.join(qaDir, 'overview-mobile.png'), fullPage: true });

    assert.deepStrictEqual(errors, []);
    console.log('UI smoke test passed: 7 summary cards, modal details, EN switch, desktop and mobile layouts.');
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
