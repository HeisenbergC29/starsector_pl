#!/usr/bin/env python3
"""Fail-closed 1.1 gate check: account for verified OFFLINE reviews, not gameplay.

The source mapping has unchanged DRAFT statuses. Previously the gate checker
used those statuses as the number of *unreviewed* translations; this version
subtracts only rows listed in a validated, immutable-fingerprint review ledger.
"""
from __future__ import annotations
import argparse,csv,json,re
from pathlib import Path
from verify_review_1031 import verify as verify_ledger

REQUIRED=('story_contexts','pronoun_contexts','draft_semantics','text_completeness','windows_runtime')
ALLOWED={'blocked','in_progress','verified'}
DRAFT={'OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_ONLY_NOT_INSTALLED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME'}

def check(worktree:Path,manifest:Path,ledger:Path,strict:bool=False)->dict:
    gates=json.loads(manifest.read_text('utf8'))
    assert gates.get('schema_version')==1 and gates.get('target_version')=='1.1'
    items=gates['gates'];byid={x['id']:x for x in items}
    assert len(byid)==len(items) and set(byid)==set(REQUIRED)
    for key,gate in byid.items():
        assert gate.get('status') in ALLOWED and gate.get('source'),key
        if gate['status']=='verified':
            assert gate.get('evidence_file') and gate.get('human_or_game_review'),key
    meta=json.loads((worktree/'mod/mod_info.json').read_text('utf8'))
    version=meta['version']
    assert re.fullmatch(r'\d+(?:\.\d+)+',version) and meta['gameVersion']=='0.98a-RC8'
    maps=sorted((worktree/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations').glob('TLUMACZENIA_JAR_*.csv'))
    assert maps,'API translation map missing'
    active=max(maps,key=lambda p:int(p.stem.rsplit('_',1)[1]))
    with active.open(encoding='utf8',newline='') as f: rows=list(csv.DictReader(f))
    draft=[r for r in rows if r['status'] in DRAFT]
    semantic=json.loads(ledger.read_text('utf8'))
    checked=verify_ledger(rows,semantic)
    gate=byid['draft_semantics']
    assert gate.get('review_ledger')=='docs/API_SEMANTIC_REVIEW_1031.json'
    assert gate.get('total_draft_rows')==len(draft)==3658
    assert gate.get('reviewed_offline')==checked['reviewed_offline_not_gameplay']==30
    assert gate.get('unresolved_count')==checked['still_need_review']==3628
    assert gate.get('gameplay_unverified_count')==checked['remaining_windows_gameplay_reviews']==3658
    blocked=[k for k in REQUIRED if byid[k]['status']!='verified']
    if (version=='1.1' or strict) and blocked:
        raise RuntimeError('Cannot release Starsector PL 1.1: unverified gates '+', '.join(blocked))
    return {'current_version':version,'target_version':'1.1','active_api_map':active.name,
            'draft_optional_rows':len(draft),'reviewed_offline':checked['reviewed_offline_not_gameplay'],
            'pending_semantic_review':checked['still_need_review'],
            'pending_windows_gameplay_checks':checked['remaining_windows_gameplay_reviews'],
            'blocked_gates':blocked,'final_release_allowed':not blocked}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('worktree',type=Path)
    ap.add_argument('--gates',type=Path,default=Path('docs/RELEASE_GATES_11.json'))
    ap.add_argument('--ledger',type=Path,default=Path('docs/API_SEMANTIC_REVIEW_1031.json'))
    ap.add_argument('--strict',action='store_true')
    a=ap.parse_args();print(json.dumps(check(a.worktree,a.gates,a.ledger,a.strict),indent=2))
if __name__=='__main__':main()
