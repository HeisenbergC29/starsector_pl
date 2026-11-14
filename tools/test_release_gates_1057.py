#!/usr/bin/env python3
"""Mutation tests for strict, cumulative 1.1 release-gate accounting."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1057 import metadata,audit

def test(root:Path,gates:Path,previous:Path)->dict:
 base=json.loads(gates.read_text('utf8'));invalid={}
 def gate(obj,name):return next(x for x in obj['gates'] if x['id']==name)
 def reject(name,mutator):
  obj=copy.deepcopy(base);mutator(obj)
  with tempfile.TemporaryDirectory() as td:
   fp=Path(td)/'gates.json';fp.write_text(json.dumps(obj),encoding='utf8')
   try:metadata(fp,previous)
   except (ValueError,KeyError):invalid[name]='REJECTED'
   else:raise AssertionError(('Falsified completion accepted',name))
 reject('declare v1.1 complete',lambda x:gate(x,'rules_reflexive_1057').update(status='completed'))
 reject('falsify native Windows play',lambda x:gate(x,'windows_runtime').update(native_gameplay_tested=True))
 reject('erase unresolved API reviews',lambda x:gate(x,'draft_semantics').update(unresolved_count=0))
 reject('erase unreviewed JVM getters',lambda x:gate(x,'pronoun_contexts').update(unresolved_count=0))
 reject('inflate reviewed dialogues',lambda x:gate(x,'pronoun_contexts').update(reviewed_rules_rows_offline=434))
 reject('inflate removed tokens',lambda x:gate(x,'rules_reflexive_1057').update(remaining_placeholder_occurrences=0))
 reject('allow script mutation',lambda x:gate(x,'rules_reflexive_1057').update(changes_to_conditions_scripts_ids_options=1))
 reject('claim 1.0.56 was reviewed again',lambda x:gate(x,'rules_reflexive_1057').update(protected_prior_reviewed_ids=0))
 reject('erase historic release gate',lambda x:x['gates'].pop(3))
 reject('duplicate gate identifier',lambda x:x['gates'].append(copy.deepcopy(x['gates'][0])))
 if len(invalid)!=10:raise AssertionError('Incomplete negative gate tests')
 audit(root,gates,previous)
 return {'release':'1.0.57','false_release_completions_rejected':len(invalid),'cases':invalid}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',type=Path,required=True);p.add_argument('--previous',type=Path,required=True)
 a=p.parse_args();print(json.dumps(test(a.worktree,a.gates,a.previous),indent=2))
