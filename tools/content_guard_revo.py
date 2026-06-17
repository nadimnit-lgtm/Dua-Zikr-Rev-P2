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
        err(f'{id_}: verification_status must be Verified under Rev O source-based pass; found {it.get("verification_status")!r}')
    if it.get('rotation_allowed') is not True:
        err(f'{id_}: rotation_allowed must be true for all items under revised Rev O rule')
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

for id_,count in Counter(ids).items():
    if count>1:
        err(f'duplicate id: {id_}')

summary={
    'revision':'Rev O',
    'total_items':len(items),
    'errors':errors,
    'warnings':warnings,
    'verification_status_counts':dict(Counter(str(it.get('verification_status')) for it in items)),
    'rotation_allowed_counts':dict(Counter(str(it.get('rotation_allowed')) for it in items)),
    'traditional_name_count':sum(1 for it in items if it.get('traditional_name')),
}
(QA/'content-guard-rev-o.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
lines=[]
lines.append('Rev O content guard')
lines.append(f"Items checked: {len(items)}")
lines.append(f"Errors: {len(errors)}")
lines.append(f"Warnings: {len(warnings)}")
for e in errors: lines.append('ERROR: '+e)
for w in warnings: lines.append('WARN: '+w)
lines.append('RESULT: PASS' if not errors else 'RESULT: FAIL')
(QA/'content-guard-rev-o.log').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines))
if errors:
    sys.exit(1)
