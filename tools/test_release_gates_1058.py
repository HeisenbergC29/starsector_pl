#!/usr/bin/env python3
"""Ten fail-closed mutations of v1.1 release metadata after 1.0.58."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1058 import metadata,audit,NEW_GATE

def test(worktree:Path,gates:Path,previous:Path)->dict:
 base=json.loads(gates.read_text('utf8'));failed={}
 def pick(x,id):return next(y for y in x['gates'] if y['id']==id)
 def reject(label,fn):
  d=copy.deepcopy(base);fn(d)
  with tempfile.TemporaryDirectory() as temp:
   path=Path(temp)/'gates.json';path.write_text(json.dumps(d),encoding='utf8')
   try:metadata(path,previous)
   except (ValueError,KeyError):failed[label]='REJECTED'
   else:raise AssertionError(('Invalid release status accepted',label))
 reject('mark 1.1 ready',lambda d:pick(d,NEW_GATE).update(status='completed'))
 reject('fake Windows gameplay',lambda d:pick(d,'windows_runtime').update(native_gameplay_tested=True))
 reject('erase unreviewed JVM getters',lambda d:pick(d,'pronoun_contexts').update(unresolved_count=0))
 reject('erase API review queue',lambda d:pick(d,'draft_semantics').update(unresolved_count=0))
 reject('inflate reviewed dialogue count',lambda d:pick(d,'pronoun_contexts').update(reviewed_rules_rows_offline=556))
 reject('understate raw dynamic tokens',lambda d:pick(d,NEW_GATE).update(remaining_placeholder_occurrences=1))
 reject('allow code changes',lambda d:pick(d,NEW_GATE).update(changes_to_conditions_scripts_ids_options=1))
 reject('erase old protected IDs',lambda d:pick(d,NEW_GATE).update(protected_prior_reviewed_ids=0))
 reject('delete older gate',lambda d:d['gates'].pop(7))
 reject('duplicate a gate',lambda d:d['gates'].append(copy.deepcopy(d['gates'][0])))
 if len(failed)!=10:raise AssertionError('Incomplete release gate mutation tests')
 audit(worktree,gates,previous)
 return {'release':'1.0.58','rejected_false_completions':len(failed),'cases':failed}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',required=True,type=Path);p.add_argument('--previous',required=True,type=Path)
 a=p.parse_args();print(json.dumps(test(a.worktree,a.gates,a.previous),indent=2))
