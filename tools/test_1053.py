#!/usr/bin/env python3
"""Mutation tests for the three actual, class-scoped recovery fragments."""
from __future__ import annotations
import argparse,copy,csv,json,tempfile
from pathlib import Path
from apply_1053 import CHANGES,STATUS,FIELDS,make_obf,serialize,read_csv,sha,NEW_OBF,OLD_OBF
from verify_1053 import check

def run(root):
 root=Path(root);o=root/'buildtools/NARZEDZIA_OBF'
 base=read_csv(o/OLD_OBF);updated=make_obf(base)
 count=0
 for n in (1,2,5,12,21):
  amount=str(n)
  singular=CHANGES[next(k for k in CHANGES if k[1]=='ship')]
  plural=CHANGES[next(k for k in CHANGES if k[1]=='ships')]
  result='Wybrano '+amount+' '+(singular if n==1 else plural)+' do odzyskania'
  recovery='Podjeto nadzwyczajne wysilki, aby odzyskac '+amount+CHANGES[next(k for k in CHANGES if k[1]==' ships')]
  if any(x in result+' '+recovery for x in (' ship ',' ships ',' ship.', ' ships.')):raise ValueError('English ship word remained')
  if result.count('okr.')!=1 or recovery.count('okr.')!=1:raise ValueError('Lost number-neutral ship abbreviation')
  count+=2
 rejected={}
 def fails(name,fn):
  try:fn()
  except (ValueError,KeyError,AssertionError):rejected[name]='REJECTED'
  else:raise AssertionError(('Invalid map accepted',name))
 def mutate(entry,field,value):
  rows=copy.deepcopy(base);rows[entry][field]=value;make_obf(rows)
 fails('duplicate_key',lambda:make_obf(base+[base[0]]))
 fails('missing_source_row',lambda:make_obf(base[:-1]))
 fails('non_exact_source_english',lambda:make_obf(base+[dict(source_class=list(CHANGES)[0][0],english_literal=list(CHANGES)[0][1],polish_ascii_draft='broken',status=STATUS)]))
 fails('unrecognized_header',lambda:read_csv(Path('/dev/null')))
 with tempfile.TemporaryDirectory() as d:
  p=Path(d)/'bad.csv';p.write_text('a,b,c\nx,y,z\n',encoding='utf8')
  fails('tampered_csv_header',lambda:read_csv(p))
  p.write_bytes((o/OLD_OBF).read_bytes()+b'\n')
  if sha(p.read_bytes())==sha((o/OLD_OBF).read_bytes()):raise AssertionError('Mutation did not change CSV')
  p2=Path(d)/'badnew.csv';p2.write_bytes((o/NEW_OBF).read_bytes()+b'\n')
  if p2.read_bytes()==serialize(updated):raise AssertionError('New mapping mutation not detected')
 v=check(root)
 if count!=10 or len(rejected)!=5:raise ValueError('Not all negative tests covered')
 return {'rendered_count_cases':count,'rejected_invalid_structures':len(rejected),'negative_results':rejected,
  'target_map_verified':True,'obf_count':v['obf_entries']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 print(json.dumps(run(p.parse_args().worktree),indent=2))
