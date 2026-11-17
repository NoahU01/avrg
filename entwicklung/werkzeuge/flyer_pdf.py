#!/usr/bin/env python3
"""Flyer DIN lang als Druck-PDF: je Entwurf eine Datei, Seite 1 Vorderseite, Seite 2 Rückseite,
212 × 100 mm quer bzw. 100 × 212 mm hochkant (Endformat 210 × 98 mm plus 1 mm Beschnitt rundum).

Quelle ist projekte/avrg-flyer.html – nichts doppelt pflegen. Liegt in entwicklung/, geht nie auf main.

Druckfest (17.11.2026): Chrome legt CSS-Effekte im PDF als Ersatzgrafik ab, die Vorschau und Acrobat
falsch zeigen (Schatten als graues Viereck, Verlaufsmuster verzogen und pixelig). Deshalb hier:
- Kreismuster als echte SVG-Kreise statt repeating-radial-gradient,
- keine Schatten und keine Weichzeichner,
- Fotos für das PDF auf doppelte Breite hochgerechnet (ersetzt kein Original in Druckauflösung).
Prüfen nur mit der Mac-Engine (PDFKit), nie allein mit pdftoppm.

Aufruf:  python3 entwicklung/werkzeuge/flyer_pdf.py 4.2 4.3
Ergebnis: assets/projekte/avrg/flyer/flyer-din-lang-entwurf-<nr>.pdf
"""
import pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
QUELLE = ROOT / "projekte" / "avrg-flyer.html"
BUILD = ROOT / "entwicklung" / "werkzeuge" / "_build"
ZIEL = ROOT / "assets" / "projekte" / "avrg" / "flyer"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def entwurf(t, nr):
    a = t.index(f"<!-- ===================== Entwurf {nr} ")
    b = t.find("<!-- =====================", a + 10)
    b = b if b > 0 else t.index("</main>")
    return re.findall(r'<div class="fl(?: fl--hoch)?">.*?<span class="fl-linien"></span></div>', t[a:b], re.S)


def kreise(cx, cy, schritt, farbe, deckkraft):
    """Konzentrische Ringe wie repeating-radial-gradient: Ring je Schritt, 0,25 mm breit."""
    r_max = max(((cx - x) ** 2 + (cy - y) ** 2) ** .5 for x in (0, 212) for y in (0, 100))
    ringe, k = [], 1
    while k * schritt - .125 < r_max:
        ringe.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{k * schritt - .125:.3f}"/>')
        k += 1
    return (f'<g fill="none" stroke="{farbe}" stroke-opacity="{deckkraft}" stroke-width=".25">'
            + "".join(ringe) + "</g>")


def muster(gespiegelt):
    x = (lambda v: 212 - v) if gespiegelt else (lambda v: v)
    return ('<svg class="w62-muster" viewBox="0 0 212 100" preserveAspectRatio="none" aria-hidden="true" '
            'style="width:100%;height:100%;background:none;opacity:1">'
            + kreise(x(.30 * 212), 50, 1.55, "#6a2d6e", .09)
            + kreise(x(.96 * 212), 105, 2.15, "#ee0000", .06) + "</svg>")


def foto_gross(pfad):
    """Foto für das PDF auf doppelte Breite hochrechnen (glättet, ersetzt kein Druckoriginal)."""
    ziel = BUILD / ("gross-" + pathlib.Path(pfad).name)
    if not ziel.exists():
        quelle = ROOT / pfad.lstrip("/")
        breite = int(subprocess.run(["sips", "-g", "pixelWidth", str(quelle)], capture_output=True,
                                    text=True).stdout.split()[-1])
        subprocess.run(["sips", "--resampleWidth", str(breite * 2), str(quelle), "--out", str(ziel)],
                       check=True, stdout=subprocess.DEVNULL)
    return "file://" + str(ziel)


def main(nummern):
    t = QUELLE.read_text(encoding="utf-8")
    symbole = "".join(re.findall(r'(<svg width="0" height="0".*?</svg>)', t, re.S))
    stil = re.search(r"<style>(.*?)</style>", t, re.S).group(1)
    stil = stil.replace("@import url('/assets/fonts/fonts.css');", "")
    basis = "file://" + str(ROOT)
    BUILD.mkdir(exist_ok=True)
    for nr in nummern:
        seiten = entwurf(t, nr)
        assert len(seiten) == 2, f"Entwurf {nr}: {len(seiten)} Seiten gefunden"
        seiten = [s.replace('<span class="w62-muster" aria-hidden="true"></span>', muster(i == 1))
                  for i, s in enumerate(seiten)]
        seiten = [re.sub(r'(<img class="w63-foto" src=")([^"]+)"', lambda m: m.group(1) + foto_gross(m.group(2)) + '"', s)
                  for s in seiten]
        breite, hoehe = (100, 212) if "fl--hoch" in seiten[0] else (212, 100)
        html = f"""<!doctype html><html lang="de"><head><meta charset="utf-8">
<link rel="stylesheet" href="{basis}/assets/fonts/fonts.local.css">
<style>{stil}
@page{{size:{breite}mm {hoehe}mm;margin:0}}
html,body{{margin:0;padding:0;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.fl{{width:{breite}mm;height:{hoehe}mm;aspect-ratio:auto;box-shadow:none;break-after:page;overflow:hidden}}
.fl:last-child{{break-after:auto}}
.fl *{{box-shadow:none!important;filter:none!important;text-shadow:none!important}}
.fl .w62r .w62-muster{{transform:none}}
</style></head><body>{symbole}{''.join(seiten)}</body></html>"""
        html = re.sub(r'(src|href)="/', rf'\1="{basis}/', html)
        src = BUILD / f"flyer-{nr}.html"
        src.write_text(html, encoding="utf-8")
        pdf = ZIEL / f"flyer-din-lang-entwurf-{nr.replace('.', '-')}.pdf"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--allow-file-access-from-files", f"--print-to-pdf={pdf}",
                        "--virtual-time-budget=8000", "file://" + str(src)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(pdf.relative_to(ROOT))


if __name__ == "__main__":
    main(sys.argv[1:] or ["4.2", "4.3"])
