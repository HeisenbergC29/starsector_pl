#!/usr/bin/env python3
"""Adversarial test: regressions or unrelated edits to 1.0.42 map must fail closed."""
from __future__ import annotations
import argparse,copy,json
from pathlib import Path
from apply_1042 import readmap
from verify_1042 import verify_delta

def run(root):
 td=Path(root)/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 a=readmap(td/'TLUMACZENIA_JAR_1041.csv');b=readmap(td/'TLUMACZENIA_JAR_1042.csv')
 out=verify_delta(a,b)
 modified=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
 untouched=[i for i,(x,y) in enumerate(zip(a,b)) if x==y]
 assert len(modified)==15 and len(untouched)==5242
 passes=[]
 def check(name,change):
  aa=copy.deepcopy(a);bb=copy.deepcopy(b);change(aa,bb)
  try:verify_delta(aa,bb)
  except (AssertionError,ValueError,KeyError):passes.append(name);return
  raise AssertionError('Tamper accepted: '+name)
 k,j=modified[:2];u=untouched[0]
 check('remove approved row',lambda a,b:b.pop(k))
 check('duplicate an approved row',lambda a,b:b.insert(k,copy.deepcopy(b[k])))
 check('restore invalid double period',lambda a,b:b[k].__setitem__('polish_ascii_draft',a[k]['polish_ascii_draft']))
 check('replace period with exclamation mark',lambda a,b:b[k].__setitem__('polish_ascii_draft',b[k]['polish_ascii_draft']+'!'))
 check('double period in an unrelated string',lambda a,b:b[u].__setitem__('polish_ascii_draft',b[u]['polish_ascii_draft']+'..'))
 check('change unrelated translation',lambda a,b:b[u].__setitem__('polish_ascii_draft',b[u]['polish_ascii_draft']+' test'))
 check('change source English',lambda a,b:b[k].__setitem__('english_literal','WRONG'))
 check('change source class',lambda a,b:b[k].__setitem__('source_class','wrong.Class'))
 check('falsify approved status',lambda a,b:b[k].__setitem__('status','VERIFIED_WINDOWS'))
 check('introduce Polish diacritic',lambda a,b:b[k].__setitem__('polish_ascii_draft','błędne'))
 check('baseline translated text tampered',lambda a,b:a[k].__setitem__('polish_ascii_draft','modified'))
 check('baseline English text tampered',lambda a,b:a[k].__setitem__('english_literal','modified'))
 check('baseline status tampered',lambda a,b:a[k].__setitem__('status','FAKE'))
 check('swap corrected text between classes',lambda a,b:b[k].__setitem__('polish_ascii_draft',b[j]['polish_ascii_draft']))
 assert len(passes)==14
 return {'positive':'PASS','negative_cases_passed':len(passes),'negative_cases':passes,'exact_delta':out}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args();print(json.dumps(run(a.worktree),indent=2))
