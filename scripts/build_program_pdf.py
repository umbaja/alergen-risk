from __future__ import annotations

import re
import shutil
from pathlib import Path

from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "dist" / "index.html"
OUT = ROOT / "output" / "pdf"
DOWNLOADS = ROOT / "dist" / "downloads"
OUTPUT = OUT / "AlergenRisk_Programova_a_metodicka_dokumentacia_v25.pdf"

GREEN = colors.HexColor("#7EA43A")
GREEN_DARK = colors.HexColor("#4F7227")
GREEN_PALE = colors.HexColor("#EAF2DD")
BLUE = colors.HexColor("#338FBA")
DARK = colors.HexColor("#2D4B53")
INK = colors.HexColor("#2D3D45")
MUTED = colors.HexColor("#687A83")
LINE = colors.HexColor("#CAD9D8")
PALE = colors.HexColor("#EAF3F5")
BG = colors.HexColor("#F4F8F7")
WHITE = colors.white

PANEL_NAMES = {
    "egg": "Vajce",
    "peanut": "Arašidy",
    "milk": "Kravské mlieko",
    "shared": "Spoločná potravinová predispozícia",
    "lactose": "Laktóza",
    "celiac": "Celiakia",
    "histamine": "Histamín / DAO",
}

GENES = {
    "rs12123821": "FLG-AS1 / FLG",
    "rs11949166": "IL4 / KIF3A",
    "rs2212434": "C11orf30 / LRRC32",
    "rs1243064": "SERPINB7 / SERPINB2",
    "rs7192": "HLA-DRA",
    "rs9275596": "HLA-DQB1 / HLA-DQA2",
    "rs7936434": "C11orf30 / EMSY",
    "rs7475217": "CTNNA3",
    "rs744597": "ARHGAP24",
    "rs17616434": "TLR6 región",
    "rs2069772": "IL2 / ADAD1",
    "rs4988235": "MCM6 / LCT",
    "rs2052129": "AOC1 regulačný región",
    "rs10156191": "AOC1 Thr16Met",
    "rs1049742": "AOC1 Ser332Phe",
}


def register_fonts() -> None:
    regular = Path("C:/Windows/Fonts/arial.ttf")
    bold = Path("C:/Windows/Fonts/arialbd.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("NuRegular", regular))
        pdfmetrics.registerFont(TTFont("NuBold", bold))
    else:
        pdfmetrics.registerFont(TTFont("NuRegular", "DejaVuSans.ttf"))
        pdfmetrics.registerFont(TTFont("NuBold", "DejaVuSans-Bold.ttf"))


register_fonts()
STYLES = getSampleStyleSheet()
STYLES.add(ParagraphStyle(name="CoverBrand", fontName="NuBold", fontSize=9, leading=12, textColor=GREEN_DARK, spaceAfter=28))
STYLES.add(ParagraphStyle(name="Eyebrow", fontName="NuBold", fontSize=8, leading=11, textColor=GREEN, spaceBefore=8, spaceAfter=7, tracking=1.0))
STYLES.add(ParagraphStyle(name="CoverTitle", fontName="NuBold", fontSize=31, leading=33, textColor=INK, spaceAfter=16))
STYLES.add(ParagraphStyle(name="CoverLead", fontName="NuRegular", fontSize=11.5, leading=17, textColor=MUTED, spaceAfter=18))
STYLES.add(ParagraphStyle(name="H1", fontName="NuBold", fontSize=22, leading=26, textColor=INK, spaceBefore=2, spaceAfter=11))
STYLES.add(ParagraphStyle(name="H2", fontName="NuBold", fontSize=13, leading=17, textColor=GREEN_DARK, spaceBefore=13, spaceAfter=7))
STYLES.add(ParagraphStyle(name="H3", fontName="NuBold", fontSize=9.5, leading=13, textColor=GREEN_DARK, spaceBefore=8, spaceAfter=4))
STYLES.add(ParagraphStyle(name="Body", fontName="NuRegular", fontSize=9, leading=13.5, textColor=INK, spaceAfter=7))
STYLES.add(ParagraphStyle(name="Small", fontName="NuRegular", fontSize=7.3, leading=10, textColor=MUTED, spaceAfter=4))
STYLES.add(ParagraphStyle(name="Cell", fontName="NuRegular", fontSize=6.45, leading=8.25, textColor=INK, spaceAfter=0))
STYLES.add(ParagraphStyle(name="CellHead", fontName="NuBold", fontSize=6.45, leading=8, textColor=WHITE, spaceAfter=0))
STYLES.add(ParagraphStyle(name="White", fontName="NuRegular", fontSize=8.8, leading=12.5, textColor=WHITE, spaceAfter=0))
STYLES.add(ParagraphStyle(name="WhiteBold", fontName="NuBold", fontSize=9.5, leading=12.5, textColor=WHITE, spaceAfter=0))
STYLES.add(ParagraphStyle(name="Part", fontName="NuBold", fontSize=27, leading=30, textColor=INK, spaceAfter=13))


def p(text: str, style: str = "Body") -> Paragraph:
    return Paragraph(text, STYLES[style])


def bullets(items: list[str]) -> list[Paragraph]:
    return [Paragraph(f"• {item}", ParagraphStyle(
        name=f"bullet-{index}-{len(item)}",
        parent=STYLES["Body"],
        leftIndent=11,
        firstLineIndent=-8,
        spaceAfter=4,
    )) for index, item in enumerate(items)]


def section(title: str, kicker: str) -> list:
    return [p(kicker.upper(), "Eyebrow"), p(title, "H1")]


def banner(title: str, text: str, color=GREEN_DARK) -> Table:
    table = Table([[p(title, "WhiteBold"), p(text, "White")]], colWidths=[45 * mm, 122 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return table


def info_cards(items: list[tuple[str, str]]) -> Table:
    cells = [Paragraph(
        f"<font color='#4F7227' size='7'><b>{label}</b></font><br/><font size='15'><b>{value}</b></font>",
        STYLES["Body"],
    ) for label, value in items]
    width = 167 * mm / len(items)
    table = Table([cells], colWidths=[width] * len(items), hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), WHITE),
        ("BOX", (0, 0), (-1, -1), .7, LINE),
        ("INNERGRID", (0, 0), (-1, -1), .7, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    return table


def data_table(rows: list[list[object]], widths: list[float], compact: bool = False) -> Table:
    formatted = []
    for row_index, row in enumerate(rows):
        style = STYLES["CellHead"] if row_index == 0 else (STYLES["Cell"] if compact else STYLES["Small"])
        formatted.append([cell if hasattr(cell, "wrap") else Paragraph(str(cell), style) for cell in row])
    table = Table(formatted, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GREEN_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#F8FBF9")]),
        ("GRID", (0, 0), (-1, -1), .45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4 if compact else 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4 if compact else 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4 if compact else 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4 if compact else 6),
    ]))
    return table


def page_background(canvas, doc) -> None:
    canvas.saveState()
    width, height = doc.pagesize
    canvas.setFillColor(BG)
    canvas.rect(0, 0, width, height, fill=1, stroke=0)
    canvas.setStrokeColor(GREEN)
    canvas.setLineWidth(1.2)
    canvas.line(doc.leftMargin, 16 * mm, width - doc.rightMargin, 16 * mm)
    canvas.setFont("NuBold", 7)
    canvas.setFillColor(GREEN_DARK)
    canvas.drawString(doc.leftMargin, 10 * mm, "NU3GEN / ALERGENRISK")
    canvas.setFont("NuRegular", 7)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(width - doc.rightMargin, 10 * mm, f"PROGRAMOVÁ DOKUMENTÁCIA  |  {canvas.getPageNumber():02d}")
    canvas.restoreState()


def document(path: Path) -> BaseDocTemplate:
    doc = BaseDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=21 * mm,
        rightMargin=21 * mm,
        topMargin=20 * mm,
        bottomMargin=23 * mm,
        title="AlergenRisk - programová a metodická dokumentácia",
        author="NU3GEN",
        subject="Používateľský, vedecký a technický opis nasadenej aplikácie AlergenRisk v25",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="content")
    doc.addPageTemplates(PageTemplate(id="standard", frames=[frame], onPage=page_background))
    return doc


def extract_balanced(text: str, anchor: str, opener: str, closer: str) -> str:
    start = text.index(anchor)
    start = text.index(opener, start)
    depth = 0
    quote = None
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"', "`"}:
            quote = char
            continue
        if char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    raise ValueError(f"Neuzavretý blok za {anchor}")


def top_level_objects(array_text: str) -> list[str]:
    objects = []
    depth = 0
    start = None
    quote = None
    escaped = False
    for index, char in enumerate(array_text):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"', "`"}:
            quote = char
        elif char == "{":
            if depth == 0:
                start = index
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0 and start is not None:
                objects.append(array_text[start:index + 1])
                start = None
    return objects


def js_number(value: str) -> float:
    value = value.strip()
    if value.startswith("."):
        value = "0" + value
    if value.startswith("-."):
        value = "-0" + value[1:]
    return float(value)


def parse_object_loci(html: str, anchor: str, panel: str) -> list[dict]:
    block = extract_balanced(html, anchor, "[", "]")
    records = []
    for obj in top_level_objects(block):
        target = re.search(r"\bid:'(rs\d+)'", obj)
        risk = re.search(r"\brisk:'([ACGT])'", obj)
        non_risk = re.search(r"\bnonRisk:'([ACGT])'", obj)
        beta = re.search(r"\bbeta:([+\-]?(?:\d+(?:\.\d*)?|\.\d+))", obj)
        if not (target and risk and non_risk and beta):
            continue
        proxies = []
        for match in re.finditer(
            r"\{id:'(rs\d+)'[^{}]*?riskAllele:'([ACGT])'[^{}]*?r2:([+\-]?(?:\d+(?:\.\d*)?|\.\d+))[^{}]*?dPrime:([+\-]?(?:\d+(?:\.\d*)?|\.\d+))",
            obj,
        ):
            proxies.append({"id": match.group(1), "allele": match.group(2), "r2": js_number(match.group(3)), "d_prime": js_number(match.group(4))})
        records.append({
            "panel": panel,
            "target": target.group(1),
            "gene": GENES[target.group(1)],
            "allele": risk.group(1),
            "other": non_risk.group(1),
            "weight": js_number(beta.group(1)),
            "group": "GWAS panel",
            "role": "Nevážený príspevok 0/1/2; beta dokumentuje publikačný efekt",
            "proxies": proxies,
            "missing": "EUR očakávanie; neistota oddelene",
        })
    return records


def parse_tuple_loci(html: str, anchor: str, panel: str, group: str) -> list[dict]:
    block = extract_balanced(html, anchor, "[", "]")
    pattern = re.compile(r"\['(rs\d+)','([ACGT])',([+\-]?(?:\d+(?:\.\d*)?|\.\d+)),([+\-]?(?:\d+(?:\.\d*)?|\.\d+)),'([^']+)'\]")
    return [{
        "panel": panel,
        "target": match.group(1),
        "gene": match.group(5),
        "allele": match.group(2),
        "other": "-",
        "weight": js_number(match.group(3)),
        "frequency": js_number(match.group(4)),
        "group": group,
        "role": "Vážený aditívny príspevok do GRS",
        "proxies": [],
        "missing": "Proxy r2 >= 0,90; inak populačná neistota",
    } for match in pattern.finditer(block)]


def parse_hla_loci(html: str) -> list[dict]:
    block = extract_balanced(html, "const celiacHlaMarkers=", "[", "]")
    pattern = re.compile(r"\['(rs\d+)','([ACGT])','([^']+)','([^']+)'\]")
    return [{
        "panel": "celiac",
        "target": match.group(1),
        "gene": match.group(4),
        "allele": match.group(2),
        "other": "-",
        "weight": None,
        "group": "HLA tag",
        "role": f"Odhad haplotypu {match.group(3)}; váha patrí diplotypu",
        "proxies": [],
        "missing": "Proxy r2 >= 0,90; inak HLA populačná neistota",
    } for match in pattern.finditer(block)]


def parse_celiac_proxies(html: str) -> dict[str, list[dict]]:
    block = extract_balanced(html, "const celiacProxyCatalog=", "{", "}")
    result: dict[str, list[dict]] = {}
    for target, values in re.findall(r"(?m)^\s*(rs\d+):\[(.*?)\],?\s*$", block):
        result[target] = []
        for match in re.finditer(
            r"celiacProxy\('([^']+)','([ACGT])',([+\-]?(?:\d+(?:\.\d*)?|\.\d+)),([+\-]?(?:\d+(?:\.\d*)?|\.\d+)),",
            values,
        ):
            result[target].append({
                "id": match.group(1),
                "allele": match.group(2),
                "r2": js_number(match.group(3)),
                "d_prime": js_number(match.group(4)),
            })
    return result


def clone_record(record: dict, panel: str, weight: float) -> dict:
    clone = dict(record)
    clone["panel"] = panel
    clone["weight"] = weight
    clone["role"] = "Nevážený príspevok 0/1/2; beta dokumentuje všeobecný GWAS efekt"
    return clone


def build_records(html: str) -> tuple[int, list[dict]]:
    version_match = re.search(r"AlergenRisk\s*·\s*verzia\s*(\d+)", html)
    if not version_match:
        raise ValueError("Verzia aplikácie nebola nájdená")
    version = int(version_match.group(1))
    egg = parse_object_loci(html, "const eggLoci", "egg")
    peanut = parse_object_loci(html, "const peanutLoci", "peanut")
    shared_weights = [0.97456, 0.462035, 0.300105]
    shared = [clone_record(record, "shared", shared_weights[index]) for index, record in enumerate(egg[:3])]
    milk = [
        {"panel": "milk", "target": "rs12123821", "gene": GENES["rs12123821"], "allele": "T", "other": "C", "weight": 1.008, "group": "povinná proxy", "role": "Celý príspevok 0/1/2 odvodený z rs115288876", "proxies": [{"id": "rs115288876", "allele": "A", "r2": .698182, "d_prime": .914501}], "missing": "Bez proxy sa cieľ nepovažuje za priamo určený"},
        {"panel": "milk", "target": "rs11949166", "gene": GENES["rs11949166"], "allele": "A", "other": "T", "weight": .478, "group": "povinná proxy", "role": "Celý príspevok 0/1/2 odvodený z rs63582760 / rs10588133", "proxies": [{"id": "rs63582760 / rs10588133", "allele": "T", "r2": .9551, "d_prime": .9798}], "missing": "Bez proxy sa cieľ nepovažuje za priamo určený"},
        {"panel": "milk", "target": "rs2212434", "gene": GENES["rs2212434"], "allele": "T", "other": "C", "weight": .300105, "group": "priamy GWAS lokus", "role": "Nevážený príspevok 0/1/2", "proxies": [], "missing": "Chýbajúci priamy marker znižuje pokrytie"},
        {"panel": "milk", "target": "rs17616434", "gene": GENES["rs17616434"], "allele": "C", "other": "T", "weight": None, "group": "kandidátny lokus", "role": "Nevážený príspevok 0/1/2", "proxies": [], "missing": "Chýbajúci priamy marker znižuje pokrytie"},
        {"panel": "milk", "target": "rs2069772", "gene": GENES["rs2069772"], "allele": "T", "other": "C", "weight": None, "group": "povinná proxy", "role": "Celý príspevok 0/1/2 odvodený z rs17388568", "proxies": [{"id": "rs17388568", "allele": "G", "r2": .981, "d_prime": 1.0}], "missing": "Bez proxy sa cieľ nepovažuje za priamo určený"},
    ]
    lactose = [{"panel": "lactose", "target": "rs4988235", "gene": GENES["rs4988235"], "allele": "G", "other": "A", "weight": None, "group": "genotypové pravidlo", "role": "GG nonperzistencia; AG/AA perzistencia", "proxies": [], "missing": "Bez imputácie; výsledok neurčený"}]
    histamine = [{"panel": "histamine", "target": target, "gene": GENES[target], "allele": "T", "other": other, "weight": None, "group": "AOC1 kandidátny lokus", "role": "Priamy počet efektových alel 0/1/2", "proxies": [], "missing": "Bez imputácie; znížené pokrytie"} for target, other in [("rs2052129", "G"), ("rs10156191", "C"), ("rs1049742", "C")]]
    core = parse_tuple_loci(html, "const celiacCoreLoci=", "celiac", "jadro PGS000316")
    research = parse_tuple_loci(html, "const celiacResearchLoci=", "celiac", "výskumné rozšírenie")
    hla = parse_hla_loci(html)
    proxy_map = parse_celiac_proxies(html)
    for record in [*core, *research, *hla]:
        record["proxies"] = proxy_map.get(record["target"], [])
    records = [*egg, *peanut, *milk, *shared, *lactose, *core, *research, *hla, *histamine]
    if version != 25:
        raise AssertionError(f"Dokument je pripravený pre verziu 25, zdroj obsahuje verziu {version}")
    if len(records) != 71:
        raise AssertionError(f"Očakáva sa 71 panel-lokus záznamov, získaných {len(records)}")
    return version, records


def fmt(value: float | None, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{digits}f}".replace(".", ",")


def proxy_text(proxies: list[dict]) -> str:
    if not proxies:
        return "Bez proxy"
    return "; ".join(f"{proxy['id']} ({proxy['allele']}; r2 {fmt(proxy['r2'])}; D' {fmt(proxy['d_prime'])})" for proxy in proxies)


def cover(version: int, records: list[dict]) -> list:
    return [
        p("NU3GEN / ALERGENRISK / NASADENÁ APLIKÁCIA", "CoverBrand"),
        Spacer(1, 19 * mm),
        p(f"PROGRAMOVÁ DOKUMENTÁCIA / VERZIA {version}", "Eyebrow"),
        p("AlergenRisk", "CoverTitle"),
        p("Používateľský, vedecký a technický opis nasadenej webovej aplikácie na interpretáciu vybraných genetických predispozícií.", "CoverLead"),
        Spacer(1, 7 * mm),
        info_cards([("PANELY", "7"), ("PANEL-LOKUSY", str(len(records))), ("UNIKÁTNE rsID", str(len({row['target'] for row in records})))]),
        Spacer(1, 12 * mm),
        banner("STATUS", "Dokument opisuje produkčne nasadenú verziu 25. Aplikácia je určená na výskumné a vzdelávacie použitie; výsledok nie je diagnóza ani liečebné odporúčanie."),
        PageBreak(),
    ]


def part_cover(number: str, title: str, subtitle: str, facts: list[tuple[str, str]]) -> list:
    return [
        Spacer(1, 20 * mm),
        p(f"ČASŤ {number}", "Eyebrow"),
        p(title, "Part"),
        p(subtitle, "CoverLead"),
        Spacer(1, 9 * mm),
        info_cards(facts),
        PageBreak(),
    ]


def contents() -> list:
    return section("Obsah a účel dokumentu", "orientácia") + [
        data_table([
            ["Časť", "Obsah", "Pre koho"],
            ["I. Používateľský opis", "Import DNA, hlavný prehľad, detaily panelov a interpretácia", "Používateľ a odborný konzultant"],
            ["II. Metodika", "Vedecká logika siedmich panelov a kompletný register markerov", "Genetik, metodik, audítor"],
            ["III. Technická správa", "Architektúra, parser, proxy, neistota a ochrana dát", "Vývojár a technický audítor"],
            ["IV. QA a hranice", "Rozsah testov, stav validácie a podmienky správneho použitia", "Vlastník produktu a hodnotiteľ"],
        ], [39 * mm, 77 * mm, 51 * mm]),
        Spacer(1, 7 * mm),
        banner("ROZSAH", "Dokument opisuje reálne správanie statickej aplikácie. Výskumné metriky samostatného ML pilotu sa sem neprenášajú ako klinická validácia produkčného programu.", DARK),
        PageBreak(),
    ]


def user_flow_diagram() -> Drawing:
    drawing = Drawing(470, 250)
    labels = ["1. Export DNA", "2. Lokálny parser", "3. Priamy SNP / proxy", "4. Skóre a neistota", "5. Grafické zhrnutie", "6. Detail panelu"]
    positions = [(5, 150), (125, 150), (245, 150), (365, 150), (95, 55), (275, 55)]
    for index, (label, (x, y)) in enumerate(zip(labels, positions)):
        fill = GREEN_PALE if index % 2 == 0 else PALE
        drawing.add(Rect(x, y, 100, 50, rx=6, ry=6, fillColor=fill, strokeColor=GREEN_DARK, strokeWidth=.8))
        drawing.add(String(x + 50, y + 26, label, textAnchor="middle", fontName="NuBold", fontSize=6.8, fillColor=INK))
    for x in (108, 228, 348):
        drawing.add(Line(x, 175, x + 14, 175, strokeColor=GREEN, strokeWidth=1.4))
        drawing.add(Polygon([x + 14, 175, x + 9, 178, x + 9, 172], fillColor=GREEN, strokeColor=None))
    drawing.add(Line(415, 145, 145, 108, strokeColor=GREEN, strokeWidth=1.2))
    drawing.add(Polygon([145, 108, 152, 112, 151, 104], fillColor=GREEN, strokeColor=None))
    drawing.add(Line(198, 80, 272, 80, strokeColor=GREEN, strokeWidth=1.4))
    drawing.add(Polygon([272, 80, 267, 83, 267, 77], fillColor=GREEN, strokeColor=None))
    drawing.add(String(235, 20, "Genotypový súbor zostáva počas výpočtu v pamäti prehliadača", textAnchor="middle", fontName="NuRegular", fontSize=8.3, fillColor=MUTED))
    return drawing


def user_section(version: int) -> list:
    story = part_cover("I", "Používateľský opis", "Čo program robí, ako sa používa a ako správne čítať jeho výsledky.", [("VERZIA", str(version)), ("JAZYKY", "SK / EN"), ("FORMÁTY", "3")])
    story += section("Účel programu", "I.01 / zameranie")
    story += [
        p("AlergenRisk je statická webová aplikácia na orientačnú interpretáciu vybraných genetických predispozícií súvisiacich s potravinovými alergiami, laktázovou perzistenciou, celiakiou a aktivitou enzýmu DAO. Po jednom importe vytvorí spoločný prehľad siedmich panelov a každý výsledok otvorí v samostatnom detailnom okne."),
        banner("DÔLEŽITÉ", "Program neidentifikuje aktuálnu alergiu, nenahrádza anamnézu, laboratórne vyšetrenie, eliminačný alebo provokačný test a neurčuje bezpečnosť konzumácie potraviny.", GREEN_DARK),
    ]
    story += section("Podporovaný vstup", "I.02 / DNA export")
    story += [data_table([
        ["Zdroj", "Očakávaný obsah", "Rozpoznanie"],
        ["23andMe", "Textový export s rsID, chromozómom, pozíciou a genotypom", "Automaticky podľa hlavičky a stĺpcov"],
        ["MyHeritage", "CSV export s RSID, CHROMOSOME, POSITION, RESULT", "Automaticky podľa hlavičky"],
        ["DNAEra", "GSGT / Illumina CSV s alelami v plus orientácii", "Automaticky podľa sekcie Data"],
    ], [36 * mm, 78 * mm, 53 * mm]), p("Jednotlivé revízie DNA čipov sa môžu líšiť. Program preto nepredpokladá dostupnosť markera iba podľa značky. Reálnu dostupnosť overuje priamo v nahratom súbore.")]
    story += section("Používateľský tok", "I.03 / od súboru k výsledku")
    story += [user_flow_diagram(), banner("OCHRANA DÁT", "Výpočet prebieha v prehliadači. Nasadená verzia nemá serverovú analytickú časť a genotypový súbor sa neodosiela na spracovanie.", BLUE), PageBreak()]
    story += section("Sedem zobrazených panelov", "I.04 / hlavný prehľad")
    story += [data_table([
        ["Panel", "Výstup", "Základ interpretácie"],
        ["Vajce", "Skóre 0-8", "4 GWAS ciele; direct alebo EUR proxy"],
        ["Arašidy", "Skóre 0-10", "2 replikované HLA a 3 kandidátne lokusy"],
        ["Kravské mlieko", "Skóre 0-10", "3 povinné proxy a 2 priame ciele"],
        ["Spoločná predispozícia", "Skóre 0-6", "3 všeobecné food-allergy lokusy"],
        ["Laktóza", "Genotyp GG / AG / AA", "Priame pravidlo rs4988235 bez imputácie"],
        ["Celiakia", "Vážené GRS a HLA diplotyp", "38 jadrových, 4 výskumné a 8 HLA tag markerov"],
        ["Histamín / DAO", "Počet alel 0-6", "3 priame AOC1 varianty"],
    ], [35 * mm, 44 * mm, 88 * mm], compact=True)]
    story += section("Farby a slovné pásma", "I.05 / vizuálna interpretácia")
    story += [data_table([
        ["Farba", "Význam", "Čo neznamená"],
        ["Zelená", "Znížená relatívna predispozícia v rámci modelu", "Vylúčenie alergie alebo ochorenia"],
        ["Modrá", "Typická predispozícia voči modelovej referencii", "Priemernú klinickú pravdepodobnosť"],
        ["Okrová", "Zvýšená relatívna predispozícia v rámci modelu", "Diagnózu alebo očakávanú závažnosť"],
        ["Sivá", "Nedostatočné pokrytie alebo neurčený výsledok", "Negatívny výsledok"],
    ], [33 * mm, 67 * mm, 67 * mm]), p("Pri laktóze farba opisuje predispozíciu k poklesu laktázy, nie alergiu na mliečne bielkoviny. Pri celiakii je pásmo relatívne voči modelovej EUR/CEU distribúcii a nesmie sa čítať ako percento ochorenia.")]
    story += section("Čo obsahuje detail panelu", "I.06 / vysvetliteľnosť")
    story += bullets([
        "výsledkové skóre alebo genotyp a opis príslušného pásma",
        "spôsob určenia: priamy genotyp, proxy odhad alebo populačná neistota",
        "referenčnú distribúciu tam, kde má model definovanú referenciu",
        "praktickú interpretáciu a klinické upozornenie",
        "tabuľku cieľových SNP, nájdených genotypov, príspevkov a použitých proxy",
        "pôvod modelu a odkazy na vedecké zdroje",
    ])
    story.append(PageBreak())
    return story


def methodology_section(records: list[dict]) -> list:
    story = part_cover("II", "Metodika a markery", "Vedecký rámec panelov, skórovacie pravidlá a úplný register 71 panel-lokus záznamov.", [("PANELY", "7"), ("ZÁZNAMY", "71"), ("UNIKÁTNE rsID", str(len({row['target'] for row in records})))])
    story += section("Spoločné metodické zásady", "II.01 / modelová logika")
    story += bullets([
        "Efektové alely sa vždy interpretujú v explicitne určenej orientácii.",
        "Priamy cieľ má prednosť pred proxy, okrem troch zámerne proxy založených cieľov mliečneho panelu.",
        "Proxy nenesie ďalší samostatný bod; iba nahrádza chýbajúci cieľ.",
        "Genetický príspevok a technická neistota sú oddelené veličiny.",
        "Opisné pásma alergénových panelov nie sú klinicky kalibrované prahy.",
        "Populačný odhad nie je genotyp osoby a nesmie sa tak prezentovať.",
    ])
    story += section("Metodika jednotlivých panelov", "II.02 / vedecké použitie")
    story += [data_table([
        ["Panel", "Výpočet", "Primárny zdroj", "Hlavné obmedzenie"],
        ["Vajce", "Nevážený počet rizikových alel", "Marenholz 2017", "Opisné pásma; nie klinické PRS"],
        ["Arašidy", "Nevážený 5-lokusový súčet", "Hong 2015; Asai 2018", "HLA lokusy môžu niesť spoločný LD signál"],
        ["Mlieko", "Celý 5-lokusový súčet 0-10", "Henneman 2016; Marenholz 2017", "Malá kandidátna štúdia a 3 proxy"],
        ["Spoločná", "Nevážený 3-lokusový súčet", "Marenholz 2017", "Nerozlišuje jednotlivé potraviny"],
        ["Laktóza", "Priame genotypové pravidlo", "Enattah 2002", "Najsilnejšie pre európsky pôvod"],
        ["Celiakia", "Vážené GRS + HLA diplotyp", "PGS000316; Sharp 2020; Monsuur 2008", "Relatívna predispozícia, nie absolútne riziko"],
        ["Histamín / DAO", "Priamy počet AOC1 alel", "Maintz 2011", "DAO aktivita nie je diagnóza intolerancie"],
    ], [30 * mm, 44 * mm, 47 * mm, 46 * mm], compact=True)]
    story += section("Register všetkých markerov", "II.03 / produkčný model")
    story += [p("Rovnaký rsID môže byť použitý vo viacerých paneloch s inou úlohou alebo váhou. Preto sa eviduje 71 panel-lokus záznamov a 65 unikátnych cieľových rsID.")]
    for panel in ["egg", "peanut", "milk", "shared", "lactose", "celiac", "histamine"]:
        panel_records = [record for record in records if record["panel"] == panel]
        rows = [["Cieľ / gén", "Efekt / váha", "Úloha v programe", "Proxy a chýbanie"]]
        for record in panel_records:
            weight = "HLA diplotyp" if record["group"] == "HLA tag" else (fmt(record["weight"]) if record["weight"] is not None else "pravidlo / nevážené")
            rows.append([
                f"<b>{record['target']}</b><br/>{record['gene']}",
                f"{record['allele']} / {weight}<br/>{record['group']}",
                record["role"],
                f"{proxy_text(record['proxies'])}<br/><font color='#687A83'>{record['missing']}</font>",
            ])
        story += [p(f"{PANEL_NAMES[panel]} ({len(panel_records)} záznamov)", "H2"), data_table(rows, [37 * mm, 37 * mm, 44 * mm, 49 * mm], compact=True), Spacer(1, 4 * mm)]
    story += section("Vedecké zdroje", "II.04 / bibliografia")
    story += [data_table([
        ["Oblasť", "Citácia / identifikátor", "Použitie"],
        ["Potravinová alergia", "Marenholz et al. 2017, DOI 10.1038/s41467-017-01220-0", "Vajce a spoločný panel"],
        ["Arašidy", "Hong et al. 2015, DOI 10.1038/ncomms7304", "Replikované HLA asociácie"],
        ["Arašidy", "Asai et al. 2018, DOI 10.1016/j.jaci.2017.09.015", "Kandidátne lokusy"],
        ["Mlieko", "Henneman et al. 2016, DOI 10.1186/s13601-016-0096-9", "Kandidátne varianty"],
        ["Laktóza", "Enattah et al. 2002, PMID 11788828", "rs4988235 pravidlo"],
        ["Histamín / DAO", "Maintz et al. 2011, DOI 10.1111/j.1398-9995.2011.02548.x", "AOC1 a aktivita DAO"],
        ["Celiakia", "PGS000316; Sharp 2020; Monsuur 2008", "GRS42, HLA tagy a diplotyp"],
        ["Proxy", "1000 Genomes Phase 3 EUR; Ensembl; NIH LDlink", "r2, D' a mapovanie alel"],
    ], [35 * mm, 83 * mm, 49 * mm], compact=True), banner("VEDECKÁ HRANICA", "Zobrazený výsledok je relatívna genetická interpretácia. Bez nezávislej klinickej kalibrácie sa nesmie označovať ako individuálna pravdepodobnosť ochorenia.", DARK), PageBreak()]
    return story


def architecture_diagram() -> Drawing:
    drawing = Drawing(470, 255)
    blocks = [
        (15, 165, 120, 55, "dist/index.html", "UI + parser + modely"),
        (175, 165, 120, 55, "Pamäť prehliadača", "genotypový súbor"),
        (335, 165, 120, 55, "Lokálny výpočet", "skóre + neistota"),
        (95, 55, 120, 55, "Výsledkové karty", "7 panelov"),
        (255, 55, 120, 55, "Detail a audit", "SNP + proxy + zdroje"),
    ]
    for index, (x, y, w, h, title, sub) in enumerate(blocks):
        drawing.add(Rect(x, y, w, h, rx=6, ry=6, fillColor=GREEN_PALE if index % 2 == 0 else PALE, strokeColor=GREEN_DARK, strokeWidth=.8))
        drawing.add(String(x + w / 2, y + 33, title, textAnchor="middle", fontName="NuBold", fontSize=8, fillColor=INK))
        drawing.add(String(x + w / 2, y + 17, sub, textAnchor="middle", fontName="NuRegular", fontSize=7, fillColor=MUTED))
    for x in (138, 298):
        drawing.add(Line(x, 192, x + 34, 192, strokeColor=GREEN, strokeWidth=1.4))
        drawing.add(Polygon([x + 34, 192, x + 29, 195, x + 29, 189], fillColor=GREEN, strokeColor=None))
    drawing.add(Line(395, 160, 190, 113, strokeColor=GREEN, strokeWidth=1.2))
    drawing.add(Polygon([190, 113, 197, 117, 196, 109], fillColor=GREEN, strokeColor=None))
    drawing.add(Line(218, 82, 252, 82, strokeColor=GREEN, strokeWidth=1.4))
    drawing.add(Polygon([252, 82, 247, 85, 247, 79], fillColor=GREEN, strokeColor=None))
    drawing.add(String(235, 20, "Žiadna aplikačná databáza ani serverová analytická služba", textAnchor="middle", fontName="NuRegular", fontSize=8.3, fillColor=MUTED))
    return drawing


def technical_section(records: list[dict]) -> list:
    story = part_cover("III", "Technická správa", "Architektúra nasadenia, spracovanie vstupu, proxy hierarchia a výpočet neistoty.", [("APLIKÁCIA", "1 HTML"), ("SERVER", "bez API"), ("MAPA", "71 riadkov")])
    story += section("Architektúra nasadenia", "III.01 / statická aplikácia")
    story += [architecture_diagram(), data_table([
        ["Vrstva", "Implementácia", "Dôsledok"],
        ["Hosting", "GitHub Pages publikuje priečinok dist", "Jednoduché verzované nasadenie"],
        ["Aplikácia", "Jeden samostatný súbor dist/index.html", "Bez runtime balíčkov a build servera"],
        ["Spracovanie", "JavaScript v prehliadači", "Genotyp zostáva lokálny"],
        ["Modely", "Vložené dátové štruktúry a funkcie", "Rovnaká verzia UI a výpočtovej logiky"],
        ["Jazyky", "Slovenčina a angličtina", "Prepnutie bez straty nahratých dát"],
    ], [35 * mm, 67 * mm, 65 * mm], compact=True)]
    story += section("Parser a normalizácia", "III.02 / vstupná vrstva")
    story += bullets([
        "rozpozná textové, CSV a Illumina/GSGT hlavičky podporovaných exportov",
        "normalizuje genotyp na dve bázy v plus orientácii",
        "indexuje rsID aj vybrané pozičné aliasy GRCh37/GRCh38",
        "odmietne neplatné alebo nepodporované alelové zápisy",
        "dostupnosť markerov určuje podľa obsahu súboru, nie podľa marketingového názvu čipu",
    ])
    story += section("Hierarchia genetického dôkazu", "III.03 / direct, proxy, population, missing")
    story += [data_table([
        ["Priorita", "Zdroj", "Genetický príspevok", "Technická neistota"],
        ["1", "Priamy cieľ", "Dávka 0/1/2", "Najnižšia; genotyp je priamo pozorovaný"],
        ["2", "Povolená proxy", "Celý odhad 0/1/2 alebo distribúcia dávky", "r2 a podmienené pravdepodobnosti"],
        ["3", "Populačná referencia", "Očakávaná hodnota iba tam, kde je povolená", "Kvalita 0; nie osobný genotyp"],
        ["4", "Missing", "Bez individuálneho príspevku", "Výsledok neurčený alebo s nižším pokrytím"],
    ], [20 * mm, 38 * mm, 59 * mm, 50 * mm], compact=True), PageBreak()]
    story += section("Špeciálne výpočtové vetvy", "III.04 / mlieko, laktóza, celiakia")
    story += [
        p("Kravské mlieko", "H2"),
        p("Tri ciele sa zámerne určujú cez rs115288876, rs63582760 / rs10588133 a rs17388568. Pre každý cieľ sa vyberie najpravdepodobnejší celý príspevok 0, 1 alebo 2. Pravdepodobnostný model sa používa iba na spoľahlivosť presného skóre a stabilitu pásma. Desatinná pravdepodobnosť sa nepripočítava ako genetický bod."),
        p("Laktóza", "H2"),
        p("Priamy rs4988235 sa vyhodnotí ako GG, AG alebo AA. Chýbajúci marker sa neimputuje. Hodnota 100 % pri priamom určení znamená úplný technický pôvod z priameho genotypu, nie diagnostickú presnosť."),
        p("Celiakia", "H2"),
        p("Výpočet kombinuje 38 aditívnych jadrových variantov, 4 výskumné varianty a HLA diplotyp odvodený z 8 tag markerov. Pri chýbaní cieľa sa používajú iba auditované EUR proxy s r2 >= 0,90. Distribúcie dávok a HLA posterior vstupujú do 90 % intervalu a stability pásma."),
        banner("KĽÚČOVÉ ODDELENIE", "Celé genetické skóre, pravdepodobnosť presného proxy odhadu a klinická platnosť sú tri rozdielne veličiny. Rozhranie ich nesmie zlúčiť do jedného percenta.", BLUE),
    ]
    story += section("Mapa lokusov podľa DNA čipu", "III.05 / transparentnosť")
    proxy_targets = sum(bool(record["proxies"]) for record in records)
    story += [p(f"Rozbaľovacia mapa obsahuje 71 panel-lokus riadkov. Z nich {proxy_targets} má aspoň jednu technickú proxy. Stĺpce DNAEra, MyHeritage a 23andMe sa po importe naplnia podľa skutočne nájdených markerov."), data_table([
        ["Stav", "Význam"],
        ["Priamy rsID", "Cieľový marker je v súbore a má prednosť"],
        ["Proxy rsID", "Cieľ chýba, použitá je zaregistrovaná náhrada"],
        ["Chýba", "Nenachádza sa cieľ ani použiteľná proxy"],
        ["Nahrajte export", "Dostupnosť konkrétnej revízie čipu ešte nebola overená"],
    ], [43 * mm, 124 * mm])]
    story += section("Ochrana súkromia a bezpečnostné hranice", "III.06 / dáta")
    story += bullets([
        "Nasadenie neobsahuje aplikačný backend ani analytické API.",
        "Importovaný genotyp sa používa iba počas otvorenej relácie prehliadača.",
        "GitHub Pages prijíma bežné HTTP požiadavky na statické súbory, nie obsah DNA exportu.",
        "Používateľ musí chrániť pôvodný export a nesmie ho zdieľať ako bežnú prílohu bez primeranej ochrany.",
        "Ak sa neskôr pridá telemetria, upload alebo serverové ukladanie, musí sa nanovo posúdiť GDPR a bezpečnostná architektúra.",
    ])
    story.append(PageBreak())
    return story


def qa_section(version: int, records: list[dict]) -> list:
    story = part_cover("IV", "QA, validácia a obmedzenia", "Čo bolo technicky overené, čo zostáva vedeckou hranicou a ako program bezpečne odovzdať.", [("UI KARTY", "7"), ("MAPA", "71"), ("VERZIA", str(version))])
    story += section("Rozsah automatizovaného QA", "IV.01 / regresné scenáre")
    story += [data_table([
        ["Oblasť", "Overované správanie", "Typ dôkazu"],
        ["Import", "23andMe, MyHeritage a DNAEra syntetické exporty", "Browserový smoke test"],
        ["Prehľad", "7 výsledkových kariet a stavové farby", "DOM assertions a screenshoty"],
        ["Mapa", "71 riadkov a rozlíšenie direct/proxy/missing", "DOM assertions"],
        ["Mlieko", "Tri proxy, celé skóre, spoľahlivosť a pásmo", "Regresné scenáre low/typical/high"],
        ["Laktóza", "GG verzus AA, farba, priame určenie a bez imputácie", "Regresné scenáre"],
        ["Celiakia", "50 riadkov, GRS, HLA, proxy a interval", "Direct aj proxy fixture"],
        ["Jazyk", "SK/EN bez straty nahratého stavu", "Prepnutie v browseri"],
        ["Responsive", "Desktop a mobilné rozloženie", "Screenshot QA"],
        ["JavaScript", "Bez nezachytených page errors", "Runtime listener"],
    ], [31 * mm, 85 * mm, 51 * mm], compact=True)]
    story += section("Čo QA potvrdzuje", "IV.02 / technická validácia")
    story += bullets([
        "Parser spracuje podporované syntetické formáty podľa očakávanej schémy.",
        "Výpočtové vetvy dávajú deterministický výsledok pre testovacie genotypy.",
        "Proxy sa nepoužíva ako ďalší nezávislý marker a priamy cieľ má správnu prioritu.",
        "Rozhranie zobrazuje skóre, neistotu a pôvod markerov konzistentne.",
        "Mobilná a desktopová verzia zachovávajú čitateľnosť základných výstupov.",
    ])
    story += section("Čo QA nepotvrdzuje", "IV.03 / klinická hranica")
    story += [banner("NIE JE KLINICKÁ VALIDÁCIA", "Syntetické fixtures a browserové testy nepotvrdzujú citlivosť, špecificitu, AUC, kalibráciu absolútneho rizika ani klinický benefit programu.", DARK), Spacer(1, 5 * mm), data_table([
        ["Otvorená otázka", "Potrebný dôkaz"],
        ["Klinická diskriminácia", "Nezávislá fenotypovaná kohorta pre každý zamýšľaný výstup"],
        ["Absolútne riziko", "Kalibračný model s prevalenciou, interceptom a externou validáciou"],
        ["Prenositeľnosť", "Subgroup analýzy podľa pôvodu, veku, pohlavia a platformy"],
        ["Užitočnosť", "Prospektívny protokol a rozhodovacia analýza"],
        ["Čipové pokrytie", "Empirický audit konkrétnych revízií komerčných čipov"],
    ], [54 * mm, 113 * mm])]
    story.append(PageBreak())
    story += section("Akceptačná matica programu", "IV.04 / stav")
    story += [data_table([
        ["Požiadavka", "Implementácia", "Stav"],
        ["Lokálne spracovanie", "Statická klientská aplikácia bez upload API", "implementované"],
        ["Viacpanelové zhrnutie", "7 kariet a samostatné detailné okná", "implementované"],
        ["Forenzná vysvetliteľnosť", "71-riadková mapa a detail markerov", "implementované"],
        ["Proxy neistota", "r2, podmienené pravdepodobnosti, intervaly", "implementované"],
        ["Celočíselné skóre mlieka", "Oddelené od proxy spoľahlivosti", "implementované"],
        ["Vážený celiakálny model", "GRS42 + 4 research + HLA diplotyp", "implementované"],
        ["Automatický QA workflow", "GitHub Pages deploy bez samostatnej validačnej brány", "čiastočné"],
        ["Klinická validácia", "Nezávislá kohorta a kalibrácia", "otvorené"],
    ], [53 * mm, 80 * mm, 34 * mm], compact=True)]
    story += section("Prevádzkové odporúčania", "IV.05 / ďalšie kroky")
    story += bullets([
        "Pridať samostatný GitHub Actions validačný workflow pred nasadením Pages.",
        "Pri každej zmene panelu aktualizovať verziu, dokumentáciu a regresné fixtures.",
        "Zmraziť vedecký register pred externou klinickou validáciou.",
        "Udržiavať jasné oddelenie výskumného skóre, technickej spoľahlivosti a klinického tvrdenia.",
        "Pred formálnym release potvrdiť licenciu a správcu vedeckého obsahu.",
    ])
    story += [banner("ZÁVER", "AlergenRisk v25 je transparentná statická výskumná aplikácia s lokálnym spracovaním a auditovateľnou markerovou logikou. Klinické použitie zostáva podmienené externou validáciou.", GREEN_DARK), PageBreak()]
    return story


def appendices(version: int, records: list[dict]) -> list:
    proxy_targets = sum(bool(record["proxies"]) for record in records)
    return section("Kontrola úplnosti", "príloha A / dokumentačný audit") + [
        info_cards([("VERZIA", str(version)), ("PANEL-LOKUSY", str(len(records))), ("CIELE S PROXY", str(proxy_targets))]),
        Spacer(1, 6 * mm),
        data_table([
            ["Kontrola", "Výsledok", "Význam"],
            ["Panel-lokus záznamy", len(records), "Musí byť presne 71"],
            ["Unikátne cieľové rsID", len({row['target'] for row in records}), "Opakovanie medzi panelmi je zámerné"],
            ["Panely", len({row['panel'] for row in records}), "Sedem výstupných modulov"],
            ["Ciele s proxy", proxy_targets, "Aspoň jedna zaregistrovaná náhrada"],
            ["Priame-only panely", 2, "Laktóza a histamín/DAO bez imputácie"],
        ], [57 * mm, 28 * mm, 82 * mm]),
        Spacer(1, 6 * mm),
        banner("AUTOMATICKÁ OCHRANA", "Generátor dokumentu číta markerové definície z nasadeného dist/index.html a zastaví sa, ak verzia nie je 25 alebo register nemá 71 panel-lokus záznamov.", DARK),
        *section("Repozitár a nasadenie", "príloha B / dostupnosť"),
        data_table([
            ["Položka", "Hodnota"],
            ["Repozitár", "github.com/umbaja/alergen-risk"],
            ["Aplikácia", "umbaja.github.io/alergen-risk/?lang=sk"],
            ["Zdroj aplikácie", "dist/index.html"],
            ["Deploy workflow", ".github/workflows/pages.yml"],
            ["Dokument", "dist/downloads/AlergenRisk_Programova_a_metodicka_dokumentacia_v25.pdf"],
        ], [48 * mm, 119 * mm]),
        Spacer(1, 7 * mm),
        p("Dokument opisuje stav produkčnej vetvy main v čase vytvorenia. Pri zmene verzie programu je potrebné dokument znovu vygenerovať a vizuálne skontrolovať.", "Small"),
    ]


def build() -> Path:
    html = SOURCE.read_text(encoding="utf-8")
    version, records = build_records(html)
    story = cover(version, records)
    story += contents()
    story += user_section(version)
    story += methodology_section(records)
    story += technical_section(records)
    story += qa_section(version, records)
    story += appendices(version, records)
    OUT.mkdir(parents=True, exist_ok=True)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    document(OUTPUT).build(story)
    shutil.copyfile(OUTPUT, DOWNLOADS / OUTPUT.name)
    print(f"version={version}")
    print(f"panel_locus_records={len(records)}")
    print(f"unique_target_rsids={len({row['target'] for row in records})}")
    print(OUTPUT.relative_to(ROOT))
    return OUTPUT


if __name__ == "__main__":
    build()
