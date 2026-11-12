#!/usr/bin/env python3
"""Negative tests: CSV technical fields, exact text deltas and unauthorized versions."""
from __future__ import annotations
import argparse,csv,io,json,tempfile
from pathlib import Path
from apply_1039 import patch_bytes,PATCHES,OLD_SHA,NEW_SHA,sha
from verify_1039 import revert,verify

def run(root):
    src=(root/'mod/data/campaign/rules.csv').read_bytes();prior=revert(src)
    assert patch_bytes(prior)[0]==src
    def bad(blob,reason):
        try:patch_bytes(blob)
        except (ValueError,AssertionError):return
        raise AssertionError('Accepted tampering: '+reason)
    tests=[]
    def case(name,new):
        assert new!=prior,('Mutation had no effect',name)
        bad(new,name);tests.append(name)
    case('unexpected checksum',prior+b'garbage')
    case('missing newline',prior[:-2])
    case('modified script field',prior.replace(b'ShowDefaultVisual',b'ShowDefaultVisuaI',1))
    case('modified condition byte',prior.replace(b'$option ==',b'$option !=',1))
    case('modified title',prior.replace(b'greetingDefaultInfamousFriendly',b'greetingDefaultInfamousFriendlx',1))
    case('repeated row id',prior.replace(b'greetingDefaultInfamousFriendly',b'customsInspectionConvStart',1))
    case('already patched refuses second run',src)
    case('fake ASCII control',prior+b'\x00')
    case('non-ascii text',prior+b'\xc5')
    case('truncated input',prior[:500])
    case('unapproved quote mutation',prior.replace(b'Kapitan',b'kapitan',1))
    case('unknown old-hash',prior.replace(b'\r\n',b'\n',1))
    good=verify(root);assert good['changed_rows']==62 and good['verified_options']==7371
    return {'negative_cases':len(tests),'case_names':tests,'positive_full_data_and_options':True}

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('worktree',type=Path);x=a.parse_args();print(json.dumps(run(x.worktree),indent=2))
