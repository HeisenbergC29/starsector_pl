#!/usr/bin/env python3
"""Regression/negative tests for 64 audited Starsector rules.csv dialogue edits."""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,io,json
from pathlib import Path
from apply_1035 import OLD_SHA,NEW_SHA,patch_bytes,sha,PRONOUN
from verify_1035 import revert,check

def must_reject(label,fn,tests):
 try:fn()
 except (AssertionError,ValueError,UnicodeDecodeError,KeyError,TypeError):tests.append(label);return
 raise AssertionError('Expected rejection: '+label)

def main(root):
 path=root/'mod/data/campaign/rules.csv';new=path.read_bytes();old=revert(new)
 assert sha(old)==OLD_SHA and sha(new)==NEW_SHA and patch_bytes(old)[0]==new
 test=check(root);assert test['gender_variables_removed']==108
 tests=[]
 must_reject('truncated input',lambda:patch_bytes(old[:-1]),tests)
 must_reject('already patched',lambda:patch_bytes(new),tests)
 must_reject('corrupt CSV header',lambda:patch_bytes(b'XXX'+old[3:]),tests)
 damaged=old.replace(b'TTmarketWeirdMods1a',b'TTmarketWeirdModsXX',1)
 must_reject('missing reviewed ID',lambda:patch_bytes(damaged,expected_hash=sha(damaged)),tests)
 damaged=old.replace(b'TTmarketWeirdMods1c',b'TTmarketWeirdMods1a',1)
 must_reject('duplicate reviewed ID',lambda:patch_bytes(damaged,expected_hash=sha(damaged)),tests)
 damaged=old.replace(b'$HeOrShe przerywa i zaczyna od nowa.',b'$HeOrShe znika i zaczyna od nowa.',1)
 must_reject('unexpected source text',lambda:patch_bytes(damaged,expected_hash=sha(damaged)),tests)
 damaged=old.replace(b'$HeOrShe przerywa i zaczyna od nowa.',b'$HeOrShe przerywa i zaczyna od nowa. $HeOrShe przerywa i zaczyna od nowa.',1)
 must_reject('ambiguous duplicate source substring',lambda:patch_bytes(damaged,expected_hash=sha(damaged)),tests)
 damaged=old.replace(b'TTmarketWeirdMods1a,',b'TTmarketWeirdMods1a,,',1)
 must_reject('incorrect CSV field structure',lambda:patch_bytes(damaged,expected_hash=sha(damaged)),tests)
 damaged=old.replace(b'TTmarketWeirdMods1a',b'\xffTmarketWeirdMods1a',1)
 must_reject('non-ASCII text in source',lambda:patch_bytes(damaged,expected_hash=sha(damaged)),tests)
 must_reject('wrong reconstructed output',lambda:revert(new.replace(b'Rozmowca urywa wypowiedz',b'Rozmowca urywa przemowe',1)),tests)
 must_reject('edited option caption in patched file',lambda:revert(new.replace(b'Pokaz kustoszowi, jak to zrobic',b'Pokaz kustoszowi jak to zrobic',1)),tests)
 # Validate options using the exact game-specific parser guard; a colon can crash the game.
 spec=importlib.util.spec_from_file_location('option_parser',root/'maintenance/check_rules_options.py')
 checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
 invalid=new.replace(b'lpp_hookCurateUpload:Pokaz kustoszowi, jak to zrobic',b'lpp_hookCurateUpload:Pokaz:DODATKOWE:kustoszowi, jak to zrobic',1)
 count,errors=checker.audit(invalid)
 assert count==7371 and errors
 tests.append('invalid colon in dialogue option is rejected')
 assert path.read_bytes()==new
 print(json.dumps({'positive_cases':3,'negative_cases':tests,'negative_count':len(tests),'dialogue_rows':64,'exact_replacements':93,'gender_variables_removed':108},indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 a=p.parse_args();main(a.worktree)
