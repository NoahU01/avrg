# Handoff

Dieses Repository ist die Arbeitsgrundlage, damit Dani das Projekt fuer die AVRG bearbeiten kann.

## Branches und Entwicklungsmenü

- Gearbeitet wird auf `daniel`. `main` ist die Live-Fassung unter https://empiria-avrg.vercel.app/ (Vercel-Projekt „avrg“).
- **„/ Entwicklung /“ geht NIE auf `main`** – auch nicht teilweise, auch nicht auf Zuruf. Gemeint ist bei „auf main“ immer nur der Live-Teil.
  - Entwicklungsseiten liegen in `entwicklung/` (Menü: `entwicklung/menu.js` + `menu.css`; neue Unterseiten nur dort in `MENU` eintragen).
  - Seiten binden das Menü über einen Block `<!-- ENTWICKLUNG:START -->` … `<!-- ENTWICKLUNG:END -->` vor `</body>` ein.
- Übertrag nach `main`: nie `daniel` blind auf `main` schieben. Nur Live-Dateien übernehmen, ENTWICKLUNG-Blöcke entfernen, `entwicklung/` weglassen.
- Schutz, doppelt:
  1. Lokal (Daniels Mac): `core.hooksPath` → `~/Projekte/.git-hooks` stoppt Commit und Push auf `main` mit Entwicklungsinhalten. Nie mit `--no-verify` umgehen.
  2. Vercel: `vercel.json` führt `werkzeuge/main-schutz.sh` als Build aus; enthält ein main-Stand Entwicklungsinhalte, bricht der Build ab und die Live-Seite bleibt unverändert.
