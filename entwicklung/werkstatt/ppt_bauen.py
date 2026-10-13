#!/usr/bin/env python3
"""Baut den PowerPoint-Master der SV Owen als .pptx.

Aufruf:  python3 ppt_bauen.py <logo.png> <logo-weiss.png> <beispielfoto.jpg> <ziel.pptx>

- Folienmaster mit acht Layouts (Deckblatt, Inhalt, Agenda, Vergleich, Kontakt 1/2/3, Kapitel)
  und je einer Beispielfolie.
- Farben im Design (Designfarben + benutzerdefinierte Farben), Schriften Sparkasse Head und
  Sparkasse Lt im Design und eingebettet (EOT wie PowerPoint, unkomprimiert), Sprache überall de-DE.
- Die Schriften liegen lizenziert nur lokal (~/Library/Fonts) – die fertige Datei gehört NIE ins
  öffentliche Repo, sondern in den Nextcloud-Projektordner.
Maße: Folie 1600 × 900 px = 33,867 × 19,05 cm, 1 px = 7620 EMU (wie die Vorschau in folien.html).
"""
import os, struct, sys, zipfile, datetime
from fontTools.ttLib import TTFont

LOGO, LOGO_W, FOTO, ZIEL = sys.argv[1:5]
FONTS = os.path.expanduser('~/Library/Fonts')

def E(px): return int(round(px * 7620))
W, H = E(1600), E(900)
RAND, OBEN, UNTEN = 76, 66, 42
LANG = 'de-DE'
RECHTECK = '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
OHNE_MASTER = ' showMasterSp="0"'
DIRTY = ' dirty="0"'
NS = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"')
XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
R_LAYOUT = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout'
R_MASTER = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster'
R_IMAGE = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'
R_THEME = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme'

# ---------------------------------------------------------------- Farben
PRIMAER = [('Weiß', 'FFFFFF'), ('Sparkassen-Rot', 'EE0000'), ('Sparkassen-Dunkelgrau 1', '666666'),
           ('Sparkassen-Grau 3', 'D9D9D9'), ('Schwarz', '000000')]
GRAU = [('Sparkassen-Hellgrau', 'F0F0F0'), ('Sparkassen-Grau 1', 'E9E9E9'), ('Sparkassen-Grau 2', 'E3E3E3'),
        ('Sparkassen-Grau 4', 'CCCCCC'), ('Sparkassen-Grau 5', 'BBBBBB'), ('Sparkassen-Grau 6', '999999'),
        ('Sparkassen-Dunkelgrau 2', '444444')]
AKZENT = [('Sparkassen-Gelb', 'FFC900'), ('Sparkassen-Orange', 'FF8F00'), ('Sparkassen-Violett', '9B348E'),
          ('Sparkassen-Dunkelblau', '2C57D2'), ('Sparkassen-Hellblau', '00ACD3'), ('Sparkassen-Dunkelgrün', '009864'),
          ('Sparkassen-Hellgrün', '8CD000'), ('Sparkassen-Gelb hell', 'FFDF66'), ('Sparkassen-Orange hell', 'FFBC66'),
          ('Sparkassen-Violett hell', 'C385BB'), ('Sparkassen-Dunkelblau hell', '809AE4'),
          ('Sparkassen-Hellblau hell', '66CDE5'), ('Sparkassen-Dunkelgrün hell', '66C1A2'),
          ('Sparkassen-Hellgrün hell', 'BAE366')]

def theme():
    cust = ''.join(f'<a:custClr name="{n}"><a:srgbClr val="{h}"/></a:custClr>' for n, h in PRIMAER + GRAU + AKZENT)
    fill = ('<a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
            '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>')
    ln = ''.join(f'<a:ln w="{w}"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>' for w in (6350, 12700, 19050))
    eff = '<a:effectStyleLst>' + '<a:effectStyle><a:effectLst/></a:effectStyle>' * 3 + '</a:effectStyleLst>'
    return (XML + f'<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="SV Owen">'
            '<a:themeElements><a:clrScheme name="SV Owen">'
            '<a:dk1><a:srgbClr val="000000"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>'
            '<a:dk2><a:srgbClr val="666666"/></a:dk2><a:lt2><a:srgbClr val="F0F0F0"/></a:lt2>'
            '<a:accent1><a:srgbClr val="EE0000"/></a:accent1><a:accent2><a:srgbClr val="666666"/></a:accent2>'
            '<a:accent3><a:srgbClr val="D9D9D9"/></a:accent3><a:accent4><a:srgbClr val="2C57D2"/></a:accent4>'
            '<a:accent5><a:srgbClr val="FFC900"/></a:accent5><a:accent6><a:srgbClr val="009864"/></a:accent6>'
            '<a:hlink><a:srgbClr val="EE0000"/></a:hlink><a:folHlink><a:srgbClr val="666666"/></a:folHlink></a:clrScheme>'
            '<a:fontScheme name="SV Owen"><a:majorFont><a:latin typeface="Sparkasse Head"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont>'
            '<a:minorFont><a:latin typeface="Sparkasse Lt"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme>'
            f'<a:fmtScheme name="SV Owen">{fill}<a:lnStyleLst>{ln}</a:lnStyleLst>{eff}'
            '<a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
            '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme></a:themeElements>'
            f'<a:objectDefaults/><a:extraClrSchemeLst/><a:custClrLst>{cust}</a:custClrLst></a:theme>')

# ---------------------------------------------------------------- Bausteine
def rpr(sz=None, farbe=None, font=None, alpha=None, tag='a:defRPr', extra=''):
    a = f' lang="{LANG}"' + (f' sz="{sz}"' if sz else '') + ' b="0"' + extra
    inner = ''
    if farbe:
        inner += f'<a:solidFill><a:srgbClr val="{farbe}">' + (f'<a:alpha val="{alpha}"/>' if alpha else '') + '</a:srgbClr></a:solidFill>'
    if font:
        inner += f'<a:latin typeface="{font}"/>'
    return f'<{tag}{a}>{inner}</{tag}>'

def lst(sz, farbe='000000', font='+mn-lt', algn='l', bu='<a:buNone/>', mar=0, ind=0, spc_bef=0, ln=100):
    return (f'<a:lstStyle><a:lvl1pPr marL="{mar}" indent="{ind}" algn="{algn}"><a:lnSpc><a:spcPct val="{ln * 1000}"/></a:lnSpc>'
            f'<a:spcBef><a:spcPts val="{spc_bef}"/></a:spcBef>{bu}{rpr(sz, farbe, font)}</a:lvl1pPr></a:lstStyle>')

def body_pr(anchor='t', autofit=''):
    return f'<a:bodyPr lIns="0" tIns="0" rIns="0" bIns="0" anchor="{anchor}" wrap="square">{autofit}</a:bodyPr>'

class Ids:
    def __init__(self): self.n = 1
    def __call__(self): self.n += 1; return self.n

def ph(ids, name, typ, idx, x, y, w, h, lststyle='', anchor='t', text='', geom='', autofit='<a:normAutofit/>'):
    t = f' type="{typ}"' if typ else ''
    i = f' idx="{idx}"' if idx is not None else ''
    para = text or f'<a:p><a:endParaRPr lang="{LANG}"/></a:p>'
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{ids()}" name="{name}"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
            f'<p:nvPr><p:ph{t}{i}/></p:nvPr></p:nvSpPr><p:spPr><a:xfrm><a:off x="{E(x)}" y="{E(y)}"/><a:ext cx="{E(w)}" cy="{E(h)}"/></a:xfrm>'
            f'{geom or RECHTECK}</p:spPr>'
            f'<p:txBody>{body_pr(anchor, autofit)}{lststyle}{para}</p:txBody></p:sp>')

def prompt(t, sz=None):
    return f'<a:p><a:r>{rpr(sz, tag="a:rPr")}<a:t>{t}</a:t></a:r></a:p>'

def pic(ids, rid, name, x, y, w, h):
    return (f'<p:pic><p:nvPicPr><p:cNvPr id="{ids()}" name="{name}" descr="SV Owen"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr userDrawn="1"/></p:nvPicPr>'
            f'<p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
            f'<p:spPr><a:xfrm><a:off x="{E(x)}" y="{E(y)}"/><a:ext cx="{E(w)}" cy="{E(h)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>')

def linie(ids, x, y, w, farbe, dicke_px):
    return (f'<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="{ids()}" name="Linie"/><p:cNvCxnSpPr/><p:nvPr userDrawn="1"/></p:nvCxnSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{E(x)}" y="{E(y)}"/><a:ext cx="{E(w)}" cy="0"/></a:xfrm><a:prstGeom prst="line"><a:avLst/></a:prstGeom>'
            f'<a:ln w="{E(dicke_px)}"><a:solidFill><a:srgbClr val="{farbe}"/></a:solidFill></a:ln></p:spPr></p:cxnSp>')

LOGO_RATIO = 1071.64 / 267.7
def logo_fuss(ids, rid='rIdLogo'):
    h = 30; return pic(ids, rid, 'Logo', RAND, 900 - UNTEN - h, h * LOGO_RATIO, h)

def fuss_ph(ids):
    y, h = 900 - UNTEN - 32, 32
    ftr = ph(ids, 'Fußzeile', 'ftr', 11, 400, y, 800, h, lst(1000, '666666', algn='ctr'), anchor='b', autofit='')
    nr = ph(ids, 'Foliennummer', 'sldNum', 12, 1600 - RAND - 200, y, 200, h, lst(1000, '666666', '+mj-lt', algn='r'), anchor='b',
            text=f'<a:p><a:fld id="{{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}}" type="slidenum">{rpr(tag="a:rPr")}<a:t>‹#›</a:t></a:fld></a:p>', autofit='')
    return ftr + nr

def kopf_ph(ids, subline=True):
    t = ph(ids, 'Titel', 'title', None, RAND, 14, 1600 - 2 * RAND, 108, anchor='b', text=prompt('Titel durch Klicken hinzufügen'))
    s = ph(ids, 'Subline', 'body', 13, RAND, 128, 1600 - 2 * RAND, 70, lst(1600, '666666'), text=prompt('Optionale Subline')) if subline else ''
    return t + s

# ---------------------------------------------------------------- Master
def master():
    ids = Ids()
    sp = (ph(ids, 'Titel', 'title', None, RAND, 14, 1600 - 2 * RAND, 108, anchor='b', text=prompt('Titel durch Klicken hinzufügen'))
          + ph(ids, 'Text', 'body', 1, RAND, 230, 1600 - 2 * RAND, 550, text=''.join(
              f'<a:p><a:pPr lvl="{l}"/><a:r>{rpr(tag="a:rPr")}<a:t>{t}</a:t></a:r></a:p>' for l, t in
              [(0, 'Textebene 1'), (1, 'Textebene 2'), (2, 'Textebene 3')]))
          + fuss_ph(ids) + logo_fuss(ids))
    lv = lambda n, sz, bu, mar, ind: (f'<a:lvl{n}pPr marL="{mar}" indent="{ind}" algn="l"><a:lnSpc><a:spcPct val="110000"/></a:lnSpc>'
                                      f'<a:spcBef><a:spcPts val="600"/></a:spcBef>{bu}{rpr(sz, "000000", "+mn-lt")}</a:lvl{n}pPr>')
    strich = '<a:buFont typeface="Sparkasse Lt"/><a:buChar char="–"/>'
    body = (lv(1, 1800, '<a:buNone/>', 0, 0) + lv(2, 1800, strich, E(24), -E(24)) + lv(3, 1600, strich, E(48), -E(24))
            + lv(4, 1400, strich, E(72), -E(24)) + lv(5, 1400, strich, E(96), -E(24)))
    other = '<a:lvl1pPr>' + rpr(1800, '000000', '+mn-lt') + '</a:lvl1pPr>'
    title = f'<a:lvl1pPr algn="l"><a:lnSpc><a:spcPct val="100000"/></a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef><a:buNone/>{rpr(2800, "000000", "+mj-lt")}</a:lvl1pPr>'
    ids_layouts = ''.join(f'<p:sldLayoutId id="{2147483649 + i}" r:id="rId{i + 1}"/>' for i in range(len(LAYOUTS)))
    return (XML + f'<p:sldMaster {NS}><p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>'
            f'<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>{sp}</p:spTree></p:cSld>'
            '<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>'
            f'<p:sldLayoutIdLst>{ids_layouts}</p:sldLayoutIdLst><p:hf hdr="0" dt="0"/>'
            f'<p:txStyles><p:titleStyle>{title}</p:titleStyle><p:bodyStyle>{body}</p:bodyStyle><p:otherStyle>{other}</p:otherStyle></p:txStyles></p:sldMaster>')

# ---------------------------------------------------------------- Layouts
def L_deckblatt(ids):
    t = ph(ids, 'Titel', 'ctrTitle', None, RAND, 40, 1600 - 2 * RAND, 190, lst(4400, '000000', '+mj-lt'), anchor='b',
           text=prompt('Titel der Präsentation'))
    s = ph(ids, 'Subline', 'subTitle', 1, RAND, 251, 1600 - 2 * RAND, 100, lst(2200, '666666'), text=prompt('Optionale Subline'))
    m = ph(ids, 'Anlass · Ort · Datum', 'body', 13, 1600 - RAND - 700, 900 - UNTEN - 36, 700, 34, lst(1000, '666666', algn='r'), anchor='b',
           text=prompt('Anlass · Ort · Datum'), autofit='')
    h = 38
    return t + s + m + pic(ids, 'rIdLogo', 'Logo', RAND, 900 - UNTEN - h, h * LOGO_RATIO, h), False, None

def L_inhalt(ids):
    b = ph(ids, 'Inhalt', 'body', 1, RAND, 230, 1600 - 2 * RAND, 550, text=prompt('Text durch Klicken hinzufügen'))
    return kopf_ph(ids) + b + fuss_ph(ids), True, None

def L_agenda(ids):
    bu = '<a:buClr><a:srgbClr val="666666"/></a:buClr><a:buSzPct val="100000"/><a:buFont typeface="Sparkasse Head"/><a:buAutoNum type="arabicPlain"/>'
    b = ph(ids, 'Agenda', 'body', 1, RAND, 230, 1600 - 2 * RAND, 550,
           lst(2400, '000000', mar=E(90), ind=-E(90), bu=bu, spc_bef=1800, ln=110),
           text=''.join(prompt(x) for x in ['Erster Punkt', 'Zweiter Punkt', 'Dritter Punkt']))
    return kopf_ph(ids, subline=False) + b + fuss_ph(ids), True, None

def L_vergleich(ids):
    sp_w = (1600 - 2 * RAND - 96) / 2; x2 = RAND + sp_w + 96
    k1 = ph(ids, 'Überschrift links', 'body', 14, RAND, 250, sp_w, 60, lst(2400, '666666', '+mj-lt'), anchor='b', text=prompt('Heute'), autofit='')
    k2 = ph(ids, 'Überschrift rechts', 'body', 15, x2, 250, sp_w, 60, lst(2400, '000000', '+mj-lt'), anchor='b', text=prompt('Morgen'), autofit='')
    l1 = linie(ids, RAND, 324, sp_w, 'D9D9D9', 3); l2 = linie(ids, x2, 324, sp_w, '000000', 3)
    st = lst(1800, '000000', spc_bef=1200, ln=110)
    b1 = ph(ids, 'Text links', 'body', 16, RAND, 346, sp_w, 434, st, text=prompt('Punkte der linken Seite'))
    b2 = ph(ids, 'Text rechts', 'body', 17, x2, 346, sp_w, 434, st, text=prompt('Punkte der rechten Seite'))
    return kopf_ph(ids) + k1 + k2 + l1 + l2 + b1 + b2 + fuss_ph(ids), True, None

KREIS = '<a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>'
def person(ids, n, x, y, bild, gross, txt_x=None, txt_y=None, txt_w=420, sz=(3400, 1800, 1800)):
    i = 20 + n * 4
    out = ph(ids, f'Foto {n + 1}', 'pic', i, x, y, bild, bild, geom=KREIS, text=prompt('Foto einfügen'), autofit='')
    tx = txt_x if txt_x is not None else x; ty = txt_y if txt_y is not None else y + bild + 28
    out += ph(ids, f'Name {n + 1}', 'body', i + 1, tx, ty, txt_w, sz[0] / 100 * 1.667 * 1.3, lst(sz[0], '000000', '+mj-lt'), text=prompt('Vorname Nachname'), autofit='')
    ty2 = ty + sz[0] / 100 * 1.667 * 1.3 + 6
    out += ph(ids, f'Einheit {n + 1}', 'body', i + 2, tx, ty2, txt_w, sz[1] / 100 * 1.667 * 1.4, lst(sz[1], '666666'), text=prompt('Funktion · Einheit'), autofit='')
    ty3 = ty2 + sz[1] / 100 * 1.667 * 1.4 + 22
    out += ph(ids, f'Kontakt {n + 1}', 'body', i + 3, tx, ty3, txt_w, 120, lst(sz[2], '000000', spc_bef=400, ln=110),
              text=prompt('Telefon') + prompt('E-Mail'), autofit='')
    return out

def L_kontakt1(ids):
    return kopf_ph(ids, subline=False) + person(ids, 0, RAND, 300, 300, True, txt_x=RAND + 372, txt_y=322, txt_w=900) + fuss_ph(ids), True, None

def L_kontakt2(ids):
    sp_w = (1600 - 2 * RAND - 96) / 2
    out = ''.join(person(ids, n, RAND + n * (sp_w + 96), 300, 220, False, txt_x=RAND + n * (sp_w + 96) + 256, txt_y=316,
                         txt_w=sp_w - 256, sz=(2800, 1600, 1600)) for n in range(2))
    return kopf_ph(ids, subline=False) + out + fuss_ph(ids), True, None

def L_kontakt3(ids):
    sp_w = (1600 - 2 * RAND - 2 * 64) / 3
    out = ''.join(person(ids, n, RAND + n * (sp_w + 64), 240, 190, False, txt_w=sp_w, sz=(2400, 1400, 1400)) for n in range(3))
    return kopf_ph(ids, subline=False) + out + fuss_ph(ids), True, None

def L_kapitel(ids):
    k = ph(ids, 'Kapitel', 'body', 13, RAND, 360, 1600 - 2 * RAND, 44, lst(1400, 'FFFFFF', '+mj-lt').replace(' b="0">', ' b="0" cap="all" spc="200">').replace('<a:srgbClr val="FFFFFF"></a:srgbClr>', '<a:srgbClr val="FFFFFF"><a:alpha val="75000"/></a:srgbClr>'),
           anchor='b', text=prompt('Kapitel 2'), autofit='')
    t = ph(ids, 'Titel', 'title', None, RAND, 420, 1600 - 2 * RAND, 200, lst(4400, 'FFFFFF', '+mj-lt'), text=prompt('Titel des Kapitels'))
    h = 30
    return k + t + pic(ids, 'rIdLogoW', 'Logo weiß', RAND, 900 - UNTEN - h, h * LOGO_RATIO, h), False, 'EE0000'

LAYOUTS = [('Deckblatt', L_deckblatt), ('Inhalt', L_inhalt), ('Agenda', L_agenda), ('Zwei Seiten im Vergleich', L_vergleich),
           ('Kontakt · 1 Person', L_kontakt1), ('Kontakt · 2 Personen', L_kontakt2), ('Kontakt · 3 Personen', L_kontakt3),
           ('Kapiteltrenner', L_kapitel)]

def layout_xml(name, fn):
    ids = Ids(); sp, master_sp, bg = fn(ids)
    bgx = f'<p:bg><p:bgPr><a:solidFill><a:srgbClr val="{bg}"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>' if bg else ''
    return (XML + f'<p:sldLayout {NS} preserve="1" userDrawn="1"{"" if master_sp else OHNE_MASTER}><p:cSld name="{name}">{bgx}'
            f'<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>{sp}</p:spTree></p:cSld>'
            '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr><p:hf hdr="0" dt="0"/></p:sldLayout>')

# ---------------------------------------------------------------- Beispielfolien
def s_ph(ids, typ, idx, paras, name='Platzhalter'):
    t = f' type="{typ}"' if typ else ''
    i = f' idx="{idx}"' if idx is not None else ''
    ps = ''.join(f'<a:p><a:r>{rpr(tag="a:rPr", extra=DIRTY)}<a:t>{x}</a:t></a:r></a:p>' for x in paras)
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{ids()}" name="{name}"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph{t}{i}/></p:nvPr></p:nvSpPr>'
            f'<p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>{ps}</p:txBody></p:sp>')

def s_nr(ids):
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{ids()}" name="Foliennummer"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="sldNum" idx="12"/></p:nvPr></p:nvSpPr>'
            f'<p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:fld id="{{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}}" type="slidenum">{rpr(tag="a:rPr")}<a:t>‹#›</a:t></a:fld></a:p></p:txBody></p:sp>')

def s_foto(ids, idx, rid):
    return (f'<p:pic><p:nvPicPr><p:cNvPr id="{ids()}" name="Foto"/><p:cNvPicPr><a:picLocks noGrp="1" noChangeAspect="1"/></p:cNvPicPr><p:nvPr><p:ph type="pic" idx="{idx}"/></p:nvPr></p:nvPicPr>'
            f'<p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr/></p:pic>')

FUSS = 'Die neue Altersvorsorge 2027'
def folien():
    F = []
    def neu(layout, inhalt, fuss=True, foto=False):
        ids = Ids(); x = inhalt(ids)
        if fuss: x += s_ph(ids, 'ftr', 11, [FUSS], 'Fußzeile') + s_nr(ids)
        F.append((layout, x, foto))
    neu(0, lambda i: s_ph(i, 'ctrTitle', None, ['Die neue Altersvorsorge 2027']) + s_ph(i, 'subTitle', 1, ['Was die Reform für Ihre Kunden bedeutet'])
        + s_ph(i, 'body', 13, ['Anlass · Ort · Datum']), fuss=False)
    neu(2, lambda i: s_ph(i, 'title', None, ['Agenda']) + s_ph(i, 'body', 1, ['Ausgangslage', 'Was sich 2027 ändert', 'Was das für Sie bedeutet',
                                                                              'Beispiele aus der Praxis', 'Ihre Fragen', 'Nächste Schritte']))
    neu(7, lambda i: s_ph(i, 'body', 13, ['Kapitel 1']) + s_ph(i, 'title', None, ['Ausgangslage']), fuss=False)
    neu(1, lambda i: s_ph(i, 'title', None, ['Headline der Inhaltsseite']) + s_ph(i, 'body', 13, ['Optionale Subline für den Kontext'])
        + s_ph(i, 'body', 1, ['Fließtext in Sparkasse Light, 18 pt. Die Sprache aller Platzhalter ist Deutsch.',
                              'Mit der Tabulatortaste wird aus einem Absatz ein Aufzählungspunkt mit Strich.']))
    neu(3, lambda i: s_ph(i, 'title', None, ['Zwei Seiten im Vergleich']) + s_ph(i, 'body', 13, ['Optionale Subline für den Kontext'])
        + s_ph(i, 'body', 14, ['Heute']) + s_ph(i, 'body', 15, ['Ab 2027'])
        + s_ph(i, 'body', 16, ['Erster Punkt der linken Seite', 'Zweiter Punkt in einer Zeile', 'Dritter Punkt, kurz gehalten'])
        + s_ph(i, 'body', 17, ['Erster Punkt der rechten Seite', 'Zweiter Punkt in einer Zeile', 'Dritter Punkt, kurz gehalten']))
    def leute(i, n, kurz=False):
        x = ''
        for k in range(n):
            b = 20 + k * 4
            name, rolle = (('Sandra Hild', 'SV Gebietsdirektion Owen') if k == 0 else ('Vorname Nachname', 'Funktion · Einheit'))
            tel = '07021 9808021' if kurz else 'Telefon 07021 9808021'
            mail = 'sandra.hild@sv-owen.de' if k == 0 else 'name@sv-owen.de'
            x += s_foto(i, b, 'rIdFoto') + s_ph(i, 'body', b + 1, [name]) + s_ph(i, 'body', b + 2, [rolle]) + s_ph(i, 'body', b + 3, [tel, mail])
        return x
    neu(4, lambda i: s_ph(i, 'title', None, ['Dein direkter Draht zu uns']) + leute(i, 1), foto=True)
    neu(5, lambda i: s_ph(i, 'title', None, ['Dein direkter Draht zu uns']) + leute(i, 2), foto=True)
    neu(6, lambda i: s_ph(i, 'title', None, ['Dein direkter Draht zu uns']) + leute(i, 3, kurz=True), foto=True)
    return F

def slide_xml(inhalt):
    return (XML + f'<p:sld {NS}><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>'
            f'{inhalt}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>')

# ---------------------------------------------------------------- Schriften als EOT (wie PowerPoint)
def eot(pfad):
    f = TTFont(pfad); data = open(pfad, 'rb').read(); o = f['OS/2']; n = f['name']
    def s(x):
        b = (x or '').encode('utf-16-le'); return struct.pack('<HH', 0, len(b)) + b
    names = s(n.getDebugName(1)) + s(n.getDebugName(2)) + s(n.getDebugName(5)) + s(n.getDebugName(4)) + struct.pack('<HH', 0, 0)
    panose = bytes([o.panose.bFamilyType, o.panose.bSerifStyle, o.panose.bWeight, o.panose.bProportion, o.panose.bContrast,
                    o.panose.bStrokeVariation, o.panose.bArmStyle, o.panose.bLetterForm, o.panose.bMidline, o.panose.bXHeight])
    kopf_rest = (struct.pack('<II', 0x00020001, 0) + panose + struct.pack('<BBIHH', 1, 1 if o.fsSelection & 1 else 0, o.usWeightClass, o.fsType, 0x504C)
                 + struct.pack('<IIIIII', o.ulUnicodeRange1, o.ulUnicodeRange2, o.ulUnicodeRange3, o.ulUnicodeRange4,
                               o.ulCodePageRange1, o.ulCodePageRange2)
                 + struct.pack('<I', f['head'].checkSumAdjustment) + b'\0' * 16 + names)
    gesamt = 8 + len(kopf_rest) + len(data)
    return struct.pack('<II', gesamt, len(data)) + kopf_rest + data, panose.hex().upper()

SCHRIFTEN = [('Sparkasse Head', [('regular', 'SparkasseHead_Rg.ttf'), ('bold', 'SparkasseHead_Rg.ttf')]),
             ('Sparkasse Lt', [('regular', 'SparLt.ttf'), ('italic', 'SparLtIt.ttf')])]

# ---------------------------------------------------------------- Paket schreiben
def bauen():
    z = zipfile.ZipFile(ZIEL, 'w', zipfile.ZIP_DEFLATED)
    F = folien()
    ct = ['<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
          '<Default Extension="xml" ContentType="application/xml"/>', '<Default Extension="png" ContentType="image/png"/>',
          '<Default Extension="jpg" ContentType="image/jpeg"/>', '<Default Extension="fntdata" ContentType="application/x-fontdata"/>',
          '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
          '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
          '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
          '<Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>',
          '<Override PartName="/ppt/viewProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"/>',
          '<Override PartName="/ppt/tableStyles.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"/>',
          '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
          '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>']
    z.writestr('ppt/media/logo.png', open(LOGO, 'rb').read())
    z.writestr('ppt/media/logo-weiss.png', open(LOGO_W, 'rb').read())
    z.writestr('ppt/media/foto.jpg', open(FOTO, 'rb').read())
    # Master
    z.writestr('ppt/slideMasters/slideMaster1.xml', master())
    mr = ''.join(f'<Relationship Id="rId{i + 1}" Type="{R_LAYOUT}" Target="../slideLayouts/slideLayout{i + 1}.xml"/>' for i in range(len(LAYOUTS)))
    mr += f'<Relationship Id="rIdTheme" Type="{R_THEME}" Target="../theme/theme1.xml"/><Relationship Id="rIdLogo" Type="{R_IMAGE}" Target="../media/logo.png"/>'
    z.writestr('ppt/slideMasters/_rels/slideMaster1.xml.rels', XML + f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{mr}</Relationships>')
    z.writestr('ppt/theme/theme1.xml', theme())
    for i, (name, fn) in enumerate(LAYOUTS, 1):
        z.writestr(f'ppt/slideLayouts/slideLayout{i}.xml', layout_xml(name, fn))
        z.writestr(f'ppt/slideLayouts/_rels/slideLayout{i}.xml.rels', XML + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   f'<Relationship Id="rId1" Type="{R_MASTER}" Target="../slideMasters/slideMaster1.xml"/>'
                   f'<Relationship Id="rIdLogo" Type="{R_IMAGE}" Target="../media/logo.png"/>'
                   f'<Relationship Id="rIdLogoW" Type="{R_IMAGE}" Target="../media/logo-weiss.png"/></Relationships>')
        ct.append(f'<Override PartName="/ppt/slideLayouts/slideLayout{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>')
    for i, (lay, inhalt, foto) in enumerate(F, 1):
        z.writestr(f'ppt/slides/slide{i}.xml', slide_xml(inhalt))
        fr = f'<Relationship Id="rIdFoto" Type="{R_IMAGE}" Target="../media/foto.jpg"/>' if foto else ''
        z.writestr(f'ppt/slides/_rels/slide{i}.xml.rels', XML + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   f'<Relationship Id="rId1" Type="{R_LAYOUT}" Target="../slideLayouts/slideLayout{lay + 1}.xml"/>{fr}</Relationships>')
        ct.append(f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>')
    # Schriften
    pr = [f'<Relationship Id="rId1" Type="{R_MASTER}" Target="slideMasters/slideMaster1.xml"/>',
          f'<Relationship Id="rId2" Type="{R_THEME}" Target="theme/theme1.xml"/>',
          '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps" Target="presProps.xml"/>',
          '<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps" Target="viewProps.xml"/>',
          '<Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/tableStyles" Target="tableStyles.xml"/>']
    fontlst = ''; nf = 0
    for fam, stile in SCHRIFTEN:
        teile = ''; pan = ''
        for stil, datei in stile:
            nf += 1; daten, pan = eot(os.path.join(FONTS, datei))
            z.writestr(f'ppt/fonts/font{nf}.fntdata', daten)
            pr.append(f'<Relationship Id="rIdF{nf}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/font" Target="fonts/font{nf}.fntdata"/>')
            teile += f'<p:{stil} r:id="rIdF{nf}"/>'
        fontlst += f'<p:embeddedFont><p:font typeface="{fam}" panose="{pan}" pitchFamily="34" charset="0"/>{teile}</p:embeddedFont>'
    sld = ''
    for i in range(1, len(F) + 1):
        pr.append(f'<Relationship Id="rIdS{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>')
        sld += f'<p:sldId id="{255 + i}" r:id="rIdS{i}"/>'
    dts = ''.join(f'<a:lvl{n}pPr marL="0" algn="l">' + rpr(1800, '000000', '+mn-lt') + f'</a:lvl{n}pPr>' for n in range(1, 10))
    z.writestr('ppt/presentation.xml', XML + f'<p:presentation {NS} saveSubsetFonts="0" embedTrueTypeFonts="1">'
               f'<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:sldIdLst>{sld}</p:sldIdLst>'
               f'<p:sldSz cx="{W}" cy="{H}"/><p:notesSz cx="6858000" cy="9144000"/><p:embeddedFontLst>{fontlst}</p:embeddedFontLst>'
               f'<p:defaultTextStyle><a:defPPr>{rpr()}</a:defPPr>{dts}</p:defaultTextStyle></p:presentation>')
    z.writestr('ppt/_rels/presentation.xml.rels', XML + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + ''.join(pr) + '</Relationships>')
    z.writestr('ppt/presProps.xml', XML + f'<p:presentationPr {NS}/>')
    z.writestr('ppt/viewProps.xml', XML + f'<p:viewPr {NS}><p:normalViewPr><p:restoredLeft sz="15620"/><p:restoredTop sz="94660"/></p:normalViewPr><p:gridSpacing cx="72008" cy="72008"/></p:viewPr>')
    z.writestr('ppt/tableStyles.xml', XML + '<a:tblStyleLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" def="{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"/>')
    jetzt = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    z.writestr('docProps/core.xml', XML + '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
               'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
               f'<dc:title>SV Owen – PowerPoint-Master</dc:title><dc:language>{LANG}</dc:language><cp:lastModifiedBy>empiria</cp:lastModifiedBy>'
               f'<dcterms:created xsi:type="dcterms:W3CDTF">{jetzt}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">{jetzt}</dcterms:modified></cp:coreProperties>')
    z.writestr('docProps/app.xml', XML + '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>Microsoft Office PowerPoint</Application></Properties>')
    z.writestr('_rels/.rels', XML + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
               '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>'
               '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
               '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>')
    z.writestr('[Content_Types].xml', XML + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">' + ''.join(ct) + '</Types>')
    z.close()
    print('geschrieben:', ZIEL, len(F), 'Folien,', len(LAYOUTS), 'Layouts,', nf, 'Schriftschnitte')

if __name__ == '__main__':
    bauen()
