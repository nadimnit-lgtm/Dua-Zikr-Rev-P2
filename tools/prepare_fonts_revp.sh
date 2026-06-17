#!/usr/bin/env bash
set -euo pipefail
FONT_DIR="app/src/main/assets/fonts"
mkdir -p "${FONT_DIR}" "${FONT_DIR}/LICENSES"

copy_first_found() {
  local dest="$1"; shift
  if [[ -s "${FONT_DIR}/${dest}" ]]; then return 0; fi
  for src in "$@"; do
    if [[ -s "$src" ]]; then cp "$src" "${FONT_DIR}/${dest}" && return 0; fi
  done
  return 1
}

fetch_url() {
  local dest="$1"; shift
  if [[ -s "${FONT_DIR}/${dest}" ]]; then return 0; fi
  for url in "$@"; do
    echo "Trying ${dest}: ${url}"
    if curl -fL --retry 3 --retry-delay 2 -o "${FONT_DIR}/${dest}.tmp" "$url"; then
      mv "${FONT_DIR}/${dest}.tmp" "${FONT_DIR}/${dest}"
      return 0
    fi
  done
  rm -f "${FONT_DIR}/${dest}.tmp"
  return 1
}

# Prefer OS fonts when present, then official public repositories as CI fallback.
copy_first_found "NotoNaskhArabic-Regular.ttf" \
  /usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf \
  /usr/share/fonts/truetype/noto/NotoNaskhArabicUI-Regular.ttf || \
fetch_url "NotoNaskhArabic-Regular.ttf" \
  "https://raw.githubusercontent.com/google/fonts/main/ofl/notonaskharabic/NotoNaskhArabic%5Bwght%5D.ttf"

copy_first_found "NotoSansArabic-Regular.ttf" \
  /usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf \
  /usr/share/fonts/truetype/noto/NotoSansArabicUI-Regular.ttf || \
fetch_url "NotoSansArabic-Regular.ttf" \
  "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansarabic/NotoSansArabic%5Bwdth%2Cwght%5D.ttf"

copy_first_found "Amiri-Regular.ttf" /usr/share/fonts/truetype/fonts-arabeyes/Amiri-Regular.ttf /usr/share/fonts/truetype/amiri/Amiri-Regular.ttf /usr/share/fonts/opentype/fonts-hosny-amiri/Amiri-Regular.ttf || \
fetch_url "Amiri-Regular.ttf" "https://raw.githubusercontent.com/google/fonts/main/ofl/amiri/Amiri-Regular.ttf"
copy_first_found "Amiri-Bold.ttf" /usr/share/fonts/truetype/fonts-arabeyes/Amiri-Bold.ttf /usr/share/fonts/truetype/amiri/Amiri-Bold.ttf /usr/share/fonts/opentype/fonts-hosny-amiri/Amiri-Bold.ttf || \
fetch_url "Amiri-Bold.ttf" "https://raw.githubusercontent.com/google/fonts/main/ofl/amiri/Amiri-Bold.ttf"

copy_first_found "NotoNastaliqUrdu-Regular.ttf" /usr/share/fonts/truetype/noto/NotoNastaliqUrdu-Regular.ttf || \
fetch_url "NotoNastaliqUrdu-Regular.ttf" "https://raw.githubusercontent.com/google/fonts/main/ofl/notonastaliqurdu/NotoNastaliqUrdu%5Bwght%5D.ttf"

copy_first_found "ScheherazadeNew-Regular.ttf" /usr/share/fonts/truetype/scheherazade/ScheherazadeNew-Regular.ttf /usr/share/fonts/truetype/sil/ScheherazadeNew-Regular.ttf /usr/share/fonts/truetype/sil-scheherazade/ScheherazadeNew-Regular.ttf /usr/share/fonts/truetype/scheherazade-new/ScheherazadeNew-Regular.ttf || \
fetch_url "ScheherazadeNew-Regular.ttf" "https://raw.githubusercontent.com/google/fonts/main/ofl/scheherazadenew/ScheherazadeNew-Regular.ttf"
copy_first_found "ScheherazadeNew-Bold.ttf" /usr/share/fonts/truetype/scheherazade/ScheherazadeNew-Bold.ttf /usr/share/fonts/truetype/sil/ScheherazadeNew-Bold.ttf /usr/share/fonts/truetype/sil-scheherazade/ScheherazadeNew-Bold.ttf /usr/share/fonts/truetype/scheherazade-new/ScheherazadeNew-Bold.ttf || \
fetch_url "ScheherazadeNew-Bold.ttf" "https://raw.githubusercontent.com/google/fonts/main/ofl/scheherazadenew/ScheherazadeNew-Bold.ttf"

# Reem Kufi is UI-only. Build can proceed without it, but keep it when already present.
cat > "${FONT_DIR}/LICENSES/README.md" <<'TXT'
Arabic and Urdu font assets are open fonts. For CI builds, Rev P prepares missing font files from OS packages or public upstream font repositories before Gradle packages the APK. Keep license files with any manually bundled font binaries.
TXT

python3 - <<'PY'
from pathlib import Path
required = [
  'NotoNaskhArabic-Regular.ttf', 'NotoSansArabic-Regular.ttf',
  'ScheherazadeNew-Regular.ttf', 'Amiri-Regular.ttf', 'NotoNastaliqUrdu-Regular.ttf'
]
font_dir = Path('app/src/main/assets/fonts')
missing = [name for name in required if not (font_dir / name).is_file() or (font_dir / name).stat().st_size < 1024]
if missing:
    raise SystemExit('Missing required Rev P font file(s): ' + ', '.join(missing))
print('Rev P font assets prepared:', ', '.join(required))
PY
