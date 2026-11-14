#!/usr/bin/env python3
"""1.0.63 immutable text-only/JVM evidence and dynamically assembled UI check."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from apply_1063 import CLASS,OLD,NEW,BASE_SHA,REPAIRS,RELEASE_SUFFIX,build,sha
from apply_1054 import readmap,encode,once
from build_review_1063 import check as check_review
NEW_MAP_SHA='5443294fa1cdf96b21fb7bba3e5a92b96f8f1b6cec6807203dd7e3e74e1d58fc'
OLD_GO_SHA='8e91220d9fd52d6c6b1a27d278706dcb911f1b589837ac62a89d843e7c8e3dd0'
NEW_GO_SHA='7261820a172e3a0fa7131cdad5c6d8ff825f5ae2485a0f7c09489a00ad32d292'
REVIEW_SHA='3376a77205591dbe2b5d3ca9e8789b8953c78633e4fad902058c7d7a1725c82d'
JVM_SHA='05ea6b7f9351199434ce668beca278402874674fcf0d6ae2fd074dabdbd74b56'
DATA_SHA='feb6e159ae8d6aa6622b3dd5e8414b425082b930ee6c739baddb0091127fb370'
RULES_SHA='4fcf72e3aad0a0c72bac3bea021a311b36f12c4d201d4dcf9b9c7edf2eeb0e04'

def render(t:dict[str,str])->dict:
 if t['Colony threats']!='Colony threats':raise ValueError('Technical Set.add category cannot be translated')
 get=lambda key:t[key]
 # Exact JVM compositions, preserving the dynamically injected name without case inflection.
 names=('uklad Corvus','Kumari Kandam','Eos Exodus','Aztlan')
 industries=('Rafineria','Skladowisko','Produkcja paliwa','Rolnictwo')
 markets=('Chicomoztoc','Jangala','Asharu','Kanta')
 duration=[(1,'dzien'),(2,'dni'),(5,'dni'),(21,'dni'),(100,'dni')]
 cases=[]
 def store(s,category):
  if not isinstance(s,str) or '  ' in s or ' . ' in s or any(en in s for en in ('operations for','planetbuster','The Pather','has smuggled','Colony threats','%s','.Jesli')):
   raise ValueError(('Bad dynamic Polish composition',category,s))
  cases.append({'category':category,'display_text':s})
 for system in names:
  s=get('The Pather base at the ')+system+get(' is providing support to these cells.')
  if not s.startswith('Baza Sciezki Ludda (lokalizacja: ') or not s.endswith(') wspiera te komorki.'):
   raise ValueError(('Base support text malformed',s))
  store(s,'support_base')
 for industry in industries:
  a=get('An attempted act of sabotage against ')+industry+get(' operations was averted by the local security forces.')
  if not a.startswith('Lokalne sluzby bezpieczenstwa') or not a.endswith('Cel: '+industry+'.'):
   raise ValueError(('Averted industrial sabotage malformed',a))
  store(a,'industrial_sabotage_averted')
  for n,unit in duration:
   suf=get(' operations disrupted for %s ')
   phrase=industry+suf.replace('%s',str(n))+unit
   if phrase.count(str(n))!=1 or phrase.count(unit)!=1 or not phrase.startswith(industry+': zaklocenie dzialalnosci na '):
    raise ValueError(('Bullet duration malformed',phrase))
   store(phrase,'bullet_disruption_duration')
   prefix=get('The Pather cells have conducted a successful act of sabotage, disrupting ')
   raw=prefix+industry+get(' operations for %s ')+unit+'.'
   if raw.count('%s')!=1:raise ValueError('Game highlight parameter lost')
   phrase=raw.replace('%s',str(n))
   if not phrase.endswith('Cel: '+industry+'. Zaklocenie potrwa '+str(n)+' '+unit+'.'):
    raise ValueError(('Successful sabotage composition malformed',phrase))
   store(phrase,'sabotage_duration')
 for name in markets:
  head=get('The Pather cells have smuggled a planetbuster onto ')+name
  completed=head+get(' and detonated it. The colony has been effectively destroyed.')
  if not completed.endswith('Cel: '+name+'. Nastepnie zdetonowali ladunek, praktycznie niszczac kolonie.'):
   raise ValueError(('Detonation text malformed',completed))
  store(completed,'planetbuster_detonation')
  stopped=head+get(', but the local security forces were able to locate and disarm it, thereby ')+get('saving the colony.')
  if not stopped.endswith('Cel: '+name+'. Lokalne sluzby bezpieczenstwa odnalazly i rozbroily ladunek, ratujac kolonie.'):
   raise ValueError(('Planetbuster defused text malformed',stopped))
  store(stopped,'planetbuster_defused')
  warning=get('There are indications that the Pather cells are preparing to sneak a planetbuster onto ')+name+'.'+get('If they succeed, the colony will effectively be destroyed.')
  if not warning.endswith('Cel: '+name+'. Jesli plan sie powiedzie, kolonia zostanie praktycznie zniszczona.'):
   raise ValueError(('Planetbuster warning text malformed',warning))
  store(warning,'planetbuster_warning')
 if len(cases)!=60:raise ValueError(('Incomplete compositional tests',len(cases)))
 return {'rendered_combinations':len(cases),'categories':sorted({x['category'] for x in cases}),
         'dynamic_market_industry_system_names_tested':len(names)+len(markets)+len(industries),
         'numeric_forms_tested':len(duration),'technical_keys_protected':1}

def check(root:Path,repo:Path|None=None)->dict:
 root=Path(root);repo=Path(repo) if repo else Path(__file__).resolve().parent.parent
 path=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';trans=path/'translations'
 old=(trans/OLD).read_bytes();new=(trans/NEW).read_bytes()
 if (sha(old),sha(new))!=(BASE_SHA,NEW_MAP_SHA):raise ValueError('Unexpected API map checksum')
 source=readmap(trans/OLD);target=readmap(trans/NEW);expected,details=build(source)
 if expected!=target or encode(expected)!=new:raise ValueError('Unapproved API mapping change')
 if len(source)!=5314 or len(target)!=5314 or len(details['reviews'])!=35 or len(details['repaired'])!=14:
  raise ValueError('Wrong mapping/inventory counts')
 classmap={r['english_literal']:r['polish_ascii_draft'] for r in target if r['source_class']==CLASS}
 if len(classmap)!=47 or set(REPAIRS)-set(classmap):raise ValueError('Missing reviewed class mapping')
 rendered=render(classmap)
 code=(path/'main.go').read_text('utf8')
 if sha(code.encode())!=NEW_GO_SHA:raise ValueError('API patcher Go code unexpectedly changed')
 for a,b in reversed([('const version = "1062"','const version = "1063"'),
  ('const exeVersion = "1.0.62"','const exeVersion = "1.0.63"'),
  ('"1061", version}','"1061", "1062", version}'),
  ('PL ASCII patch up to 1.0.62','PL ASCII patch up to 1.0.63')]):code=once(code,b,a)
 if sha(code.encode())!=OLD_GO_SHA:raise ValueError('Non-version API Go executable source change')
 if 'const edition = "1.0.63"' not in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8'):
  raise ValueError('Wrong installer version')
 mod=root/'mod';meta=json.loads((mod/'mod_info.json').read_text('utf8'))
 if (meta.get('version'),meta.get('gameVersion'),len(meta.get('replace',[])))!=('1.0.63','0.98a-RC8',41):raise ValueError('Wrong mod metadata')
 readme=(mod/'CZYTAJ.txt').read_text('utf8')
 if not readme.startswith('STARSECTOR PL ASCII 1.0.63') or not readme.endswith(RELEASE_SUFFIX):raise ValueError('Wrong release notes')
 files=sorted(x for x in (mod/'data').rglob('*') if x.is_file())
 digest=sha('\n'.join(f'{x.relative_to(mod/"data").as_posix()}:{sha(x.read_bytes())}' for x in files).encode())
 if len(files)!=870 or digest!=DATA_SHA or sha((mod/'data/campaign/rules.csv').read_bytes())!=RULES_SHA:
  raise ValueError('Game data or dialogues accidentally modified')
 manual=repo/'docs/LUDDIC_CELLS_REVIEW_1063.json';evidence=repo/'docs/JVM_AUDIT_1063.json'
 if sha(manual.read_bytes())!=REVIEW_SHA or sha(evidence.read_bytes())!=JVM_SHA:
  raise ValueError('Pinned original JVM or reviewed text evidence changed')
 check_review(root,manual)
 e=json.loads(evidence.read_text('utf8'))
 if e['original_java_ldc_string_uses']!=83 or len(e['mapped_source_literals'])!=47 or e['historical_unreviewed_rows']!=35 or e['approved_repairs']!=14:
  raise ValueError('Original JVM review numbers do not match actual evidence')
 for x in e['mapped_source_literals']:
  if x['english_literal'] not in classmap or not x['uses']:raise ValueError('Original JVM mapping lacking callsite')
 return {'release':'1.0.63','historical_api_reviewed_new':35,'historical_api_reviewed_total':482,
  'historical_api_unreviewed':3176,'source_class_count':1,'mapped_literals':47,
  'original_jvm_ldc_uses':83,'original_jvm_unique_source_strings':71,
  'repaired_literals':14,'game_data_files_byte_identical':870,'old_mapping_sha256':BASE_SHA,
  'new_mapping_sha256':NEW_MAP_SHA,'windows_gameplay_tested':False,**rendered}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--repo',type=Path)
 a=p.parse_args();print(json.dumps(check(a.worktree,a.repo),indent=2))
