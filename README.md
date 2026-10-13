# AlergenRisk

Experimentálna webová aplikácia na interpretáciu vybraných genetických predispozícií súvisiacich s potravinovými alergiami, laktázovou perzistenciou, celiakiou a aktivitou DAO.

## Vlastnosti

- lokálne spracovanie genotypu bez odosielania dát na server,
- import formátov 23andMe, MyHeritage a DNAEra,
- priame cieľové SNP a zabudované EUR proxy markery,
- nevážené súčtové genetické skóre,
- referenčná distribúcia EUR populácie,
- samostatné vyjadrenie neistoty spôsobenej proxy odhadom alebo populačnou imputáciou.
- grafický prehľad všetkých siedmich panelov inšpirovaný vizuálnym systémom správ NU3Gen,
- samostatné modálne okno pre detail každej predispozície.

Výsledok je určený na výskumné a vzdelávacie použitie. Nie je diagnózou alergie ani odporúčaním potravinu konzumovať alebo vyradiť.

## Lokálne spustenie

Aplikácia nemá serverovú časť ani externé závislosti. V koreňovom priečinku repozitára spustite:

```bash
python -m http.server 8000 --directory dist
```

Potom otvorte `http://localhost:8000`.

## GitHub Pages

Workflow v `.github/workflows/pages.yml` automaticky publikuje obsah priečinka `dist` po každom pushi do vetvy `main`.

V GitHub repozitári treba pri prvom nasadení otvoriť **Settings → Pages** a ako **Source** zvoliť **GitHub Actions**. Následne workflow možno spustiť pushom alebo ručne cez kartu **Actions**.

## Štruktúra

- `dist/index.html` – kompletná offline aplikácia,
- `.github/workflows/pages.yml` – automatické nasadenie na GitHub Pages.

## Odborné zdroje arašidového panelu

- Hong X. et al. *Nature Communications* (2015), DOI: [10.1038/ncomms7304](https://doi.org/10.1038/ncomms7304)
- Asai Y. et al. *Journal of Allergy and Clinical Immunology* (2018), DOI: [10.1016/j.jaci.2017.09.015](https://doi.org/10.1016/j.jaci.2017.09.015)


## Verzia 13

Pridané panely pre mlieko, pšenicu, sóju, stromové orechy, sezam, ryby, kôrovce/mäkkýše a histamín/DAO.

Pšenica, sója, orechy, sezam, ryby a morské plody používajú rovnaký všeobecný 3-SNP panel; nejde o alergénovo špecifickú predikciu. Pšenica nehodnotí celiakiu.

Mlieko: 3 spoločné + 2 kandidátne markery. Histamín: 3 varianty AOC1 spojené s DAO aktivitou. Tieto dva výskumné panely počítajú iba priamo zistené alely, uvádzajú rozsah pri chýbaní a nevytvárajú neoverenú EUR distribúciu, rizikové pásma ani percento klinickej istoty.

Zdroje sú uvedené pri každom paneli v aplikácii. Súbor genotypu sa spracúva lokálne bez sieťových požiadaviek.


## Verzia 14

Šesť kategórií s identickým 3-SNP panelom je zlúčených do jednej skupiny „Spoločná predispozícia k potravinovej alergii“: pšenica, sója, stromové orechy, sezam, ryby, kôrovce a mäkkýše. Aplikácia zobrazuje päť jedinečných panelov: vajce, arašidy, mlieko, spoločná predispozícia a DAO. Výpočty sa nemenia.

## Version 15

Slovak/English UI, selectable with `?lang=sk` or `?lang=en`; uploaded data stays in memory when switching languages or panels.

Added separate lactose and partial coeliac susceptibility panels. Lactose uses direct rs4988235 plus-strand GG/AG/AA genotype rules (Enattah 2002, PMID 11788828). Coeliac uses rs2187668 T and rs7454108 C as indirect DQ2.5/DQ8 tags (Monsuur 2008, DOI 10.1371/journal.pone.0002270); it does not cover the full six-SNP assay, DQ2.2/DQ7 or phase. Neither panel imputes missing data or reports disease probabilities. Negative partial HLA tags do not exclude coeliac disease.

Verification: syntax validation; 28 genotype/language cases, including unsupported/missing genotypes; live browser upload with synthetic data. No personal genotype was used for deployment testing.

## Verzia 16

Rozhranie je prepracované podľa vizuálneho jazyka správ NU3Gen: zelené sekčné nadpisy, bodkované deliace línie, kruhové výsledkové značky a farebné rozlíšenie zníženej, typickej, zvýšenej, výskumnej a neúplnej interpretácie.

Po jednom lokálnom importe aplikácia zobrazí spoločné grafické zhrnutie všetkých siedmich panelov. Každá predispozícia sa otvára v samostatnom prístupnom modálnom okne s pôvodným detailom skóre, distribúciou, interpretáciou, SNP tabuľkou a literatúrou. Výpočtové a vedecké pravidlá panelov sa nezmenili.

## Verzia 17

Panel Mlieko používa namiesto priameho rs12123821 marker rs115288876 (plus vlákno G>A, efektová/proxy alela A) ako pravdepodobnostný EUR proxy. Ostatné panely, vrátane Vajca a Spoločnej potravinovej predispozície, naďalej používajú pôvodný rs12123821.

Príspevok pôvodného lokusu sa v mliečnom paneli neberie ako istý genotyp. Aplikácia z podmieneného proxy modelu (EUR r² = 0,698) vypočíta rozdelenie možného príspevku 0/1/2 alely, jeho očakávanú hodnotu, pravdepodobnosť najpravdepodobnejšieho príspevku a výsledný rozsah skóre. Táto neistota je započítaná priamo do odhadu; nejde o klinickú pravdepodobnosť alergie ani presnosť diagnózy.

## Verzia 18

V paneli Mlieko nahrádza rs63582760 cieľový rs11949166 ako druhý pravdepodobnostný proxy marker. Historický identifikátor rs63582760 bol v dbSNP zlúčený do rs10588133, preto aplikácia prijíma oba identifikátory aj ich GRCh37/GRCh38 pozičné zápisy. Ostatné panely naďalej používajú pôvodný rs11949166.

Pre európsku skupinu 1000 Genomes (CEU, TSI, FIN, GBR a IBS) má dvojica rs11949166–rs10588133 v NIH LDlink r² = 0,9551 a D′ = 0,9798. Proxy alela T zodpovedá cieľovej alele A; model používa P(A | T)=267/271 a P(A | G)=5/735. Neistoty rs115288876 aj rs63582760 sa kombinujú do jedného rozdelenia celkového proxy príspevku, z ktorého sa počíta očakávané skóre, najpravdepodobnejší príspevok a rozsah.

## Verzia 19

Genetické skóre panelu Mlieko je opäť vždy celé číslo. Za každý proxy lokus sa vyberie najpravdepodobnejší príspevok 0, 1 alebo 2 cieľové alely a tieto hodnoty sa sčítajú s priamo zistenými alelami.

Pravdepodobnostný model sa už nepoužíva na vytvorenie desatinného skóre. Používa sa iba na výpočet spoľahlivosti zvoleného celého proxy skóre a na zobrazenie ostatných možných celočíselných výsledkov.

## Verzia 20

Na hlavnej stránke pribudla rozbaľovacia mapa všetkých 23 panelových lokusov a ich proxy náhrad v poradí použitia. Tabuľka má samostatné stĺpce pre DNAEra, MyHeritage a 23andMe.

Keďže jednotlivé revízie čipov jednej značky sa môžu líšiť, aplikácia nepredpokladá dostupnosť SNP iba podľa názvu dodávateľa. Po nahratí exportu zvýrazní príslušný stĺpec a pri každom cieli ukáže priamy nález, použitelný proxy marker alebo chýbajúci nález podľa skutočného obsahu súboru.
