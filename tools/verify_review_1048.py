#!/usr/bin/env python3
"""Cumulative API semantic review: update 3 prior records, append 23 new.

Historical prior evidence remains linked by superseded SHA; changed strings must
never be silently counted as a second review or treated as byte-identical.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from apply_1048 import OLD,NEW,readmap,plan
from verify_review_1047 import fp,DRAFT

def make(root,previous):
    root=Path(root);prev=json.loads(Path(previous).read_text('utf8'))
    if prev.get('installed_version')!='1.0.47' or len(prev.get('reviewed',[]))!=180:
        raise ValueError('Incorrect previous review ledger')
    t=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
    base=readmap(t/OLD);updated=readmap(t/NEW)
    changes,entries,digest=plan(base)
    a={(r['source_class'],r['english_literal']):r for r in base}
    b={(r['source_class'],r['english_literal']):r for r in updated}
    if len(a)!=5260 or len(b)!=5260 or a.keys()!=b.keys():raise ValueError('Mapping keys changed')
    prev_hashes={(v['source_class'],v['row_sha256']) for v in prev['reviewed']}
    if len(prev_hashes)!=180:raise ValueError('Duplicate reviews in preceding ledger')
    for record in prev['reviewed']:
        if not any(r['source_class']==record['source_class'] and fp(r)==record['row_sha256'] for r in base):
            raise ValueError(('Earlier reviewed row no longer exists in predecessor map',record))
    altered={};new_entries=[];existing_non_draft=0
    for key,(old,new) in sorted(changes.items()):
        r_old=a[key];r_new=b[key]
        if fp(r_old)==fp(r_new):raise ValueError('Planned correction did not change review fingerprint')
        old_key=key[0],fp(r_old)
        if old_key in prev_hashes:
            altered[old_key]=fp(r_new)
        elif r_old['status'] in DRAFT:
            new_entries.append({'source_class':key[0], 'row_sha256':fp(r_new),
                'english_key_sha256':hashlib.sha256(key[1].encode()).hexdigest(),
                'evidence':'original_JVM_const_string_number_neutral_1048',
                'review_status':'reviewed_numeric_grammar_offline_pending_native_windows'})
        else:existing_non_draft+=1
    if len(altered)!=3 or len(new_entries)!=23 or existing_non_draft!=3:raise ValueError(('Wrong review partition',len(altered),len(new_entries),existing_non_draft))
    result={'schema_version':1,'installed_version':'1.0.48',
        'review_protocol':'180 previous reviews; 3 previously reviewed rows corrected with explicit superseded hashes, 23 new historical DRAFT rows reviewed plus 3 previously verified non-DRAFT statuses corrected; 203 unique historical DRAFT rows reviewed, 3455 remaining; no Windows gameplay',
        'previous_ledger':'docs/API_SEMANTIC_REVIEW_1047.json',
        'corrected_existing_review_records':3,'corrected_preverified_non_draft_rows':3,'new_reviewed_rows':23,
        'reviewed':[dict(obj,row_sha256=altered[(obj['source_class'],obj['row_sha256'])],
               superseded_1047_row_sha256=obj['row_sha256'],
               correction_evidence_1048='original_JVM_const_string_number_neutral_1048')
             if (obj['source_class'],obj['row_sha256']) in altered else obj
             for obj in prev['reviewed']]+new_entries}
    ids={(x['source_class'],x['row_sha256']) for x in result['reviewed']}
    if len(ids)!=203:raise ValueError('Duplicate rows counted in semantic review')
    updated_ids={(r['source_class'],fp(r)) for r in updated}
    if not ids.issubset(updated_ids):raise ValueError(('Reviewed row missing from mapped output',len(ids-updated_ids)))
    return result

def verify(root,previous,ledger):
    expect=make(root,previous)
    actual=json.loads(Path(ledger).read_text('utf8'))
    if actual!=expect:raise ValueError('Cumulative 1048 ledger diverged from source maps')
    return {'new_reviewed':23,'revised_previously_reviewed':3,'corrected_preverified_non_draft':3,
            'total_reviewed':203,'historical_draft_total':3658,
            'historical_unreviewed':3455,'native_windows_gameplay_tested':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--previous',type=Path,required=True)
    p.add_argument('--ledger',type=Path,required=True);p.add_argument('--generate',action='store_true')
    a=p.parse_args()
    if a.generate:a.ledger.write_text(json.dumps(make(a.worktree,a.previous),ensure_ascii=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps(verify(a.worktree,a.previous,a.ledger),indent=2))
