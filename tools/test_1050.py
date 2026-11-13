#!/usr/bin/env python3
"""Test 1.0.50 render-safe time fragments and reject mutated API mappings."""
from __future__ import annotations
import argparse,copy,csv,json,tempfile
from pathlib import Path
from apply_1050 import OLD,NEW,CHANGES,CLASS,STATUS,plan,readmap,serialize
from verify_1050 import check

def run(root):
 root=Path(root);folder=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 prev=readmap(folder/OLD);latest=readmap(folder/NEW)
 new={r['english_literal']:r['polish_ascii_draft'] for r in latest[5261:]}
 if new!=CHANGES:raise ValueError('Dates no longer match approved grammatical plan')
 # Polish ASCII samples from real JVM compositional sequence:
 # BaseIntelPlugin uses: [label + number + space + noun] + (' and ' + next number + unit) + ' ago.'
 samples={'1 day':'1 '+new['day'],'2 days':'2 '+new['days'],'5 days':'5 '+new['days'],
 '1 month':'1 '+new['month'],'2 months':'2 '+new['months'],'5 months':'5 '+new['months'],
 '1 cycle':'1 '+new['cycle'],'2 cycles':'2 '+new['cycles'],'5 cycles':'5 '+new['cycles']}
 composed=[
  'Dodano wpis do dziennika '+samples['1 day']+new[' ago.'],
  'Dodano wpis do dziennika '+samples['2 months']+new[' and ']+samples['1 day']+new[' ago.'],
  'Dodano wpis do dziennika '+samples['1 cycle']+new[' and ']+samples['5 months']+new[' ago.'],
 ]
 for s in composed:
  if ' and ' in s or ' ago' in s or 'days' in s or 'month' in s or 'cycle' in s or 'day' in s or not s.isascii():raise ValueError('Untranslated composed timestamp')
 prefix=next(x['polish_ascii_draft'] for x in latest if x['source_class'].endswith('PromoteOfficerIntel') and x['english_literal']=='This opportunity will be available for %s more ')
 officer=[prefix.replace('%s',str(n))+new['day' if n==1 else 'days']+'.' for n in (1,2,5)]
 if any('..' in x or 'day' in x for x in officer):raise ValueError('Officer promotion tooltip grammar broken')
 rejected=[]
 def must_reject(name,fun):
  try:fun()
  except (ValueError,KeyError,AssertionError):rejected.append(name)
  else:raise AssertionError('Invalid mapping accepted: '+name)
 def changed(k,v):
  a=copy.deepcopy(prev);a[k]=v;return plan(a)
 must_reject('duplicate_prior_row',lambda:plan(prev+[prev[0]]))
 must_reject('lost_prior_row',lambda:plan(prev[:-1]))
 must_reject('existing_new_duration_key',lambda:plan(prev+[{'source_class':CLASS,'english_literal':'day','polish_ascii_draft':'day','status':STATUS}]))
 must_reject('wrong_source_field',lambda:plan(prev+[{'source_class':CLASS,'english_literal':'days','polish_ascii_draft':'dni','status':STATUS}]))
 with tempfile.TemporaryDirectory() as d:
  p=Path(d);sub=p/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations';sub.mkdir(parents=True)
  (sub/OLD).write_bytes((folder/OLD).read_bytes());(sub/NEW).write_bytes((folder/NEW).read_bytes()+b'\n')
  must_reject('target_map_sha_changed',lambda:check(p))
  (sub/NEW).write_bytes((folder/NEW).read_bytes())
  (sub/OLD).write_bytes((folder/OLD).read_bytes()+b' ')
  must_reject('previous_map_sha_changed',lambda:check(p))
  (sub/OLD).write_bytes((folder/OLD).read_bytes())
  # Original map is intact; missing release metadata is not allowed.
  must_reject('missing_metadata',lambda:check(p))
 with tempfile.TemporaryDirectory() as d:
  src=Path(d)/'fake.csv';src.write_text('id,text\nX,Y\n')
  must_reject('invalid_mapping_columns',lambda:readmap(src))
 result=check(root)
 if len(rejected)!=8:raise ValueError('Incomplete mutation tests')
 return {'release':'1.0.50','numeric_unit_render_examples':len(samples),'composed_timestamps_verified':len(composed),
  'officer_promotion_tooltip_examples':len(officer),'negative_mutations_rejected':len(rejected),
  'negative_cases':rejected,'data_preserved':result['unchanged_game_data_files']==870}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 a=p.parse_args();print(json.dumps(run(a.worktree),indent=2))
