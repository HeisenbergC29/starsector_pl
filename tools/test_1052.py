#!/usr/bin/env python3
"""1.0.52: render male/female bar dialogue fragments and reject regression mutations."""
from __future__ import annotations
import argparse,copy,hashlib,json
from pathlib import Path
from apply_1052 import BASE,LUDDIC,SHIELD,ADDITIONS,CORRECTIONS,readmap,make,NEW,OLD,STATUS
from verify_1052 import check

def compose(mp,sex):
 p=lambda cl,en:mp[(cl,en)]['polish_ascii_draft']
 who='man' if sex=='male' else 'woman'
 pos='his' if sex=='male' else 'her'
 dat='him' if sex=='male' else 'her'
 subj='he' if sex=='male' else 'she'
 return {
 'bar_open':p(LUDDIC,'A ')+p(BASE,who)+p(LUDDIC,' with Pather tattoos is staring at you from across the bar ')+p(LUDDIC,'with a desperate gleam in ')+p(BASE,pos)+p(LUDDIC,' eyes.'),
 'bar_terms_option':p(LUDDIC,'Agree to ')+p(BASE,pos)+p(LUDDIC,' terms'),
 'bar_terms_response':p(LUDDIC,'You agree to the ')+p(BASE,who)+p(LUDDIC,"'s terms and make the necessary arrangements."),
 'bar_reject':p(LUDDIC,'Suggest that ')+p(BASE,subj)+p(LUDDIC,' handle ')+p(BASE,pos)+p(LUDDIC,' own problems'),
 'bar_join':p(LUDDIC,'Offer for ')+p(BASE,dat)+p(LUDDIC,' to join your fleet instead'),
 'apologize':p(SHIELD,'Offer to apologize for the misunderstanding by buying ')+p(BASE,dat)+p(SHIELD,' a drink'),
 'peaceful_exit':p(SHIELD,'Leave the old spacer to ')+p(BASE,pos)+p(SHIELD,' rest'),
 'temple':p(SHIELD,' growls back. Then laughs, and taps ')+p(BASE,pos)+p(SHIELD,' temple. '),
 'shake':p(BASE,subj)+p(SHIELD,' shakes ')+p(BASE,pos)+p(SHIELD,' head, "Captain, '),
 'voice':p(SHIELD,'attacked with no mercy. "It weren\'t pirates, nor military," here the spacer loses ')+p(BASE,pos)+p(SHIELD,' cheer at a good story. "Ludd\'s hells, I swear to you it weren\'t anything human."'),
 }

def run(root):
 root=Path(root);td=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 a=readmap(td/OLD);b=readmap(td/NEW);d={(r['source_class'],r['english_literal']):r for r in b}
 assert len(a)==5269 and len(b)==5283
 renders={sex:compose(d,sex) for sex in ('male','female')}
 for sex,part in renders.items():
  assert len(part)==10
  for key,text in part.items():
   if not text.isascii() or not text.strip() or any(x in text for x in (' her ', ' him ', ' his ', ' man ', ' woman ', ' handle ', 'to join your fleet', ' a drink', ' eyes.')):
    raise ValueError(('Unlocalized or invalid assembled UI fragment',sex,key,text))
   if '  ' in text:raise ValueError(('Double-space in constructed text',sex,key,text))
  assert part['bar_open'].startswith('Widzisz, jak '+('mezczyzna' if sex=='male' else 'kobieta'))
  assert ('w jego oczach.' if sex=='male' else 'w jej oczach.') in part['bar_open']
  assert ('Zamiast tego zaproponuj mu dolaczenie' if sex=='male' else 'Zamiast tego zaproponuj jej dolaczenie') in part['bar_join']
  assert ('stawiajac mu drinka' if sex=='male' else 'stawiajac jej drinka') in part['apologize']
  assert ('Nie zaklocaj jego odpoczynku' if sex=='male' else 'Nie zaklocaj jej odpoczynku')==part['peaceful_exit']
  assert part['bar_reject'].startswith('Zaproponuj: niech '+('on' if sex=='male' else 'ona')+' sprobuje rozwiazac sytuacje, bo to ')
  assert 'kreci glowa. Z '+('jego' if sex=='male' else 'jej')+' ust pada: "Kapitanie,' in part['shake']
  assert ('w jego glosie gasnie entuzjazm' if sex=='male' else 'w jej glosie gasnie entuzjazm') in part['voice']
 rejected={}
 def must_fail(tag,callback):
  try:callback()
  except (ValueError,KeyError,AssertionError):rejected[tag]='PASS'
  else:raise AssertionError(('Validator accepted invalid map',tag))
 bad=copy.deepcopy(a)
 idx=next(i for i,r in enumerate(bad) if (r['source_class'],r['english_literal']) in CORRECTIONS)
 def badrow(field,value):
  t=copy.deepcopy(a);t[idx][field]=value;make(t)
 must_fail('changed historical translation',lambda:badrow('polish_ascii_draft','BROKEN'))
 must_fail('changed historical status',lambda:badrow('status','VERIFIED'))
 must_fail('removed expected historical row',lambda:make(a[:-1]))
 must_fail('duplicated base map row',lambda:make(a+[a[0]]))
 must_fail('wrong source key',lambda:badrow('english_literal','altered original literal'))
 must_fail('different source class',lambda:badrow('source_class','com.fs.starfarer.invalid.Clazz'))
 must_fail('unexpected pre-existing added literal',lambda:make(a+[{'source_class':BASE,'english_literal':'her','polish_ascii_draft':'jej','status':STATUS}]))
 def badmap():
  t=copy.deepcopy(a);t[idx]['polish_ascii_draft']=t[idx]['polish_ascii_draft']+'ę';make(t)
 must_fail('unreviewed Unicode text',badmap)
 # This structural test must recognize the exact compiled map, no undocumented edits.
 check(root)
 return {'male_female_compositions':20,'contexts_each_gender':10,'negative_inventory_mutations_rejected':len(rejected),
  'negative_cases':rejected,'rendered_samples':renders,'map_source_verified':True}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--report',type=Path)
 args=p.parse_args();result=run(args.worktree)
 if args.report:args.report.write_text(json.dumps(result,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 print(json.dumps({k:v for k,v in result.items() if k!='rendered_samples'},indent=2))
