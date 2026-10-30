#!/usr/bin/env bash
# Régénère Pixel-of-Glory-fiche-A5.pdf et .png à partir de index.html
# Usage : depuis ce dossier,  ./regen.sh
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

PORT="${PORT:-8765}"
PNG="$DIR/Pixel-of-Glory-fiche-A5.png"
PDF="$DIR/Pixel-of-Glory-fiche-A5.pdf"
WAIT="${WAIT:-8}"

# Si le port est pris, on en prend un autre.
if command -v python3 >/dev/null; then
  PORT="$(PORT="$PORT" python3 - <<'PY'
import os, socket
p = int(os.environ.get("PORT", "8765"))
for port in range(p, p + 20):
    s = socket.socket()
    try:
        s.bind(("127.0.0.1", port))
        s.close()
        print(port)
        break
    except OSError:
        s.close()
else:
    raise SystemExit("aucun port libre")
PY
)"
fi
URL="http://127.0.0.1:${PORT}/?shot"

find_chrome() {
  local c
  for c in \
    google-chrome \
    google-chrome-stable \
    chromium \
    chromium-browser \
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    "/Applications/Chromium.app/Contents/MacOS/Chromium"
  do
    if command -v "$c" >/dev/null 2>&1; then
      echo "$c"
      return
    fi
    if [[ -x "$c" ]]; then
      echo "$c"
      return
    fi
  done
  return 1
}

if ! CHROME="$(find_chrome)"; then
  echo "Chrome / Chromium introuvable." >&2
  echo "Sans script : ouvre index.html, bouton « Imprimer / PDF », format A5, marges 0, graphiques d’arrière-plan activés." >&2
  exit 1
fi

# Petit serveur : polices et images se chargent de façon fiable (file:// casse parfois).
python3 -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT
sleep 0.3

run_chrome() {
  local out="$1"
  shift
  local tmp
  tmp="$(mktemp -d)"
  # Chrome headless écrit le fichier puis reste parfois bloqué : on le tue après WAIT.
  "$CHROME" \
    --headless=new \
    --no-sandbox \
    --disable-gpu \
    --disable-dev-shm-usage \
    --hide-scrollbars \
    --user-data-dir="$tmp" \
    --no-pdf-header-footer \
    "$@" \
    "$URL" >/dev/null 2>&1 &
  local pid=$!
  local i=0
  while (( i < WAIT )); do
    sleep 1
    if [[ -s "$out" ]]; then
      sleep 1
      break
    fi
    i=$((i + 1))
  done
  kill "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
  sleep 0.2
  rm -rf "$tmp" 2>/dev/null || true
}

echo "PNG…"
rm -f "$PNG"
run_chrome "$PNG" \
  --force-device-scale-factor=2 \
  --window-size=560,794 \
  --screenshot="$PNG"

echo "PDF…"
rm -f "$PDF"
run_chrome "$PDF" --print-to-pdf="$PDF"

if [[ ! -s "$PNG" || ! -s "$PDF" ]]; then
  echo "Échec : PNG ou PDF vide." >&2
  echo "Ouvre index.html et utilise le bouton Imprimer / PDF." >&2
  exit 1
fi

echo "OK"
echo "  $PNG"
echo "  $PDF"
