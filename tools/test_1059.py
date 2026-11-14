#!/usr/bin/env python3
"""Synthetic negative tests for 1.0.59 class-scoped Java translation map."""
from __future__ import annotations
import argparse,copy,json
from pathlib import Path
from apply_1059 import CLASS,ADDITIONS,CORRECTION,build,sha,OLD
from apply_1054 import readmap
from verify_1059 import check,quantities

def run(root:Path):
 root=Path(root);base=readmap(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'/OLD)
 results={}
 def fail(name,cb):
  try:cb()
  except (ValueError,KeyError,AssertionError):results[name]='REJECTED'
  else:raise AssertionError(('Unsafe API mapping was accepted',name))
 def mutated(fn):
  rows=copy.deepcopy(base);fn(rows);return build(rows)
 fail('duplicate old map row',lambda:mutated(lambda a:a.append(dict(a[0]))))
 fail('wrong number of old map rows',lambda:mutated(lambda a:a.pop()))
 fail('remove required monthly template',lambda:mutated(lambda a:a.__setitem__(next(i for i,v in enumerate(a) if v['source_class']==CLASS and v['english_literal']==CORRECTION[0]),dict(a[0]))))
 fail('unreviewed old translation changed',lambda:mutated(lambda a:next(v for v in a if v['source_class']==CLASS and v['english_literal']==CORRECTION[0]).update(polish_ascii_draft='UNKNOWN')))
 fail('preinstalled class scoped label',lambda:mutated(lambda a:a.append(dict(source_class=CLASS,english_literal='Ships',polish_ascii_draft='Okrety',status='draft'))))
 fail('status changed on audited source',lambda:mutated(lambda a:next(v for v in a if v['source_class']==CLASS and v['english_literal']==CORRECTION[0]).update(status='UNREVIEWED')))
 value={**ADDITIONS,CORRECTION[0]:CORRECTION[2]}
 fail('missing unit suffix replacement',lambda:quantities({**value,'units':'units'}))
 fail('missing of connector replacement',lambda:quantities({**value,' of ':' of '}))
 fail('ungrammatical dynamic commodity declension',lambda:quantities({**value,CORRECTION[0]:'Okolo %s '}))
 fail('invalid singular quantity',lambda:quantities({**value,'unit':'jednostka'}))
 checked=check(root)
 if len(results)!=10:raise AssertionError('Missing negative cases')
 return {'release':'1.0.59','negative_mutations_rejected':len(results),'cases':results,
         'verified_quantity_variants':checked['monthly_report_quantity_renderings_checked']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args();print(json.dumps(run(a.worktree),indent=2))
