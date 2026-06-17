#!/usr/bin/env python3
from pathlib import Path
import re, sys, hashlib
ROOT=Path('.')
paths=[
  ROOT/'app/src/main/assets/app.js',
  ROOT/'app/src/main/assets/app.css',
  ROOT/'app/src/main/assets/app-tv.css',
  ROOT/'app/src/main/assets/index.html',
  ROOT/'app/src/main/AndroidManifest.xml',
  ROOT/'app/build.gradle',
]
errors=[]

def read(p): return p.read_text(encoding='utf-8')
texts={str(p):read(p) for p in paths}
app_js=texts['app/src/main/assets/app.js']
app_css=texts['app/src/main/assets/app.css']
tv_css=texts['app/src/main/assets/app-tv.css']
html=texts['app/src/main/assets/index.html']
build=texts['app/build.gradle']
manifest=texts['app/src/main/AndroidManifest.xml']
for label,text in texts.items():
    for bad in ['TODO','FIXME','XXX','PLACEHOLDER','TBD','debugger','alert(']:
        if bad in text:
            errors.append(f'{label}: unresolved development token remains: {bad}')
for bad in ['highContrast','high-contrast','contrastBtn','High Contrast','audioBase','recAudio','recBtn','recitationNotes','waqfNotes']:
    hay='\n'.join(texts.values())
    if bad in hay:
        errors.append(f'forbidden legacy token remains in app source: {bad}')
for obsolete in ['theme-card','tv-font-select','tv-font-wrap','tv-font-menu','tv-font-option']:
    hay='\n'.join(texts.values())
    if obsolete in hay:
        errors.append(f'obsolete Settings implementation token remains: {obsolete}')
if 'versionCode 66' not in build or 'versionName "Rev P - Arabic Sentence Ending Lock"' not in build:
    errors.append('build.gradle must declare versionCode 66 and versionName Rev P - Arabic Sentence Ending Lock')
if "namespace 'com.ahmed.azkartv'" not in build or 'applicationId "com.ahmed.azkartv"' not in build:
    errors.append('package identity changed or missing')
if 'android.intent.category.LEANBACK_LAUNCHER' not in manifest:
    errors.append('Android TV launcher category missing')
if 'rawAr > 2.0 || rawAr < 0.1' not in app_js:
    errors.append('TV saved Arabic-size persistence still not locked to 10%-200%')
if 'num("arScale", 0.1, 2.0' not in app_js:
    errors.append('Arabic size normalizer missing 10%-200% range')
if 'tvStepperRow("Arabic text size"' not in app_js or 'stepperRow("Arabic text size"' not in app_js:
    errors.append('Arabic size row missing from TV or mobile Settings')
if 'tvDropdownRow("Arabic Font"' not in app_js or 'selectRow("Arabic Font"' not in app_js:
    errors.append('Arabic font dropdown missing from TV or mobile Settings')
if 'tvSelectRow("Theme"' not in app_js or 'selectRow("Theme"' not in app_js:
    errors.append('Theme dropdown missing from TV or mobile Settings')
# CSS brace check
for p in [ROOT/'app/src/main/assets/app.css', ROOT/'app/src/main/assets/app-tv.css']:
    depth=0
    for i,ch in enumerate(read(p)):
        if ch=='{': depth+=1
        elif ch=='}': depth-=1
        if depth<0: errors.append(f'{p}: CSS brace underflow at {i}'); break
    if depth: errors.append(f'{p}: CSS brace mismatch depth {depth}')
print('REV P SOURCE CLEAN GUARD RESULT:', 'PASS' if not errors else 'FAIL')
for e in errors: print('ERROR:', e)
if errors: sys.exit(1)
for rel in ['app/src/main/assets/app.js','app/src/main/assets/app.css','app/src/main/assets/app-tv.css']:
    h=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
    print(f'{rel} SHA-256 {h}')
