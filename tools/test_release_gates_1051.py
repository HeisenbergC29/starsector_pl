#!/usr/bin/env python3
"""Malicious/incorrect 1.1 completion flags must remain rejected."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1051 import audit

def test(root,gates,previous,ledger):
 original=json.loads(Path(gates).read_text('utf8'));done=[]
 def attempt(name,func):
  obj=copy.deepcopy(original);func(obj);tmp=None
  with tempfile.TemporaryDirectory() as d:
   tmp=Path(d)/'gates.json';tmp.write_text(json.dumps(obj))
   try:audit(root,tmp,previous,ledger)
   except (ValueError,KeyError):done.append(name)
   else:raise AssertionError(('Unsafe release gate accepted',name))
 def field(id,key,val):
  return lambda x:next(g for g in x['gates'] if g['id']==id).__setitem__(key,val)
 attempt('premature_windows',field('windows_runtime','native_gameplay_tested',True))
 attempt('premature_pronouns',field('pronoun_contexts','unresolved_count',0))
 attempt('shared_her_falsely_resolved',field('pronoun_contexts','shared_her_conflict_open',False))
 attempt('unreviewed_semantics_zero',field('draft_semantics','unresolved_count',0))
 attempt('historical_review_count_exaggerated',field('draft_semantics','reviewed_offline',3658))
 attempt('bad_java_exception_count',field('personality_ui_1051','jvm_ldc_operand_changes',3))
 attempt('technical_ids_claimed_modified',field('personality_ui_1051','technical_identity_constants_preserved',False))
 attempt('pretend_personality_ui_checked_windows',field('personality_ui_1051','pending_windows_ui',0))
 attempt('incorrect_game_release_ready',field('personality_ui_1051','status','completed'))
 attempt('previous_gate_1050_missing',lambda x:x['gates'].__setitem__(slice(None),[g for g in x['gates'] if g['id']!='api_time_fragments_1050']))
 if len(done)!=10:raise AssertionError('Incorrect negative release gate test count')
 return {'release':'1.0.51','release_gate_mutations_rejected':len(done),'cases':done}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--gates',type=Path,required=True);p.add_argument('--previous',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True)
 a=p.parse_args();print(json.dumps(test(a.worktree,a.gates,a.previous,a.ledger),indent=2))
