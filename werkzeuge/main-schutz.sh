#!/bin/sh
# Schutz bei Vercel: „/ Entwicklung /“ geht NIE live.
# Läuft als Build-Befehl (vercel.json). Ist der Stand für main und enthält er
# Entwicklungsinhalte, bricht der Build ab – die Live-Seite bleibt beim letzten sauberen Stand.
# Lokal zusätzlich: ~/Projekte/.git-hooks (core.hooksPath) stoppt Commit/Push auf main.
[ "$VERCEL_GIT_COMMIT_REF" = "main" ] || { echo "Branch ${VERCEL_GIT_COMMIT_REF:-lokal}: keine main-Prüfung."; exit 0; }
treffer=$(grep -rIlE 'data-dev-dd|ENTWICKLUNG:START|Nur in der Entwicklungsumgebung sichtbar|/ Entwicklung /' . \
  --exclude-dir=.git --exclude-dir=werkzeuge --exclude='*.md')
ordner=$(find . -path ./.git -prune -o -ipath '*entwicklung*' -print | grep -v '^\./werkzeuge/')
if [ -n "$treffer$ordner" ]; then
  echo "BUILD GESTOPPT: Entwicklungsinhalte auf main."
  echo "$treffer"; echo "$ordner"
  exit 1
fi
echo "main ist frei von Entwicklungsinhalten."
