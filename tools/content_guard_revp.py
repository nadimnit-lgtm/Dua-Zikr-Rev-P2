#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTENT=ROOT/'app/src/main/assets/content/content.json'
QA=ROOT/'qa-results'
QA.mkdir(exist_ok=True)
errors=[]
warnings=[]

def err(msg): errors.append(msg)
def warn(msg): warnings.append(msg)

def notes_text(v):
    if isinstance(v, list): return ' | '.join(str(x) for x in v)
    return str(v or '')


AR_FULL_STOP='۔'
ACCEPTED_AR_END_RE=re.compile(r'(?:[۔۝۩۞؞؟!?؛]|[\)\]\}﴿﴾]|(?:قلى|صلى|لا|[مجطزصقسع]))\s*$')
DUPLICATE_AR_PUNCT_RE=re.compile(r'(?:۔۔|\.۔|۔\.|؟؟|!!|۝۔|۔۝)')
ELIGIBLE_PUNCT_TYPES={'Dua','Azkar','Kalima','Salawat','Istighfar','Dhikr','Reminder'}

def strip_tags(v):
    return re.sub(r'<[^>]*>', '', str(v or '')).strip()

def is_quranic_item(it):
    hay=' '.join(str(it.get(k,'')) for k in ['source','category','type','main_category','verification','id']).lower()
    tags=' '.join(str(x) for x in it.get('tags',[]) or []).lower()
    return 'quran' in hay or 'qur' in hay or 'quran' in tags or 'qur' in tags or str(it.get('verification','')).lower()=='quran'

def is_instruction_only_item(it):
    if str(it.get('type',''))=='Guidance':
        return True
    title=' '.join(str(it.get(k,'')) for k in ['title','title_en','category']).lower()
    return 'rule' in title or 'instruction' in title

def display_arabic(it):
    return str(it.get('arabic_punctuated') or it.get('arabic') or '').strip()

def display_tajweed(it):
    return str(it.get('tajweed_html_punctuated') or it.get('tajweed_html') or '').strip()

def ends_accepted_ar(text):
    return bool(ACCEPTED_AR_END_RE.search(str(text or '').replace('\u200e','').replace('\u200f','').strip()))

try:
    data=json.loads(CONTENT.read_text(encoding='utf-8'))
except Exception as e:
    print(f'ERROR: invalid JSON: {e}')
    sys.exit(1)

items=data.get('items')
if not isinstance(items, list):
    err('content.json must contain items list')
    items=[]

if len(items)!=233:
    err(f'item count changed: expected 233, got {len(items)}')

ids=[]
for idx,it in enumerate(items):
    id_=it.get('id')
    if not id_:
        err(f'item[{idx}] missing id')
        continue
    ids.append(id_)
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', id_):
        err(f'{id_}: id is not lowercase hyphen format')
    if it.get('verification_status') != 'Verified':
        err(f'{id_}: verification_status must be Verified under Rev P source-based pass; found {it.get("verification_status")!r}')
    if it.get('rotation_allowed') is not True:
        err(f'{id_}: rotation_allowed must be true for all items under revised Rev P rule')
    if it.get('display_status') in {'review_only', 'section_only', 'alternate_wording'}:
        err(f'{id_}: display_status still blocks or classifies content outside normal rotation: {it.get("display_status")!r}')
    if 'urdu_status' not in it:
        err(f'{id_}: missing urdu_status')
    notes=notes_text(it.get('verification_notes'))
    if not notes:
        err(f'{id_}: missing verification_notes')
    if 'reliable online' not in notes and 'Traditional name verified' not in notes:
        err(f'{id_}: verification_notes must document reliable online verification basis')
    if 'excluded from normal rotation' in notes.lower():
        err(f'{id_}: old exclusion wording remains in verification_notes')
    if 'before normal rotation' in notes.lower():
        err(f'{id_}: old normal-rotation blocker wording remains in verification_notes')
    if 'pending final scholarly' in notes.lower() or 'final scholarly' in notes.lower():
        err(f'{id_}: obsolete scholarly-blocker wording remains in verification_notes')
    if it.get('traditional_name') and 'Traditional name verified against reliable online references.' not in notes:
        err(f'{id_}: non-null traditional_name missing online verification note')
    source=str(it.get('source',''))
    if not source.strip():
        err(f'{id_}: missing source')
    if re.search(r'pending review|pending exact|review remains|required before normal rotation|not confirmed', source, re.I):
        err(f'{id_}: source contains review/pending wording')
    if it.get('arabic_uthmani') is not None and not isinstance(it.get('arabic_uthmani'), bool):
        err(f'{id_}: arabic_uthmani must remain boolean when present')

    # Rev P Addition: Arabic sentence-ending and Urdu full stop display lock.
    # Quranic items must remain untouched; eligible non-Quranic complete cards must
    # render with accepted Arabic ending punctuation, preferably U+06D4 (۔).
    is_q=is_quranic_item(it)
    ar_display=display_arabic(it)
    if is_q:
        if it.get('arabic_punctuated') or it.get('tajweed_html_punctuated'):
            err(f'{id_}: Quranic item must not receive generated Arabic punctuation fields')
    elif ar_display and str(it.get('type','')) in ELIGIBLE_PUNCT_TYPES and not is_instruction_only_item(it):
        if not ends_accepted_ar(ar_display):
            err(f'{id_}: eligible non-Quranic Arabic display must end with accepted Arabic punctuation')
        if re.search(r'\.\s*$', ar_display):
            err(f'{id_}: Arabic display ends with English full stop instead of Arabic/Urdu full stop')
        if DUPLICATE_AR_PUNCT_RE.search(ar_display):
            err(f'{id_}: duplicate or mixed Arabic punctuation found in Arabic display')
        if not (it.get('arabic_punctuated') or ends_accepted_ar(str(it.get('arabic','')))):
            err(f'{id_}: missing arabic_punctuated display field for abrupt non-Quranic Arabic source')
        if it.get('tajweed_html'):
            tj_display=strip_tags(display_tajweed(it))
            if ar_display.endswith(AR_FULL_STOP) and not tj_display.endswith(AR_FULL_STOP):
                err(f'{id_}: Tajweed HTML punctuation does not match plain Arabic punctuation')
            if DUPLICATE_AR_PUNCT_RE.search(tj_display):
                err(f'{id_}: duplicate or mixed Arabic punctuation found in Tajweed display')

for id_,count in Counter(ids).items():
    if count>1:
        err(f'duplicate id: {id_}')

summary={
    'revision':'Rev P',
    'total_items':len(items),
    'errors':errors,
    'warnings':warnings,
    'verification_status_counts':dict(Counter(str(it.get('verification_status')) for it in items)),
    'rotation_allowed_counts':dict(Counter(str(it.get('rotation_allowed')) for it in items)),
    'traditional_name_count':sum(1 for it in items if it.get('traditional_name')),
    'arabic_sentence_ending_policy':data.get('arabic_sentence_ending_policy'),
    'arabic_sentence_ending_applied_count':data.get('arabic_sentence_ending_applied_count'),
}
(QA/'content-guard-rev-p.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
lines=[]
lines.append('Rev P content guard')
lines.append(f"Items checked: {len(items)}")
lines.append(f"Errors: {len(errors)}")
lines.append(f"Warnings: {len(warnings)}")
for e in errors: lines.append('ERROR: '+e)
for w in warnings: lines.append('WARN: '+w)
lines.append('RESULT: PASS' if not errors else 'RESULT: FAIL')
(QA/'content-guard-rev-p.log').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines))
if errors:
    sys.exit(1)
