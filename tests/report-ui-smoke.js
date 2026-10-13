const assert = require('assert');
const fs = require('fs');
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
    assert.strictEqual(await desktop.locator('#locusMapRows tr').count(), 23);
    await desktop.locator('#locusMapDetails > summary').click();
    assert.match(await desktop.locator('#locusMapRows tr[data-panel="egg"][data-target="rs12123821"] td[data-chip="23andme"]').innerText(), /Priamy rs12123821/i);
    assert.match(await desktop.locator('#locusMapRows tr[data-panel="milk"][data-target="rs12123821"] td[data-chip="23andme"]').innerText(), /Proxy rs115288876/i);
    assert.match(await desktop.locator('#locusMapRows tr[data-panel="milk"][data-target="rs11949166"] td[data-chip="23andme"]').innerText(), /Proxy rs63582760/i);
    assert.match(await desktop.locator('#locusMapRows tr[data-panel="milk"][data-target="rs2069772"] td[data-chip="23andme"]').innerText(), /Proxy rs17388568/i);
    assert.match(await desktop.locator('#locusMapNote').innerText(), /rs17388568/i);
    assert.match(await desktop.locator('#locusMapRows tr[data-panel="milk"][data-target="rs11949166"] td[data-chip="dnaera"]').innerText(), /Nahrajte export/i);
    await desktop.locator('#locusMapSection').screenshot({ path: path.join(qaDir, 'locus-map-23andme.png') });
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

    const milkCard = desktop.locator('[data-summary-model="milk"]');
    assert.match(await milkCard.locator('.summary-card-meta').innerText(), /2 priamo \+ 3 proxy/i);
    await milkCard.click();
    await desktop.waitForSelector('#detailModal.open');
    assert.match(await desktop.locator('#resultCopy').innerText(), /rs115288876/i);
    assert.match(await desktop.locator('#resultCopy').innerText(), /rs63582760/i);
    assert.match(await desktop.locator('#resultCopy').innerText(), /rs17388568/i);
    assert.strictEqual((await desktop.locator('#rawScore').innerText()).trim(), '7');
    assert.match((await desktop.locator('#scoreConfidence').innerText()).trim(), /^88,1 %$/);
    assert.strictEqual((await desktop.locator('#interpretationConfidence').innerText()).trim(), '4 / 6');
    assert.strictEqual((await desktop.locator('#scoreRange').innerText()).trim(), '3–9');
    assert.match(await desktop.locator('#markerRows').innerText(), /rs115288876/i);
    assert.match(await desktop.locator('#markerRows').innerText(), /rs63582760/i);
    assert.match(await desktop.locator('#markerRows').innerText(), /rs10588133/i);
    assert.match(await desktop.locator('#markerRows').innerText(), /rs17388568/i);
    assert.strictEqual((await desktop.locator('#markerRows tr').nth(0).locator('td').nth(4).innerText()).trim(), '1');
    assert.strictEqual((await desktop.locator('#markerRows tr').nth(1).locator('td').nth(4).innerText()).trim(), '1');
    assert.strictEqual((await desktop.locator('#markerRows tr').nth(2).locator('td').nth(4).innerText()).trim(), '2');
    assert.match(await desktop.locator('#interpretationText').innerText(), /rs115288876, rs63582760 aj rs17388568/i);
    await desktop.screenshot({ path: path.join(qaDir, 'detail-milk-proxy.png') });
    await desktop.locator('#detailModal').evaluate(element => { element.scrollTop = element.scrollHeight; });
    await desktop.screenshot({ path: path.join(qaDir, 'detail-milk-proxy-bottom.png') });
    await desktop.keyboard.press('Escape');
    await desktop.locator('#detailModal').waitFor({ state: 'hidden' });

    for (const key of ['peanut', 'shared', 'lactose', 'celiac', 'histamine']) {
      await desktop.locator(`[data-summary-model="${key}"]`).click();
      await desktop.waitForSelector('#detailModal.open');
      assert.notStrictEqual((await desktop.locator('#detailModalTitle').innerText()).trim(), '');
      await desktop.keyboard.press('Escape');
      await desktop.locator('#detailModal').waitFor({ state: 'hidden' });
    }

    await desktop.locator('[data-lang="en"]').click();
    assert.strictEqual((await desktop.locator('#summaryTitle').innerText()).toLowerCase(), 'your genetic predispositions');
    assert.strictEqual(await desktop.locator('.summary-card').count(), 7);
    assert.strictEqual((await desktop.locator('#locusMapTitle').innerText()).trim().toLowerCase(), 'locus and proxy map by dna chip');
    await desktop.locator('[data-summary-model="milk"]').click();
    await desktop.waitForSelector('#detailModal.open');
    assert.match(await desktop.locator('#resultCopy').innerText(), /rs115288876/i);
    assert.match(await desktop.locator('#resultCopy').innerText(), /rs63582760/i);
    assert.match(await desktop.locator('#resultCopy').innerText(), /rs17388568/i);
    assert.match(await desktop.locator('#interpretationText').innerText(), /rs115288876, rs63582760 and rs17388568/i);
    await desktop.keyboard.press('Escape');
    await desktop.locator('#detailModal').waitFor({ state: 'hidden' });

    const aliasPage = await browser.newPage({ viewport: { width: 1200, height: 900 }, deviceScaleFactor: 1 });
    aliasPage.on('pageerror', error => errors.push(error.message));
    await aliasPage.goto(appUrl);
    const aliasFixture = fs.readFileSync(fixture, 'utf8').replace(/^rs63582760\t/m, 'rs10588133\t');
    await aliasPage.setInputFiles('#fileInput', { name: 'synthetic-current-id.txt', mimeType: 'text/plain', buffer: Buffer.from(aliasFixture) });
    await aliasPage.waitForSelector('#summaryDashboard:not([hidden])');
    await aliasPage.locator('[data-summary-model="milk"]').click();
    await aliasPage.waitForSelector('#detailModal.open');
    assert.match(await aliasPage.locator('#resultCopy').innerText(), /rs63582760/i);
    assert.match((await aliasPage.locator('#scoreConfidence').innerText()).trim(), /^88,1 %$/);
    assert.match(await aliasPage.locator('#markerRows').innerText(), /rs10588133/i);
    await aliasPage.close();

    const myHeritagePage = await browser.newPage({ viewport: { width: 1200, height: 900 }, deviceScaleFactor: 1 });
    myHeritagePage.on('pageerror', error => errors.push(error.message));
    await myHeritagePage.goto(appUrl);
    const myHeritageFixture = [
      '##fileformat=MyHeritage',
      'RSID,CHROMOSOME,POSITION,RESULT',
      'rs12123821,1,152179152,CT',
      'rs115288876,1,152000117,AG',
      'rs63582760,5,132022972,GT',
      'rs17388568,4,123329362,GG'
    ].join('\n');
    await myHeritagePage.setInputFiles('#fileInput', { name: 'synthetic-myheritage.csv', mimeType: 'text/csv', buffer: Buffer.from(myHeritageFixture) });
    await myHeritagePage.waitForSelector('#summaryDashboard:not([hidden])');
    await myHeritagePage.locator('#locusMapDetails > summary').click();
    assert.match(await myHeritagePage.locator('#locusMapRows tr[data-panel="egg"][data-target="rs12123821"] td[data-chip="myheritage"]').innerText(), /Priamy rs12123821/i);
    assert.match(await myHeritagePage.locator('#locusMapRows tr[data-panel="milk"][data-target="rs11949166"] td[data-chip="myheritage"]').innerText(), /Proxy rs63582760/i);
    assert.match(await myHeritagePage.locator('#locusMapRows tr[data-panel="milk"][data-target="rs2069772"] td[data-chip="myheritage"]').innerText(), /Proxy rs17388568/i);
    await myHeritagePage.close();

    const dnaEraPage = await browser.newPage({ viewport: { width: 1200, height: 900 }, deviceScaleFactor: 1 });
    dnaEraPage.on('pageerror', error => errors.push(error.message));
    await dnaEraPage.goto(appUrl);
    const dnaEraFixture = [
      '[Header]',
      'GSGT Version,2.0.4',
      '[Data]',
      'Sample Name,SNP Name,Chr,Position,Allele1 - Plus,Allele2 - Plus',
      'sample,rs12123821,1,152179152,C,T',
      'sample,rs115288876,1,152000117,A,G',
      'sample,rs63582760,5,132022972,G,T',
      'sample,rs17388568,4,123329362,G,G'
    ].join('\n');
    await dnaEraPage.setInputFiles('#fileInput', { name: 'synthetic-dnaera.csv', mimeType: 'text/csv', buffer: Buffer.from(dnaEraFixture) });
    await dnaEraPage.waitForSelector('#summaryDashboard:not([hidden])');
    await dnaEraPage.locator('#locusMapDetails > summary').click();
    assert.match(await dnaEraPage.locator('#locusMapRows tr[data-panel="egg"][data-target="rs12123821"] td[data-chip="dnaera"]').innerText(), /Priamy rs12123821/i);
    assert.match(await dnaEraPage.locator('#locusMapRows tr[data-panel="milk"][data-target="rs11949166"] td[data-chip="dnaera"]').innerText(), /Proxy rs63582760/i);
    assert.match(await dnaEraPage.locator('#locusMapRows tr[data-panel="milk"][data-target="rs2069772"] td[data-chip="dnaera"]').innerText(), /Proxy rs17388568/i);
    await dnaEraPage.close();

    const integerScorePage = await browser.newPage({ viewport: { width: 1200, height: 900 }, deviceScaleFactor: 1 });
    integerScorePage.on('pageerror', error => errors.push(error.message));
    await integerScorePage.goto(appUrl);
    const integerFixture = fs.readFileSync(fixture, 'utf8').replace(/^rs115288876\t1\t152000117\tAG$/m, 'rs115288876\t1\t152000117\tGG');
    await integerScorePage.setInputFiles('#fileInput', { name: 'synthetic-integer-score.txt', mimeType: 'text/plain', buffer: Buffer.from(integerFixture) });
    await integerScorePage.waitForSelector('#summaryDashboard:not([hidden])');
    await integerScorePage.locator('[data-summary-model="milk"]').click();
    await integerScorePage.waitForSelector('#detailModal.open');
    assert.strictEqual((await integerScorePage.locator('#rawScore').innerText()).trim(), '6');
    assert.strictEqual((await integerScorePage.locator('#markerRows tr').nth(0).locator('td').nth(4).innerText()).trim(), '0');
    assert.strictEqual((await integerScorePage.locator('#markerRows tr').nth(1).locator('td').nth(4).innerText()).trim(), '1');
    assert.match(await integerScorePage.locator('#resultCopy').innerText(), /príspevok do skóre 0 z 2/i);
    assert.match(await integerScorePage.locator('#resultCopy').innerText(), /príspevok do skóre 1 z 2/i);
    await integerScorePage.close();

    const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
    mobile.on('pageerror', error => errors.push(error.message));
    await uploadAndWait(mobile);
    await mobile.screenshot({ path: path.join(qaDir, 'overview-mobile.png'), fullPage: true });

    assert.deepStrictEqual(errors, []);
    console.log('UI smoke test passed: 7 summary cards, whole-number milk score, 23-row chip/proxy map, merged rsID alias, EN switch, desktop and mobile layouts.');
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
