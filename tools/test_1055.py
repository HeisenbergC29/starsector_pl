#!/usr/bin/env python3
"""Mutation rejects and actual composed Polish duration / dynamic operation labels."""
from __future__ import annotations
import argparse,copy,json,hashlib,tempfile,re
from pathlib import Path
from apply_1055 import ADDITIONS,REPAIRS,BLOCK,KNIGHTS,GENERIC,OLD,NEW,plan
from apply_1054 import readmap,encode
from verify_1055 import check

def test(root):
 root=Path(root);tr=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 old=readmap(tr/OLD);new=readmap(tr/NEW)
 keys={(r['source_class'],r['english_literal']):r for r in new}
 tested=[]
 for cl in (BLOCK,KNIGHTS):
  for count in (1,2,5,12,21):
   word=keys[(cl,'day' if count==1 else 'days')]['polish_ascii_draft']
   for ongoing in (False,True):
    suffix=keys[(cl,'more ')]['polish_ascii_draft'] if ongoing else ''
    prefix=keys[(cl,' will last for approximately %s ' if cl==BLOCK else 'The operation will last for approximately %s ')]['polish_ascii_draft']
    phrase=prefix.replace('%s',str(count)) + suffix+word
    if phrase.count(str(count))!=1 or 'days' in phrase or 'more ' in phrase or '  ' in phrase or re.search(r'\b(?:1 dni|2 dzien)\b',phrase):
     raise ValueError(('Unlocalized / ungrammatical duration',cl,count,ongoing,phrase))
    if not phrase.strip().endswith('dzien' if count==1 else 'dni'):
     raise ValueError(('Missing final unit',phrase))
    tested.append((cl,count,ongoing,phrase))
 nounexamples=['blokada','rajdy','operacja floty','atak']
 composed=[]
 for noun in nounexamples:
  p=keys[(GENERIC,'There are no colonies for the ')]['polish_ascii_draft']+noun+keys[(GENERIC,' to target in the system.')]['polish_ascii_draft']
  if 'do zaatakowania' in p or p.count('"')!=2 or not p.endswith('".') or noun not in p:
   raise ValueError(('No-target sentence malformed',noun,p))
  composed.append(p)
 rejected={}
 def reject(title,fn):
  try:fn()
  except (ValueError,AssertionError,KeyError):rejected[title]='REJECTED'
  else:raise AssertionError(('Invalid source was accepted',title))
 def mutate(match,field,change):
  a=copy.deepcopy(old);r=next(x for x in a if (x['source_class'],x['english_literal'])==match)
  r[field]=change(r[field]);plan(a)
 one=next(iter(REPAIRS))
 reject('old Polish translation changed',lambda:mutate(one,'polish_ascii_draft',lambda v:v+'X'))
 reject('wrong source status for edited fragment',lambda:mutate(one,'status',lambda v:'VERIFIED_ALREADY'))
 reject('removed original row',lambda:plan(old[:-1]))
 reject('duplicate English/source-class row',lambda:plan(old+[old[0]]))
 reject('added new literal to previous baseline',lambda:plan(old+[dict(source_class=BLOCK,english_literal='day',polish_ascii_draft='fake',status='draft')]))
 reject('duplicate correction key',lambda:plan(old+[next(x for x in old if (x['source_class'],x['english_literal'])==one)]))
 # Byte-exact whole-map tampering must be refused by independent verifier.
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);target=d/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations';target.mkdir(parents=True)
  (target/OLD).write_bytes((tr/OLD).read_bytes());(target/NEW).write_bytes((tr/NEW).read_bytes()+b'!')
  reject('target SHA modified',lambda:check(d))
 if len(tested)!=20 or len(composed)!=4 or len(rejected)!=7:raise AssertionError('Test coverage changed')
 check(root)
 return {'release':'1.0.55','duration_compositions':len(tested),'gender_neutral_count_1_2_5_12_21':True,
  'no_target_dynamic_noun_compositions':len(composed),'negative_mutations_rejected':len(rejected),'cases':rejected}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);args=p.parse_args()
 print(json.dumps(test(args.worktree),indent=2))
