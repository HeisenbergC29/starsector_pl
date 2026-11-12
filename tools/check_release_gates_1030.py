#!/usr/bin/env python3
"""Do not label Starsector PL 1.1 until its actual acceptance gates have evidence.

This is intentionally separate from a CI pass. GitHub Actions can verify code
and installers without ever launching Starsector on Windows.
"""
from __future__ import annotations
import argparse, csv, json, re
from pathlib import Path

REQUIRED = ('story_contexts','pronoun_contexts','draft_semantics','text_completeness','windows_runtime')
ALLOWED = {'blocked','in_progress','verified'}


def check(worktree: Path, manifest: Path, strict: bool=False) -> dict:
    info=json.loads(manifest.read_text('utf8'))
    assert info['schema_version']==1 and info['target_version']=='1.1'
    byid={r['id']:r for r in info['gates']}
    assert len(byid)==len(info['gates']) and set(byid)==set(REQUIRED)
    for key, gate in byid.items():
        assert gate['status'] in ALLOWED,(key,gate['status'])
        assert gate.get('source'),key
        if gate['status']=='verified':
            assert gate.get('evidence_file') and gate.get('human_or_game_review'),key
    meta=json.loads((worktree/'mod/mod_info.json').read_text('utf8'))
    version=meta['version'];assert re.match(r'^\d+(?:\.\d+)+$',version)
    assert meta['gameVersion']=='0.98a-RC8'
    api=worktree/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1029.csv'
    if api.exists():
        with api.open('r',encoding='utf8',newline='') as f:
            rows=list(csv.DictReader(f))
        status_counts={k:sum(1 for row in rows if row['status']==k) for k in
                       ('OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_ONLY_NOT_INSTALLED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME')}
        old_review=sum(status_counts.values())
        assert old_review==3659,('untracked historical review pool',old_review)
    else:
        status_counts={};old_review=None
    blocked=[key for key in REQUIRED if byid[key]['status']!='verified']
    # Strict mode can be used for a proposed final release, independent of the mod version.
    if (version=='1.1' or strict) and blocked:
        raise RuntimeError('Cannot release Starsector PL 1.1: unverified gates '+', '.join(blocked))
    return {'current_version':version,'target':'1.1','blocked_gates':blocked,
            'verified_gates':sorted(set(REQUIRED)-set(blocked)),
            'historical_draft_optional_entries':old_review,
            'historical_status_counts':status_counts,'final_release_allowed':not blocked}


def main():
    a=argparse.ArgumentParser();a.add_argument('worktree',type=Path)
    a.add_argument('--gates',type=Path,default=Path('docs/RELEASE_GATES_11.json'))
    a.add_argument('--strict',action='store_true')
    opts=a.parse_args();print(json.dumps(check(opts.worktree,opts.gates,opts.strict),indent=2))
if __name__=='__main__':main()
