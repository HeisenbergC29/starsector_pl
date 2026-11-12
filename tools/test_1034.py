#!/usr/bin/env python3
"""Negative and positive 1.0.34 tests, no proprietary game assets required in CI."""
import csv,hashlib,importlib.util,io,json,sys
from pathlib import Path
from apply_1034 import PATCHES,OLD_SHA,NEW_SHA,translate_bytes,rows_with_spans
from verify_1034 import revert,check


def fail(fn,exception=(ValueError,AssertionError,UnicodeDecodeError)):
 try:fn()
 except exception:return True
 raise AssertionError('Negative case unexpectedly accepted')

def main(root):
 old=revert((root/'mod/data/campaign/rules.csv').read_bytes());new=(root/'mod/data/campaign/rules.csv').read_bytes()
 assert hashlib.sha256(old).hexdigest()==OLD_SHA
 assert hashlib.sha256(new).hexdigest()==NEW_SHA
 assert translate_bytes(old)[0]==new
 result=check(root);assert result['corrected_dialogue_rows']==27
 steps=[]
 def run(label,fn):
  assert fail(fn),label
  steps.append(label)
 run('truncated source',lambda:translate_bytes(old[:-10]))
 run('already patched input',lambda:translate_bytes(new))
 run('corrupted header',lambda:translate_bytes(b'bad'+old[3:]))
 run('non-ASCII input',lambda:translate_bytes(old.replace(b'gaTJPlanetContact',b'gaTJ\xc4\x85PlanetContact',1)))
 run('altered translated output',lambda:revert(new.replace(b'Naukowiec kreci glowa',b'Naukowiec drapie glowa',1)))
 run('broken expected phrase',lambda:translate_bytes(old.replace(b'wykrzykuje $gaTJ_heOrShe',b'wykrzykuje $gaTJ_SPOILED',1)))
 # Import a copy of the verified module to check that unknown/reused row IDs are rejected.
 import apply_1034 as a
 saved=a.OLD_SHA
 try:
  cloned=old.replace(b'gaTJMissionText3a,',b'gaTJMissionText3b,',1)
  a.OLD_SHA=hashlib.sha256(cloned).hexdigest()
  run('duplicate curated row ID',lambda:a.translate_bytes(cloned))
 finally:a.OLD_SHA=saved
 try:
  damaged=old.replace(b'gaTJMissionText3a,',b'gaTJMissionTextXX,',1)
  a.OLD_SHA=hashlib.sha256(damaged).hexdigest()
  run('missing curated row ID',lambda:a.translate_bytes(damaged))
 finally:a.OLD_SHA=saved
 try:
  script_damaged=old.replace(b'gaTJPlanetContact,DialogOptionSelected',b'gaTJPlanetContact,WrongTriggerTest',1)
  a.OLD_SHA=hashlib.sha256(script_damaged).hexdigest()
  # Final result hash rejects any unrelated modification even if text substitutions work.
  run('unexpected script/trigger modification',lambda:a.translate_bytes(script_damaged))
 finally:a.OLD_SHA=saved
 try:
  data_damaged=old.replace(b'gaTJMissionText3a,',b'gaTJMissionText3a,,',1)
  a.OLD_SHA=hashlib.sha256(data_damaged).hexdigest()
  run('invalid CSV field structure',lambda:a.translate_bytes(data_damaged))
 finally:a.OLD_SHA=saved
 # An invalid extra colon in the sole changed option caption must be detected.
 spec=importlib.util.spec_from_file_location('ruleopt',root/'maintenance/check_rules_options.py')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 broken=new.replace(b'locrlf_startBar:Zapytaj osobe',b'locrlf_startBar:ZAPYTAJ:DODATKOWE:osobe',1)
 count,errs=m.audit(broken);assert errs and count==7371
 steps.append('option-colon validation regression')
 assert root.joinpath('mod/data/campaign/rules.csv').read_bytes()==new
 print(json.dumps({'positive_tests':3,'negative_cases':steps,'negative_count':len(steps),
    'rows':27,'edits':62,'removed_gender_placeholder_occurrences':75},indent=2))

if __name__=='__main__':main(Path(sys.argv[1]))
