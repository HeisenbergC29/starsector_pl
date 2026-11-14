#!/usr/bin/env python3
"""Exercise fail-closed 1.1 release-gate invariants with ten invalid variants."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1056 import metadata,audit

def tests(root,gates,prior)->dict:
 base=json.loads(Path(gates).read_text('utf8'));checked={}
 def gate(d,name):return next(x for x in d['gates'] if x['id']==name)
 def mutation(name,modify):
  d=copy.deepcopy(base);modify(d)
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'gates.json';p.write_text(json.dumps(d),encoding='utf8')
   try:metadata(p,prior)
   except (ValueError,KeyError):checked[name]='REJECTED'
   else:raise AssertionError(('Fake completion accepted',name))
 mutation('mark all work completed',lambda d:gate(d,'rules_gender_neutral_1056').update(status='completed'))
 mutation('invent Windows gameplay tests',lambda d:gate(d,'windows_runtime').update(native_gameplay_tested=True))
 mutation('fake getter review completion',lambda d:gate(d,'pronoun_contexts').update(unresolved_count=0))
 mutation('fake all API reviewed',lambda d:gate(d,'draft_semantics').update(reviewed_offline=3658))
 mutation('invent fixed 111 rows',lambda d:gate(d,'rules_gender_neutral_1056').update(corrected_rules_rows=111))
 mutation('invent removal 1000 placeholders',lambda d:gate(d,'rules_gender_neutral_1056').update(remaining_placeholder_occurrences=1275))
 mutation('pretend conditions/scripts changed',lambda d:gate(d,'rules_gender_neutral_1056').update(changes_to_conditions_scripts_ids_options=1))
 mutation('inflate prior dialogue review',lambda d:gate(d,'pronoun_contexts').update(reviewed_rules_rows_offline=400))
 mutation('drop old JVM validation gate',lambda d:d['gates'].pop(4))
 mutation('clone gate ID',lambda d:d['gates'].append(copy.deepcopy(d['gates'][0])))
 if len(checked)!=10:raise AssertionError('Missing invalid release tests')
 audit(root,gates,prior)
 return {'release':'1.0.56','false_target_1_1_completion_states_rejected':len(checked),'details':checked}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',required=True,type=Path);p.add_argument('--previous',required=True,type=Path)
 a=p.parse_args();print(json.dumps(tests(a.worktree,a.gates,a.previous),indent=2))
