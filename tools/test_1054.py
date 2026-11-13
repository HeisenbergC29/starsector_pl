#!/usr/bin/env python3
"""Tests negative drift and realistic runtime text composition for v1.0.54."""
from __future__ import annotations
import argparse,copy,json,hashlib,tempfile
from pathlib import Path
from apply_1054 import (OLD,NEW,readmap,make,ADDITIONS,CORRECTIONS,SIM,CODEX,
                         PHASE,PLANET,BLOCK,LEAGUE,sha)
from verify_1054 import check

def test(root):
 root=Path(root);f=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 base=readmap(f/OLD);now=readmap(f/NEW)
 mapped={(x['source_class'],x['english_literal']):x['polish_ascii_draft'] for x in now}
 tests=[]
 for count in (1,2,5,12,21):
  for cl,prefix,one,many in (
   (SIM,'%s new ','faction','factions'),
   (SIM,'%s new hull ','variant','variants'),
   (CODEX,'%s new Codex ','entry','entries')):
   words=one if count==1 else many
   txt=(mapped[(cl,prefix)]+mapped[(cl,words)]).replace('%s',str(count))
   if not txt.endswith(str(count)) or any(x in txt for x in (' new ', 'faction','variant','entry','entries','kadlubow','nowych wpisow')):
    raise AssertionError(('Mixed English or incorrect numeric suffix',cl,count,txt))
   tests.append(txt)
  p=mapped[(PLANET,"Only show planets with %s or more stable locations in the star system they're in, including locations already in use by objectives or similar.")].replace('%s',str(count))
  b=mapped[(BLOCK,'for all %s colonies in the ')].replace('%s',str(count))
  q=mapped[(LEAGUE,'Event progress value is based on the number and size of colonies under your control. Requires one size %s colony, or at least %s colonies with one being at least size %s.')].replace('%s',str(count))
  s=mapped[(PHASE,'The sensor profile of the %s top ships in your fleet is %s. The sensor strength of the top %s phase ships is %s.')].replace('%s',str(count))
  if '1 stabilnymi' in p or '1 kolonii' in b or '1 najwazniejszych okretow' in s or 'co najmniej 1 kolonii' in q:raise AssertionError('Polish singular mismatch')
  tests.extend([p,b,q,s])
 if len(tests)!=35:raise AssertionError('Number of composed samples changed')
 failures={}
 def reject(label,run):
  try:run()
  except (ValueError,KeyError,AssertionError):failures[label]='REJECTED'
  else:raise AssertionError(('Validator accepted mutation',label))
 def mutate_one(field,value):
  x=copy.deepcopy(base);x[0][field]=value;make(x)
 reject('mapping count omitted',lambda:make(base[:-1]))
 reject('duplicate base key',lambda:make(base+[base[0]]))
 key=next(i for i,x in enumerate(base) if (x['source_class'],x['english_literal']) in CORRECTIONS)
 def mutate_target(field,val):
  x=copy.deepcopy(base);x[key][field]=val;make(x)
 reject('original translated phrase mutated',lambda:mutate_target('polish_ascii_draft','BAD TRANSLATION'))
 reject('source technical class mutated',lambda:mutate_target('source_class','bogus'))
 reject('source english identifier mutated',lambda:mutate_target('english_literal','changed key'))
 reject('source status mutated',lambda:mutate_target('status','VERIFIED_UNAUTHORIZED'))
 reject('new row duplicated in baseline',lambda:make(base+[dict(source_class=SIM,english_literal='entry',polish_ascii_draft='',status='test')]))
 with tempfile.TemporaryDirectory() as td:
  tmp=Path(td)/'bad.csv';tmp.write_text('wrong,head\n1,2\n')
  reject('malformed CSV columns',lambda:readmap(tmp))
 if len(failures)!=8:raise AssertionError('Negative test inventory incomplete')
 verified=check(root)
 return {'version':'1.0.54','composed_numeric_samples':len(tests),'all_samples_ascii':all(x.isascii() for x in tests),
  'negative_mutations_rejected':len(failures),'negative_cases':failures,
  'source_map_validated':verified['api_map_sha256']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args();print(json.dumps(test(a.worktree),indent=2))
