# AlergenRisk

Experimentálna webová aplikácia na odhad genetickej predispozície k potravinovým alergiám. Aktuálne obsahuje modely pre vajce a arašidy.

## Vlastnosti

- lokálne spracovanie genotypu bez odosielania dát na server,
- import formátov 23andMe, MyHeritage a DNAEra,
- priame cieľové SNP a zabudované EUR proxy markery,
- nevážené súčtové genetické skóre,
- referenčná distribúcia EUR populácie,
- samostatné vyjadrenie neistoty spôsobenej proxy odhadom alebo populačnou imputáciou.

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
- `.github/workflows/pages.yml` – automatické nasadenie na GitHub Pages,
- `.openai/hosting.json` – konfigurácia existujúceho ChatGPT Sites nasadenia.

## Odborné zdroje arašidového panelu

- Hong X. et al. *Nature Communications* (2015), DOI: [10.1038/ncomms7304](https://doi.org/10.1038/ncomms7304)
- Asai Y. et al. *Journal of Allergy and Clinical Immunology* (2018), DOI: [10.1016/j.jaci.2017.09.015](https://doi.org/10.1016/j.jaci.2017.09.015)


## Verzia 13

Pridané panely pre mlieko, pšenicu, sóju, stromové orechy, sezam, ryby, kôrovce/mäkkýše a histamín/DAO.

Pšenica, sója, orechy, sezam, ryby a morské plody používajú rovnaký všeobecný 3-SNP panel; nejde o alergénovo špecifickú predikciu. Pšenica nehodnotí celiakiu.

Mlieko: 3 spoločné + 2 kandidátne markery. Histamín: 3 varianty AOC1 spojené s DAO aktivitou. Tieto dva výskumné panely počítajú iba priamo zistené alely, uvádzajú rozsah pri chýbaní a nevytvárajú neoverenú EUR distribúciu, rizikové pásma ani percento klinickej istoty.

Zdroje sú uvedené pri každom paneli v aplikácii. Súbor genotypu sa spracúva lokálne bez sieťových požiadaviek.
