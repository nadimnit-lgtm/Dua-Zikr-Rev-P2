#!/usr/bin/env python3
from pathlib import Path
import sys
root = Path('.')
app_js = (root/'app/src/main/assets/app.js').read_text(encoding='utf-8')
app_css = (root/'app/src/main/assets/app.css').read_text(encoding='utf-8')
tv_css = (root/'app/src/main/assets/app-tv.css').read_text(encoding='utf-8')
html = (root/'app/src/main/assets/index.html').read_text(encoding='utf-8')
errors = []
for label, text in [('app.js', app_js), ('app.css', app_css), ('app-tv.css', tv_css), ('index.html', html)]:
    for bad in ['high'+'Contrast', 'high'+'-contrast', 'contrast'+'Btn', 'High'+' Contrast']:
        if bad in text:
            errors.append(f'{label}: forbidden legacy contrast token remains: {bad}')

# Arabic size must persist after restart across the full approved 10%-200% range.
for bad in ['rawAr > 1.45', 'rawAr < 0.7', 's.arScale = 0.7; repaired = true; }']:
    if bad in app_js and 'rawAr > 2.0' not in app_js:
        errors.append('app.js contains obsolete TV Arabic-size reset token: ' + bad)
if 'rawAr > 2.0 || rawAr < 0.1' not in app_js:
    errors.append('app.js missing full-range TV Arabic-size persistence guard 0.1-2.0')
for obsolete in ['theme-card', 'tv-font-select', 'tv-font-menu', 'tv-font-option']:
    if obsolete in app_js or obsolete in app_css or obsolete in tv_css or obsolete in html:
        errors.append('obsolete Settings UI token remains in app assets: ' + obsolete)

required_js = [
    'showTitle: true',
    'function safeDisplayTitle',
    'function titleLooksTechnical',
    'num("arScale", 0.1, 2.0',
    'tvStepperRow("Arabic text size", "A− / A+ changes Arabic size live from 10% to 200%.", "arScale", 0.1, 0.1, 2.0, true)',
    'stepperRow("Arabic text size", "Range 10% to 200%, step 10%.", "arScale", 0.1, 0.1, 2.0)',
    'tvDropdownRow("Arabic Font"',
    'selectRow("Arabic Font"',
    'selectRow("Theme", "Dropdown selector with Dark and Light only."',
    'tvSelectRow("Theme", "Dropdown selector with Dark and Light only."',
    '["15 sec", 15]', '["30 sec", 30]', '["45 sec", 45]', '["60 sec", 60]',
    'closeTvDropdown();', 'openTvDropdown', 'selectTvDropdownValue',
    'themeQuickBtn', 'arSizeValue'
]
for token in required_js:
    if token not in app_js:
        errors.append('app.js missing Rev P settings token: ' + token)
required_labels = [
    'Show item name', 'Transliteration', 'English translation', 'Urdu translation', 'Source / reference',
    'Arabic Font', 'Arabic text size', 'Bismillah size', 'Pause marks', 'Tajweed', 'Arabic script',
    'Prayer ribbon', 'Prayer detail level', 'City / Location', 'Auto rotation', 'Display duration',
    'Theme', 'Page progress indicator', 'Show tags on display', 'Language', 'App Information'
]
for token in required_labels:
    if token not in app_js:
        errors.append('Required Settings label missing: ' + token)
required_css = ['.ar-size-value', '.set-select', '.set-group', '--arabic-font-family']
for token in required_css:
    if token not in app_css:
        errors.append('app.css missing Rev P token: ' + token)
required_tv_css = ['body.tv .tv-drop-select', 'body.tv .tv-drop-menu', 'body.tv .tv-drop-option', 'body.tv .ar-size-value']
for token in required_tv_css:
    if token not in tv_css:
        errors.append('app-tv.css missing Rev P TV token: ' + token)
required_html = ['id="themeQuickBtn"', 'id="arSizeValue"', 'id="settingsSheet"', 'id="mTitle"']
for token in required_html:
    if token not in html:
        errors.append('index.html missing token: ' + token)
if errors:
    print('REV P SETTINGS GUARD RESULT: FAIL')
    for e in errors:
        print('ERROR:', e)
    sys.exit(1)
print('REV P SETTINGS GUARD RESULT: PASS')
print('Locked areas: Arabic size 10-200, title display, font dropdown, theme dropdown, legacy contrast removal, Settings control coverage')
