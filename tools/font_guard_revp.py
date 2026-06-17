#!/usr/bin/env python3
from pathlib import Path
import re, sys, json
root = Path('.')
app_js = (root/'app/src/main/assets/app.js').read_text(encoding='utf-8')
app_css = (root/'app/src/main/assets/app.css').read_text(encoding='utf-8')
tv_css = (root/'app/src/main/assets/app-tv.css').read_text(encoding='utf-8')
html = (root/'app/src/main/assets/index.html').read_text(encoding='utf-8')
build = (root/'app/build.gradle').read_text(encoding='utf-8')
errors = []
warnings = []
required_js = [
  'var LS_AR_FONT = "duaZikrArabicFont"',
  'arabicFont: "noto-naskh"',
  '"noto-naskh": \'"Noto Naskh Arabic", "NotoNaskhArabic", serif\'',
  '"scheherazade": \'"Scheherazade New", "Scheherazade", serif\'',
  '"amiri": \'"Amiri", serif\'',
  '"noto-sans-arabic": \'"Noto Sans Arabic", "NotoSansArabic", sans-serif\'',
  'function applyArabicFontSelection',
  'document.documentElement.style.setProperty("--arabic-font-family"',
  'tvDropdownRow("Arabic Font"',
  'selectRow("Arabic Font"',
  'window.__azkar = { AR_FONTS: AR_FONTS'
]
for token in required_js:
    if token not in app_js:
        errors.append('Missing JS token: ' + token)
for value in ['noto-naskh','scheherazade','amiri','noto-sans-arabic']:
    if value not in app_js:
        errors.append('Missing Arabic font value in JS: ' + value)
if 's.arabicFont = "scheherazade"' in app_js or 'IS_TV ? AR_FONTS.scheherazade' in app_js:
    errors.append('TV still forces Scheherazade in app.js')
required_css = [
  '--arabic-font-family',
  '@font-face { font-family:"Noto Naskh Arabic"',
  '@font-face { font-family:"Noto Sans Arabic"',
  '.set-select[data-key="arabicFont"]',
]
for token in required_css:
    if token not in app_css:
        errors.append('Missing mobile CSS token: ' + token)
required_tv_css = ['body.tv .tv-drop-select', 'body.tv .tv-drop-menu', 'body.tv .tv-drop-option', 'font-family:var(--arabic-font-family) !important']
for token in required_tv_css:
    if token not in tv_css:
        errors.append('Missing TV CSS token: ' + token)
# Hardcoded TV Scheherazade rules are acceptable only as fallback, not forced final Arabic font override.
forced = re.findall(r'body\.tv[^{}]*\.arabic[^{}]*\{[^{}]*font-family:\s*"Scheherazade"[^{}]*!important', tv_css, flags=re.I|re.S)
if forced and 'Rev P Arabic Font Selector TV Lock' not in tv_css:
    errors.append('TV CSS contains forced Scheherazade without Rev P override')
required_fonts = ['NotoNaskhArabic-Regular.ttf','NotoSansArabic-Regular.ttf','ScheherazadeNew-Regular.ttf','Amiri-Regular.ttf','NotoNastaliqUrdu-Regular.ttf']
font_dir = root/'app/src/main/assets/fonts'
missing = [name for name in required_fonts if not (font_dir/name).is_file() or (font_dir/name).stat().st_size < 1024]
if missing:
    errors.append('Missing bundled/prepared font file(s): ' + ', '.join(missing))
if 'versionCode 66' not in build or 'Rev P - Arabic Sentence Ending Lock' not in build:
    errors.append('Rev P Arabic Sentence Ending Lock build version not found')
if 'id="settingsSheet"' not in html or 'id="mArabic"' not in html:
    errors.append('Required settings/Arabic reader HTML IDs missing')
if errors:
    print('REV P FONT GUARD RESULT: FAIL')
    for e in errors: print('ERROR:', e)
    for w in warnings: print('WARN:', w)
    sys.exit(1)
print('REV P FONT GUARD RESULT: PASS')
print('Font options:', ', '.join(['Clean Naskh','Traditional Naskh','Classic Arabic','Simple Arabic']))
