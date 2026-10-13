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
    assert.strictEqual(await desktop.locator('#locusMapRows tr').count(), 71);
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
    assert.strictEqual(await milkCard.evaluate(element=>element.classList.contains('state-high')), true);
    assert.match(await milkCard.locator('.summary-circle').innerText(), /Zvýšená\s+predispozícia/i);
    await milkCard.click();
    await desktop.waitForSelector('#detailModal.open');
    assert.doesNotMatch(await desktop.locator('#resultCopy').innerText(), /rs115288876|rs63582760|rs17388568/i);
    assert.match(await desktop.locator('#resultCopy').innerText(), /alergii na bielkoviny kravského mlieka/i);
    assert.match(await desktop.locator('#resultCopy').innerText(), /pravdepodobnosť presného skóre 7 z 10 je 88,1 %/i);
    assert.match(await desktop.locator('#resultCopy').innerText(), /spoľahlivosť zaradenia/i);
    assert.strictEqual((await desktop.locator('#rawScore').innerText()).trim(), '7');
    assert.match((await desktop.locator('#scoreConfidence').innerText()).trim(), /^88,1 %$/);
    assert.match((await desktop.locator('#interpretationConfidence').innerText()).trim(), /^99,8 %$/);
    assert.strictEqual((await desktop.locator('#scoreRange').innerText()).trim(), '3–9');
    assert.strictEqual(await desktop.locator('#histogram .bar-col').count(), 11);
    assert.match(await desktop.locator('#distributionMeta').innerText(), /5 cieľových SNP/i);
    assert.strictEqual((await desktop.locator('#markerLabel').innerText()).trim(), 'Skóre 7');
    assert.match(await desktop.locator('#results .section-title').nth(1).innerText(), /Referenčná distribúcia EUR populácie/i);
    assert.match(await desktop.locator('#interpretationTitle').innerText(), /Vyšší počet rizikových alel/i);
    assert.match(await desktop.locator('#interpretationText').innerText(), /modelových EUR referenčných skóre/i);
    assert.strictEqual(await desktop.locator('.band-guide').isVisible(), true);
    assert.strictEqual(await desktop.locator('#bandHigh').evaluate(element=>element.classList.contains('active')), true);
    assert.strictEqual(await desktop.locator('#literatureRows tr').count(), 5);
    assert.match(await desktop.locator('#literature-title').innerText(), /Pôvod modelu a proxy náhrady/i);
    assert.match(await desktop.locator('#markerRows').innerText(), /rs115288876/i);
    assert.match(await desktop.locator('#markerRows').innerText(), /rs63582760/i);
    assert.match(await desktop.locator('#markerRows').innerText(), /rs10588133/i);
    assert.match(await desktop.locator('#markerRows').innerText(), /rs17388568/i);
    assert.strictEqual((await desktop.locator('#markerRows tr').nth(0).locator('td').nth(4).innerText()).trim(), '1');
    assert.strictEqual((await desktop.locator('#markerRows tr').nth(1).locator('td').nth(4).innerText()).trim(), '1');
    assert.strictEqual((await desktop.locator('#markerRows tr').nth(2).locator('td').nth(4).innerText()).trim(), '2');
    await desktop.screenshot({ path: path.join(qaDir, 'detail-milk-proxy.png') });
    await desktop.locator('#detailModal').evaluate(element => { element.scrollTop = 950; });
    await desktop.screenshot({ path: path.join(qaDir, 'detail-milk-practical-origin.png') });
    await desktop.locator('#detailModal').evaluate(element => { element.scrollTop = element.scrollHeight; });
    await desktop.screenshot({ path: path.join(qaDir, 'detail-milk-proxy-bottom.png') });
    await desktop.keyboard.press('Escape');
    await desktop.locator('#detailModal').waitFor({ state: 'hidden' });

    const lactoseCard=desktop.locator('[data-summary-model="lactose"]');
    assert.strictEqual(await lactoseCard.evaluate(element=>element.classList.contains('state-high')),true);
    assert.match(await lactoseCard.locator('.summary-circle').innerText(),/Zvýšená\s+predispozícia/i);
    assert.match(await lactoseCard.locator('.summary-card-meta').innerText(),/Pokles laktázy · GG/i);
    await lactoseCard.click();
    await desktop.waitForSelector('#detailModal.open');
    assert.match(await desktop.locator('#detailModalTitle').innerText(),/Laktóza/i);
    assert.strictEqual(await desktop.locator('#results').evaluate(element=>element.classList.contains('result-high')),true);
    assert.strictEqual((await desktop.locator('#rawScore').innerText()).trim(),'GG');
    assert.strictEqual((await desktop.locator('#scoreMaximum').innerText()).trim(),'rs4988235');
    assert.match(await desktop.locator('#resultLabel').innerText(),/Zvýšená predispozícia k poklesu laktázy/i);
    assert.match(await desktop.locator('#resultCopy').innerText(),/primárnemu poklesu tvorby enzýmu laktáza/i);
    assert.match(await desktop.locator('#resultCopy').innerText(),/netýka alergie na bielkoviny kravského mlieka/i);
    assert.strictEqual((await desktop.locator('#scoreConfidence').innerText()).trim(),'Priamy genotyp');
    assert.strictEqual((await desktop.locator('#interpretationConfidence').innerText()).trim(),'Nepoužitá');
    assert.match(await desktop.locator('#results .section-title').first().innerText(),/Spôsob vyhodnotenia/i);
    assert.strictEqual((await desktop.locator('#confidenceValue').innerText()).trim(),'100 %');
    assert.strictEqual((await desktop.locator('#uncertaintyValue').innerText()).trim(),'0 %');
    assert.strictEqual(await desktop.locator('.band-guide').evaluate(element=>element.classList.contains('lactose-bands')),true);
    assert.strictEqual(await desktop.locator('#bandNormal').isVisible(),false);
    assert.strictEqual(await desktop.locator('#bandHigh').evaluate(element=>element.classList.contains('active')),true);
    assert.match(await desktop.locator('#interpretationTitle').innerText(),/Zvýšená predispozícia k poklesu laktázy/i);
    assert.match(await desktop.locator('#literature-title').innerText(),/Pôvod genetického pravidla/i);
    assert.match(await desktop.locator('.detail-card h2').innerText(),/Priamo vyhodnotený marker/i);
    assert.match(await desktop.locator('#markerRows').innerText(),/rs4988235/i);
    await desktop.screenshot({path:path.join(qaDir,'detail-lactose.png')});
    await desktop.locator('#detailModal').evaluate(element=>{element.scrollTop=element.scrollHeight;});
    await desktop.screenshot({path:path.join(qaDir,'detail-lactose-origin.png')});
    await desktop.keyboard.press('Escape');
    await desktop.locator('#detailModal').waitFor({ state: 'hidden' });

    const celiacCard=desktop.locator('[data-summary-model="celiac"]');
    assert.match(await celiacCard.locator('.summary-card-meta').innerText(),/GRS .*50\/50 SNP/i);
    assert.strictEqual(await celiacCard.evaluate(element=>['state-low','state-normal','state-high'].some(name=>element.classList.contains(name))),true);
    await celiacCard.click();
    await desktop.waitForSelector('#detailModal.open');
    assert.match(await desktop.locator('#detailModalTitle').innerText(),/vážený genetický panel/i);
    assert.strictEqual((await desktop.locator('#rawScore').innerText()).trim(),'5,52');
    assert.strictEqual((await desktop.locator('#scoreMaximum').innerText()).trim(),'vážené GRS');
    assert.match(await desktop.locator('#resultLabel').innerText(),/genetická predispozícia/i);
    assert.match(await desktop.locator('#resultCopy').innerText(),/nie je percento pravdepodobnosti ochorenia/i);
    assert.match(await desktop.locator('#panelCoverage').innerText(),/50\/50 priamo/i);
    assert.match(await desktop.locator('#scoreConfidence').innerText(),/DQ2\.5\/X/i);
    assert.strictEqual(await desktop.locator('#histogram .bar-col').count(),13);
    assert.match(await desktop.locator('#distributionMeta').innerText(),/GRS42 \+ 4 výskumné SNP/i);
    assert.match(await desktop.locator('#clinicalNotice').innerText(),/anti-tTG IgA/i);
    assert.strictEqual(await desktop.locator('#literatureRows tr').count(),50);
    assert.strictEqual(await desktop.locator('#markerRows tr').count(),50);
    assert.match(await desktop.locator('#markerRows').innerText(),/rs2187668/i);
    assert.match(await desktop.locator('#markerRows').innerText(),/rs17849502/i);
    assert.match(await desktop.locator('#literatureNotes').innerText(),/rs6822844/i);
    await desktop.screenshot({path:path.join(qaDir,'detail-celiac.png')});
    await desktop.locator('#detailModal').evaluate(element=>{element.scrollTop=element.scrollHeight;});
    await desktop.screenshot({path:path.join(qaDir,'detail-celiac-origin.png')});
    await desktop.keyboard.press('Escape');
    await desktop.locator('#detailModal').waitFor({state:'hidden'});

    for (const key of ['peanut', 'shared', 'histamine']) {
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
    assert.doesNotMatch(await desktop.locator('#resultCopy').innerText(), /rs115288876|rs63582760|rs17388568/i);
    assert.match(await desktop.locator('#resultCopy').innerText(), /cow's-milk protein allergy/i);
    assert.strictEqual(await desktop.locator('#histogram .bar-col').count(), 11);
    assert.match(await desktop.locator('#results .section-title').nth(1).innerText(), /EUR population reference distribution/i);
    assert.match(await desktop.locator('#interpretationTitle').innerText(), /Higher risk-allele count/i);
    await desktop.keyboard.press('Escape');
    await desktop.locator('#detailModal').waitFor({ state: 'hidden' });
    await desktop.locator('[data-summary-model="lactose"]').click();
    await desktop.waitForSelector('#detailModal.open');
    assert.match(await desktop.locator('#resultLabel').innerText(),/Higher predisposition to lactase non-persistence/i);
    assert.strictEqual((await desktop.locator('#scoreConfidence').innerText()).trim(),'Direct genotype');
    assert.match(await desktop.locator('#literature-title').innerText(),/Origin of the genetic rule/i);
    await desktop.keyboard.press('Escape');
    await desktop.locator('#detailModal').waitFor({ state: 'hidden' });
    await desktop.locator('[data-summary-model="celiac"]').click();
    await desktop.waitForSelector('#detailModal.open');
    assert.match(await desktop.locator('#detailModalTitle').innerText(),/weighted genetic panel/i);
    assert.strictEqual((await desktop.locator('#scoreMaximum').innerText()).trim(),'weighted GRS');
    assert.match(await desktop.locator('#resultCopy').innerText(),/not a disease-probability percentage/i);
    assert.match(await desktop.locator('#literature-title').innerText(),/Origin of the weighted model/i);
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
    assert.doesNotMatch(await aliasPage.locator('#resultCopy').innerText(), /rs63582760/i);
    assert.match((await aliasPage.locator('#scoreConfidence').innerText()).trim(), /^88,1 %$/);
    assert.match(await aliasPage.locator('#markerRows').innerText(), /rs10588133/i);
    await aliasPage.close();

    for (const scenario of [
      {
        name: 'low',
        replacements: [['rs2212434\t11\t76281593\tCT','rs2212434\t11\t76281593\tCC'],['rs17616434\t4\t38816000\tCC','rs17616434\t4\t38816000\tTT'],['rs115288876\t1\t152000117\tAG','rs115288876\t1\t152000117\tGG'],['rs63582760\t5\t132022972\tGT','rs63582760\t5\t132022972\tGG'],['rs17388568\t4\t123329362\tGG','rs17388568\t4\t123329362\tAA']],
        state: 'state-low',
        label: /Znížená\s+predispozícia/i
      },
      {
        name: 'typical',
        replacements: [['rs17616434\t4\t38816000\tCC','rs17616434\t4\t38816000\tTT']],
        state: 'state-normal',
        label: /Typická\s+predispozícia/i
      }
    ]) {
      const scenarioPage = await browser.newPage({ viewport: { width: 1000, height: 800 }, deviceScaleFactor: 1 });
      scenarioPage.on('pageerror', error => errors.push(error.message));
      await scenarioPage.goto(appUrl);
      const scenarioFixture = scenario.replacements.reduce((content,[from,to])=>content.replace(from,to),fs.readFileSync(fixture,'utf8'));
      await scenarioPage.setInputFiles('#fileInput', { name: `synthetic-milk-${scenario.name}.txt`, mimeType: 'text/plain', buffer: Buffer.from(scenarioFixture) });
      await scenarioPage.waitForSelector('#summaryDashboard:not([hidden])');
      const scenarioCard=scenarioPage.locator('[data-summary-model="milk"]');
      assert.strictEqual(await scenarioCard.evaluate((element,state)=>element.classList.contains(state),scenario.state),true);
      assert.match(await scenarioCard.locator('.summary-circle').innerText(),scenario.label);
      await scenarioPage.close();
    }

    const lactoseLowPage=await browser.newPage({viewport:{width:1000,height:800},deviceScaleFactor:1});
    lactoseLowPage.on('pageerror',error=>errors.push(error.message));
    await lactoseLowPage.goto(appUrl);
    const lactoseLowFixture=fs.readFileSync(fixture,'utf8').replace('rs4988235\t2\t136608646\tGG','rs4988235\t2\t136608646\tAA');
    await lactoseLowPage.setInputFiles('#fileInput',{name:'synthetic-lactose-low.txt',mimeType:'text/plain',buffer:Buffer.from(lactoseLowFixture)});
    await lactoseLowPage.waitForSelector('#summaryDashboard:not([hidden])');
    const lactoseLowCard=lactoseLowPage.locator('[data-summary-model="lactose"]');
    assert.strictEqual(await lactoseLowCard.evaluate(element=>element.classList.contains('state-low')),true);
    assert.match(await lactoseLowCard.locator('.summary-circle').innerText(),/Znížená\s+predispozícia/i);
    await lactoseLowCard.click();
    await lactoseLowPage.waitForSelector('#detailModal.open');
    assert.strictEqual(await lactoseLowPage.locator('#results').evaluate(element=>element.classList.contains('result-low')),true);
    assert.match(await lactoseLowPage.locator('#resultLabel').innerText(),/Znížená predispozícia k poklesu laktázy/i);
    assert.strictEqual(await lactoseLowPage.locator('#bandLow').evaluate(element=>element.classList.contains('active')),true);
    await lactoseLowPage.close();

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
    assert.doesNotMatch(await integerScorePage.locator('#resultCopy').innerText(), /príspevok do skóre|rs115288876|rs63582760/i);
    assert.match(await integerScorePage.locator('#resultCopy').innerText(), /pravdepodobnosť presného skóre/i);
    await integerScorePage.close();

    const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
    mobile.on('pageerror', error => errors.push(error.message));
    await uploadAndWait(mobile);
    await mobile.screenshot({ path: path.join(qaDir, 'overview-mobile.png'), fullPage: true });
    await mobile.locator('[data-summary-model="milk"]').click();
    await mobile.waitForSelector('#detailModal.open');
    assert.strictEqual(await mobile.locator('#histogram .bar-col').count(), 11);
    await mobile.screenshot({ path: path.join(qaDir, 'detail-milk-mobile.png') });
    await mobile.keyboard.press('Escape');
    await mobile.locator('#detailModal').waitFor({state:'hidden'});
    await mobile.locator('[data-summary-model="lactose"]').click();
    await mobile.waitForSelector('#detailModal.open');
    await mobile.screenshot({path:path.join(qaDir,'detail-lactose-mobile.png')});

    assert.deepStrictEqual(errors, []);
    console.log('UI smoke test passed: 7 summary cards, milk, lactose and weighted coeliac detail logic, colour states, 71-row chip/proxy map, EN switch, desktop and mobile layouts.');
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
