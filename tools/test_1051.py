#!/usr/bin/env python3
"""No-op/CSV/body mutation tests for the narrowly allowed Java UI exception."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from apply_1051 import OLD,NEW,CORRECTIONS,CLASS,readmap,corrected_rows,serialize
from verify_1051 import check,sha

def run(root):
 root=Path(root);td=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 previous=readmap(td/OLD);updated=readmap(td/NEW)
 report=check(root)
 assert report['intentional_ldc_operand_changes']==2
 labels={'Aggressive':'Agresywny','Cautious':'Ostrozny','Reckless':'Brawurowy','Steady':'Opanowany'}
 pairs=[]
 for personality,localized in labels.items():
  single=updated[next(i for i,r in enumerate(updated) if r['source_class']==CLASS and r['english_literal']=='%s officers and ship commanders.')]['polish_ascii_draft']
  result=single.replace('%s',localized)
  if result!=f'Oficerowie i dowodcy okretow: {localized}.':raise ValueError(('Bad single UI label',personality,result))
  pairs.append(result)
 mixed=next(r['polish_ascii_draft'] for r in updated if r['source_class']==CLASS and r['english_literal']=='A mix of %s and %s officers and ship commanders.')
 rendered=mixed.replace('%s',labels['Aggressive'],1).replace('%s',labels['Reckless'],1)
 if rendered!='Oficerowie i dowodcy okretow: Agresywny oraz Brawurowy.':raise ValueError(('Wrong mixed localized UI',rendered))
 bad=[]
 def fail(name,fn):
  try:fn()
  except (AssertionError,ValueError,KeyError):bad.append(name)
  else:raise AssertionError(('Validator accepted tampering',name))
 chosen=next(i for i,r in enumerate(previous) if r['source_class']==CLASS and r['english_literal']=='%s officers and ship commanders.')
 def mutate(key,value):
  arr=copy.deepcopy(previous);arr[chosen][key]=value;corrected_rows(arr)
 fail('missing mapped source',lambda:corrected_rows(previous[:-1]))
 fail('duplicate source row',lambda:corrected_rows(previous+[previous[chosen]]))
 fail('altered baseline translation',lambda:mutate('polish_ascii_draft','BAD'))
 fail('status modification',lambda:mutate('status','NOT_A_REVIEW'))
 fail('lost format parameter',lambda:mutate('polish_ascii_draft','oficerow bez placeholdera'))
 fail('unknown english literal',lambda:mutate('english_literal','changed source key'))
 fail('not ASCII target',lambda:mutate('polish_ascii_draft','Ostrożny'))
 fail('missing original message',lambda:corrected_rows([x for j,x in enumerate(previous) if j!=chosen]))
 if len(bad)!=8:raise ValueError('Wrong mutation coverage')
 return {'release':'1.0.51','full_single_personality_examples':pairs,'mixed_example':rendered,
  'negative_mutations_rejected':len(bad),'mutations':bad,'other_classes_unchanged':True}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 print(json.dumps(run(p.parse_args().worktree),indent=2))
