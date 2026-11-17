#!/usr/bin/env python3
"""Flyer DIN lang als Druck-PDF: je Entwurf eine Datei, Seite 1 Vorderseite, Seite 2 Rückseite,
212 × 100 mm (Endformat 210 × 98 mm plus 1 mm Beschnitt rundum).

Quelle ist projekte/avrg-flyer.html – nichts doppelt pflegen. Liegt in entwicklung/, geht nie auf main.

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
    return re.findall(r'<div class="fl">.*?<span class="fl-linien"></span></div>', t[a:b], re.S)


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
        html = f"""<!doctype html><html lang="de"><head><meta charset="utf-8">
<link rel="stylesheet" href="{basis}/assets/fonts/fonts.local.css">
<style>{stil}
@page{{size:212mm 100mm;margin:0}}
html,body{{margin:0;padding:0;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.fl{{width:212mm;height:100mm;aspect-ratio:auto;box-shadow:none;break-after:page;overflow:hidden}}
.fl:last-child{{break-after:auto}}
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
