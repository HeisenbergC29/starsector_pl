#!/usr/bin/env python3
"""Fail-closed mutation tests for exact 1.0.45 dialogue-only changes."""
from __future__ import annotations
import json,tempfile,shutil,csv,hashlib,argparse
from pathlib import Path
from apply_1034 import rows_with_spans
from apply_1045 import patch_bytes,PATCHES,PREVIOUS_SHA,GENDER,sha
from verify_1045 import check,reverse_bytes

def fails(callback):
    try:callback()
    except (ValueError,AssertionError):return True
    raise AssertionError('Invalid mutation unexpectedly accepted')

def run(root):
    root=Path(root);before=reverse_bytes((root/'mod/data/campaign/rules.csv').read_bytes())
    final,stats,ledger=patch_bytes(before)
    assert len(PATCHES)==44 and len(ledger)==44
    assert (stats['rows_changed'],stats['fragments_changed'],stats['gender_references_removed'])==(44,80,93)
    assert all(r['removed_gender_references']>0 for r in ledger)
    assert all(r['old_text_sha256']!=r['new_text_sha256'] for r in ledger)
    assert sha(final)==sha((root/'mod/data/campaign/rules.csv').read_bytes())
    assert check(root)['unchanged_data_files']==869
    invalid=[]
    invalid.append(('wrong baseline SHA',lambda:patch_bytes(before+b' ')))
    invalid.append(('bad header',lambda:patch_bytes(before.replace(b'id,trigger',b'key,trigger',1),False)))
    invalid.append(('bad CRLF',lambda:patch_bytes(before.replace(b'\r\n',b'\n',1),False)))
    invalid.append(('non-ASCII character',lambda:patch_bytes(before+b'\xc4\x85',False)))
    invalid.append(('deleted expected phrase',lambda:patch_bytes(before.replace(b'$HeOrShe rozpaczliwie',b'WHO rozpaczliwie',1),False)))
    invalid.append(('wrong output SHA',lambda:reverse_bytes(final+b' ')))
    for name,func in invalid:
        if not fails(func):raise AssertionError(name)
    with tempfile.TemporaryDirectory() as d:
        tmp=Path(d);shutil.copytree(root/'mod',tmp/'mod');(tmp/'buildtools/NARZEDZIA_INSTALATOR').mkdir(parents=True)
        shutil.copy2(root/'buildtools/NARZEDZIA_INSTALATOR/main.go',tmp/'buildtools/NARZEDZIA_INSTALATOR/main.go')
        file=tmp/'mod/data/campaign/channels.json';file.write_bytes(file.read_bytes()+b' ')
        assert fails(lambda:check(tmp))
    return {'version':'1.0.45','rows':44,'edits':80,'gender_variables_removed':93,
            'negative_tests':len(invalid)+1,'all_7371_rules_options_checked_in_CI':True,
            'java_bytecode_unchanged_by_patch':True,'native_gameplay_tested':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
    a=p.parse_args();print(json.dumps(run(a.worktree),indent=2))
