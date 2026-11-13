#!/usr/bin/env python3
"""Immutable cumulative 1.0.47 semantic ledger; 142 previous + 38 new reviewed API rows.

12 DRAFT numerical colony fields (14 corrected, 2 pre-reviewed statuses)
plus 26 player-visible battle choices confirmed by original JVM addOption calls.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from apply_1047 import readmap,CHANGES
from audit_1047_jvm import BATTLE_OPTIONS,FLEET,check as original_check

DRAFT={'DRAFT_ONLY_NOT_INSTALLED','OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME'}
PREVIOUS_SHA='8c09fa12c41199e92008551cf89e86a30e59329531ad6ba40731c9d697a73a93'

def fp(r):
    return hashlib.sha256('\0'.join(r[k] for k in ('source_class','english_literal','polish_ascii_draft')).encode('utf8')).hexdigest()

def targets(rows):
    index={(r['source_class'],r['english_literal']):r for r in rows}
    if len(index)!=5260:raise ValueError('Duplicated or missing API mapping')
    adjusted=[k for k in CHANGES if index[k]['status'] in DRAFT]
    if len(adjusted)!=12:raise ValueError(('Incorrect historical draft quantity corpus',len(adjusted)))
    ui=[(FLEET,n) for n in BATTLE_OPTIONS]
    if any(index[k]['status'] not in DRAFT for k in ui):raise ValueError('Unexpected review status on option panel')
    allkeys=set(adjusted+ui)
    if len(allkeys)!=38:raise ValueError('Overlapping review keys')
    return [(index[k],'colony_numeric_unit_grammar_1047' if k in adjusted else 'combat_option_panel_addOption_1047')
            for k in sorted(allkeys)]

def make(root,previous,original_api=None):
    root=Path(root);old=json.loads(Path(previous).read_text('utf8'))
    if old['schema_version']!=1 or old['installed_version']!='1.0.46' or len(old['reviewed'])!=142:
        raise ValueError('Incorrect previous ledger (1.0.46)')
    path=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1047.csv'
    rows=readmap(path)
    if len(rows)!=5260:raise ValueError('Unexpected release map size')
    index={(r['source_class'],fp(r)):r for r in rows}
    if len(index)!=5260:raise ValueError('Map row fingerprints collide')
    old_ids={(x['source_class'],x['row_sha256']) for x in old['reviewed']}
    if len(old_ids)!=142 or any(k not in index for k in old_ids):
        raise ValueError('Old 142 review hashes not preserved exactly')
    selected=targets(rows)
    if any((r['source_class'],fp(r)) in old_ids for r,ev in selected):raise ValueError('Double-counting prior reviewed API row')
    if original_api:
        audit=original_check(original_api)
        if audit['corrected_numeric_english_literals_found']!=14 or audit['original_battle_ui_option_labels_found']!=26:
            raise ValueError('Original JVM 40-string evidence incomplete')
    appended=[{'source_class':r['source_class'],'row_sha256':fp(r),
               'english_key_sha256':hashlib.sha256(r['english_literal'].encode()).hexdigest(),
               'evidence':evidence,
               'review_status':'reviewed_contextual_polish_offline_pending_native_windows'}
              for r,evidence in selected]
    return {'schema_version':1,'installed_version':'1.0.47',
            'review_protocol':'append-only 142 inherited verified API rows plus 12 numeric DRAFT industry messages and 26 battle option-panel strings, original JVM constant pool and 32 addOption callsites verified privately; no Windows gameplay',
            'previous_ledger':'docs/API_SEMANTIC_REVIEW_1046.json','new_reviewed_rows':38,
            'reviewed':old['reviewed']+appended}

def verify(root,previous,ledger,original_api=None):
    expected=make(root,previous,original_api)
    actual=json.loads(Path(ledger).read_text('utf8'))
    if actual!=expected:raise ValueError('1.0.47 review ledger mismatch')
    if len(actual['reviewed'])!=180:raise ValueError('Cumulative review total incorrect')
    return {'historical_api_draft_rows':3658,'prior_offline_reviews':142,
            'new_offline_reviews':38,'cumulative_reviews':180,
            'historical_draft_rows_without_review':3478,'native_windows_gameplay_tested':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
    p.add_argument('--previous',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True)
    p.add_argument('--original-api',type=Path);p.add_argument('--generate',action='store_true')
    a=p.parse_args()
    if a.generate:
        obj=make(a.worktree,a.previous,a.original_api)
        a.ledger.write_text(json.dumps(obj,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps(verify(a.worktree,a.previous,a.ledger,a.original_api),indent=2))
