#!/usr/bin/env python3
"""Fail-closed adversarial regressions for trade/procurement UI mapping 1.0.60."""
from __future__ import annotations
import argparse,copy,json
from pathlib import Path
from apply_1060 import TRADE,PROCURE,ADDITIONS,REPAIRS,STATUS,build
from apply_1054 import readmap
from verify_1060 import check,composed_texts

def tests(root:Path)->dict:
 root=Path(root)
 src=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1059.csv'
 original=readmap(src);expected=build(original)
 kmap={(r['source_class'],r['english_literal']):r['polish_ascii_draft'] for r in expected}
 valid=composed_texts(kmap)
 bad={}
 def reject(name,callback):
  try:callback()
  except (ValueError,KeyError,AssertionError):bad[name]='REJECTED'
  else:raise AssertionError(('Invalid map accepted',name))
 def damage(updater):
  rows=copy.deepcopy(original);updater(rows);build(rows)
 reject('duplicate source map row',lambda:damage(lambda rows:rows.append(copy.deepcopy(rows[0]))))
 reject('missing baseline entry',lambda:damage(lambda rows:rows.pop()))
 reject('old grammar changed without review',lambda:damage(lambda rows:next(r for r in rows if (r['source_class'],r['english_literal']) in REPAIRS).update(polish_ascii_draft='FAKE')))
 reject('previous status falsely marked verified',lambda:damage(lambda rows:next(r for r in rows if (r['source_class'],r['english_literal']) in REPAIRS).update(status='VERIFIED')))
 reject('new literal already mapped',lambda:damage(lambda rows:rows.append({'source_class':TRADE,'english_literal':'goods','polish_ascii_draft':'towary','status':'DRAFT'})))
 def invalid(mod):
  current=dict(kmap);mod(current);composed_texts(current)
 reject('untranslated goods category',lambda:invalid(lambda d:d.update({(TRADE,'goods'):'goods'})))
 reject('untranslated materiel category',lambda:invalid(lambda d:d.update({(TRADE,'materiel'):'materiel'})))
 reject('faulty large-cargo grammar',lambda:invalid(lambda d:d.update({(TRADE,"It's noteworthy because it's carrying a large quantity of "):'To warte uwagi, bo przewozi duza ilosc '})))
 reject('faulty large valuable grammar',lambda:invalid(lambda d:d.update({(TRADE,"It's noteworthy because it's carrying a large quantity of valuable "):'To warte uwagi, bo przewozi duza ilosc cennych '})))
 reject('untranslated route',lambda:invalid(lambda d:d.update({(TRADE,' to '):' to '})))
 reject('untranslated faction header',lambda:invalid(lambda d:d.update({(PROCURE,'Faction: '):'Faction: '})))
 result=check(root)
 assert len(bad)==11
 return {'release':'1.0.60','negative_cases_rejected':len(bad),'invalid_variants':bad,
  'valid_rendered_sentences':valid['total'],'unchanged_data_files':result['unchanged_data_files']}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args()
 print(json.dumps(tests(a.worktree),indent=2))
