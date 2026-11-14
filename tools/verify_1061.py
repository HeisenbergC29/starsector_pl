#!/usr/bin/env python3
"""Strict v1.0.61 class-only map, dynamic-grammar and game-data verification."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from apply_1054 import readmap,encode,once
from apply_1061 import CLASS,OLD,NEW,BASE_SHA,DRAFT,STATUS,REPAIRS,NEW_LITERALS,RELEASE_SUFFIX,build,sha
from verify_1060 import DATA_SHA,RULES_SHA,NEW_GO_SHA as PREVIOUS_GO_SHA
from build_review_1061 import check as check_review

NEW_MAP_SHA='9efa72c67950a3f92ad776ad4c92172fa050f54d88556c8f159c3b1bec91f11b'
NEW_GO_SHA='357f50ff0a085f5902b8a06ddb6948f1c512efa4115ac492579fe600a5ee505d'
REVIEW_SHA='8307c138e859b1b953f2b2b137a648da36615ac94231eb83a694892aa07100d1'
JVM_EVIDENCE_SHA='373589a97899dbc7c764ed63fe2c7d035d0c2af21c05b310b5195b5b730879dd'


def render(mapping:dict[str,str])->dict:
 v=lambda english:mapping[english]
 numbers=[1,2,5,11,21,22]
 places=['Askonia','uklad Askonia','Sigma','Nowa Ziemia','Eochu Bres']
 sentences=[]
 for count in numbers:
  unit=v('day') if count==1 else v('days')
  if unit!=('dzien' if count==1 else 'dni'):raise ValueError('Incorrect Polish day/day-plural translation')
  for tail in [' to complete transit',' for transit',' to complete transit']:
   # Three bullet callsites share one English prefix, two suffixes.
   actual=v('Estimated %s ').replace('%s',str(count))+unit+v(tail)
   if actual!=f'Szacowany czas przelotu: {count} {unit}':raise ValueError(('Incorrect full bullet',actual))
   sentences.append(actual)
  for place in places:
   for intro in ["Once it's in open space, it's estimated that it will take %s ",
       "The gate hauler is in transit, in deep space. It's estimated that it will take %s "]:
    s=(v(intro).replace('%s',str(count))+unit+v(' until it arrives ')
      +v('to its destination, the ')+place+v('. On arrival, ')
      +v('it will take some time to decelerate and attain a parking orbit.'))
    if f'{count} {unit}. Cel: {place}. Po przybyciu ' not in s:raise ValueError(('Incorrect dynamic destination/time composition',s))
    sentences.append(s)
 for place in places:
  arrived=v('Arrived at ')+place
  arriving=v('Arriving at ')+place
  inbound=v('The gate hauler has arrived to the ')+place+v(' ')+v('and is decelerating in order to attain a parking orbit.')
  if arrived!=f'Dotarl do celu: {place}' or arriving!=f'Zbliza sie do celu: {place}':
   raise ValueError('Location names have incorrect case or missing label')
  if inbound!=f'Holownik Bram dotarl do celu: {place}. Wyhamowuje, aby wejsc na orbite postojowa.':
   raise ValueError(('Arrival status has incorrect sentence separator',inbound))
  sentences.extend([arrived,arriving,inbound])
 if any(not x.isascii() for x in sentences):raise ValueError('Non-ASCII installed string')
 if any(' do zakonczenia przelotu' in x or ' do przybycia ' in x or ' dni do ' in x or ' days' in x or ' day ' in x or ' . ' in x for x in sentences):
  raise ValueError('Original English time suffix or ungrammatical Polish survived')
 for s in sentences[-len(places)*3:]:
  if not any(x in s for x in places):raise ValueError('Lost destination name')
 if not (v('Status: dormant')=='Stan: uspiony' and v('Status: activating')=='Stan: uruchamianie' and v('Status: operational')=='Stan: gotowy'):
  raise ValueError('Incorrect masculine status for Holownik')
 if v('transiting deep space')!='w przelocie przez gleboka przestrzen':raise ValueError('Wrong location phrase')
 if len(sentences)!=93:raise ValueError(('Unexpected test coverage',len(sentences)))
 return {'bullet_time_variants':18,'full_transit_variants':60,'destination_variants':15,'total_compositions':len(sentences)}


def check(root:Path)->dict:
 root=Path(root);api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';t=api/'translations'
 original=(t/OLD).read_bytes();updated=(t/NEW).read_bytes()
 if (sha(original),sha(updated))!=(BASE_SHA,NEW_MAP_SHA):raise ValueError('1.0.60/1.0.61 original map SHA mismatch')
 prev=readmap(t/OLD);now=readmap(t/NEW);expected,stats=build(prev)
 if now!=expected or encode(expected)!=updated:raise ValueError('Unexpected changed map rows')
 if len(now)!=5312 or stats['changed_translations']!=15 or stats['new_translations']!=3 or len(stats['reviewed'])!=25:
  raise ValueError('Translation/report count mismatch')
 mapped={x['english_literal']:x['polish_ascii_draft'] for x in now if x['source_class']==CLASS}
 if len(mapped)!=33:raise ValueError('Unexpected class-specific map count')
 composition=render(mapped)
 sources=(api/'main.go').read_text('utf8');newsha=sha(sources.encode())
 if newsha!=NEW_GO_SHA:raise ValueError(('Unapproved Go executable source changes',newsha))
 for old,new in reversed([
   ('const version = "1060"','const version = "1061"'),
   ('const exeVersion = "1.0.60"','const exeVersion = "1.0.61"'),
   ('"1059", version}','"1059", "1060", version}'),
   ('PL ASCII patch up to 1.0.60','PL ASCII patch up to 1.0.61')]):sources=once(sources,new,old)
 if sha(sources.encode())!=PREVIOUS_GO_SHA:raise ValueError('Non-version Go source was changed')
 if 'const edition = "1.0.61"' not in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8'):
  raise ValueError('Installer version mismatch')
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 if (meta.get('version'),meta.get('gameVersion'),len(meta.get('replace',[])))!=('1.0.61','0.98a-RC8',41):
  raise ValueError('Mod meta broken')
 guide=(root/'mod/CZYTAJ.txt').read_text('utf8')
 if not guide.startswith('STARSECTOR PL ASCII 1.0.61') or not guide.endswith(RELEASE_SUFFIX):
  raise ValueError('Mod instructions missing')
 data=root/'mod/data';files=sorted(p for p in data.rglob('*') if p.is_file())
 digest=sha('\n'.join(f'{p.relative_to(data).as_posix()}:{sha(p.read_bytes())}' for p in files).encode())
 if len(files)!=870 or digest!=DATA_SHA or sha((data/'campaign/rules.csv').read_bytes())!=RULES_SHA:
  raise ValueError('Localized game data changed unexpectedly')
 repo=Path(__file__).resolve().parent.parent
 record=repo/'docs/GATE_HAULER_REVIEW_1061.json';ev=repo/'docs/JVM_AUDIT_1061.json'
 if sha(record.read_bytes())!=REVIEW_SHA or sha(ev.read_bytes())!=JVM_EVIDENCE_SHA:raise ValueError('Original-JVM evidence or manual review ledger changed')
 review=check_review(root,record)
 audit=json.loads(ev.read_text('utf8'))
 if (audit['confirmed_original_jvm_ldc_uses'],audit['class_scoped_map_entries'],audit['day_singular_uses'],audit['day_plural_uses'])!=(49,33,5,5):raise ValueError('JVM callsite coverage changed')
 return {'release':'1.0.61','api_rows':len(now),'reviewed_historical_rows':25,
   'historical_reviewed_total':416,'historical_remaining':3242,
   'new_literals':3,'fixed_existing_literals':15,'original_jvm_callsite_uses':49,
   'grammar_combinations':composition['total_compositions'],
   'game_data_files_unchanged':870,'mapping_sha256':NEW_MAP_SHA,
   'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 a=p.parse_args();print(json.dumps(check(a.worktree),indent=2))
