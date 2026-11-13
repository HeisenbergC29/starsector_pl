#!/usr/bin/env python3
"""1.0.49 negative tests: source-map integrity, class-scoped suffix, numeric grammatical rendering."""
from __future__ import annotations
import argparse,copy,json,hashlib,tempfile
from pathlib import Path
from apply_1049 import readmap,plan,OLD,NEW,PLAN_PATH,SALVOR
from verify_1049 import check

def test(root,previous=None):
 root=Path(root);t=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 before=readmap(t/OLD);after=readmap(t/NEW)
 edits,suffix,items=plan(before)
 render=0
 for key,fix in edits.items():
  for n in ('1','2','5'):
   text=fix['new_polish'].replace('%s',n)
   if any(bad in text for bad in ('1 cykli','2 cykli','1 porzucony','1 niezbadane','1 jednostke','1 zolnierzy','1 macierzy','2 dodatkowy zaklad',' ls ','jedn..','dn..')):
    raise ValueError(('Non-neutral rendering',key,n,text))
   render+=1
 salvors=[obj for key,obj in edits.items() if key[0]==SALVOR]
 if len(salvors)!=5 or suffix['new_polish']!='':raise ValueError('Missing complete salvor noun/suffix review')
 for i in ('1','2','5'):
  for item in salvors:
   text=item['new_polish'].replace('%s',i)+suffix['new_polish']
   if not text.endswith(i) or any(e in text for e in ('okrets','instalacjas','zrodlos','szczatkow s','ruin s')):
    raise ValueError(('Salvage suffix composing incorrectly',i,text))
   render+=1
 rejected={}
 def must_reject(name,run):
  try:run()
  except (ValueError,KeyError,AssertionError):rejected[name]=True
  else:raise AssertionError('Mutation was not rejected: '+name)
 def mutate_rows(i,key,value):
  x=copy.deepcopy(before);x[i][key]=value;plan(x)
 first=next(i for i,row in enumerate(before) if (row['source_class'],row['english_literal']) in edits)
 must_reject('wrong_previous_translation',lambda:mutate_rows(first,'polish_ascii_draft','NOT THE APPROVED ORIGINAL'))
 must_reject('wrong_source_class',lambda:mutate_rows(first,'source_class','com.fs.starfarer.fake.Class'))
 must_reject('duplicate_source_key',lambda:plan(before+[before[first]]))
 must_reject('missing_map_entry',lambda:plan(before[:-1]))
 must_reject('technical_status_changed',lambda:mutate_rows(first,'status','FAKE_APPROVAL'))
 p=json.loads(PLAN_PATH.read_text('utf8'))
 def with_plan(name,mod):
  obj=copy.deepcopy(p);mod(obj)
  with tempfile.TemporaryDirectory() as d:
   temp=Path(d)/'bad.json';temp.write_text(json.dumps(obj))
   must_reject(name,lambda:plan(before,temp))
 with_plan('bad_unicode_output',lambda v:v['changes'][0].__setitem__('new_polish','Zly tekst ę'))
 with_plan('unsafe_plural_suffix',lambda v:v['changes'][-1].__setitem__('new_polish','y'))
 with_plan('lost_numeric_placeholder',lambda v:v['changes'][0].__setitem__('new_polish','Brak numeru'))
 verified=check(root,previous)
 if render!=54 or len(rejected)!=8 or verified['new_map_rows']!=5261:raise ValueError('Incomplete negative test suite')
 return {'numeric_and_suffix_renderings':render,'mutations_rejected':len(rejected),
         'negative_cases':sorted(rejected),'class_specific_empty_suffix_verified':True}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--prior-zip',type=Path)
 a=p.parse_args();print(json.dumps(test(a.worktree,a.prior_zip),indent=2))
