#!/usr/bin/env bash
# Recrée img-embed.js à partir de img/*.png
# (nécessaire seulement si tu changes les images des cartes)
# Mac / Linux, sans Python :  ./embed-images.sh
set -euo pipefail
cd "$(dirname "$0")"

b64() {
  if base64 -w0 /dev/null >/dev/null 2>&1; then
    base64 -w0 "$1"
  else
    base64 -i "$1" | tr -d '\n'
  fi
}

{
  echo "window.EMBEDDED_IMAGES = {"
  for f in img/*.png; do
    name="${f##*/}"
    echo "  '$name': 'data:image/png;base64,$(b64 "$f")',"
  done
  echo "};"
} > img-embed.js

echo "OK img-embed.js ($(wc -c < img-embed.js) octets)"
