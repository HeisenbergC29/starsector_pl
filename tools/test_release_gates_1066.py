#!/usr/bin/env python3
"""Reject fabricated 1.1 milestones, restored game tests, or double counted API rows."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1066 import metadata,audit,GATE

def test(root:Path,current:Path,previous:Path,prior:Path,semantic:Path)->dict:
 baseline=json.loads(Path(current).read_text('utf8'));metadata(current,previous);rejected=[]
 def item(d,key):return next(x for x in d['gates'] if x['id']==key)
 def reject(label,mutate):
  candidate=copy.deepcopy(baseline);mutate(candidate)
  with tempfile.TemporaryDirectory() as tmp:
   q=Path(tmp)/'gates.json';q.write_text(json.dumps(candidate)+'\n',encoding='utf8')
   try:metadata(q,previous)
   except (ValueError,KeyError,TypeError):rejected.append(label)
   else:raise AssertionError(('Invalid release gate accepted',label))
 reject('claim source translation complete',lambda d:item(d,'text_completeness').update(status='completed'))
 reject('inflate total historical reviews',lambda d:item(d,'draft_semantics').update(reviewed_offline=3658))
 reject('erase remaining API debt',lambda d:item(d,'draft_semantics').update(unresolved_count=0))
 reject('recount already reviewed BaseIndustry strings',lambda d:item(d,GATE).update(new_historical_reviews=161))
 reject('fabricated JVM string use count',lambda d:item(d,GATE).update(verified_original_jvm_ldc_calls=1000))
 reject('fabricated new UI additions',lambda d:item(d,GATE).update(added_literals=99))
 reject('fabricated executable JVM instruction changes',lambda d:item(d,GATE).update(new_jvm_executable_instructions=1))
 reject('fabricated native gameplay testing',lambda d:item(d,'windows_runtime').update(native_gameplay_tested=True))
 reject('reinstate game testing as prerelease prerequisite',lambda d:item(d,'windows_runtime').update(required_before_1_1=True))
 reject('premature gameplay test completion',lambda d:d['test_policy'].update(post_release_gameplay_status='passed'))
 reject('disable pre-release safety checks',lambda d:d['test_policy'].update(pre_release_checks=[]))
 reject('delete historical release gate',lambda d:d['gates'].pop(0))
 reject('modify earlier reviewed milestone',lambda d:item(d,'marketcmd_raid_bombardment_1065').update(new_historical_reviews=104))
 reject('hide unresolved dynamic getters',lambda d:item(d,'pronoun_contexts').update(unresolved_count=0))
 result=audit(root,current,previous,prior,semantic)
 if len(rejected)!=14 or result['history_remaining']!=2927:raise ValueError('Incomplete negative gate coverage')
 return {'release':'1.0.66','invalid_release_gate_states_rejected':len(rejected),
  'in_game_testing_only_after_1_1':True,'cases':rejected}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--gates',type=Path,required=True);p.add_argument('--previous',type=Path,required=True)
 p.add_argument('--prior-semantic',type=Path,required=True);p.add_argument('--semantic',type=Path,required=True)
 a=p.parse_args();print(json.dumps(test(a.worktree,a.gates,a.previous,a.prior_semantic,a.semantic),indent=2))
