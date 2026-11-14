#!/usr/bin/env python3
"""v1.0.62: PirateBaseIntel class-scoped original-JVM text repairs and 31 historical reviews.

Keep Java category tags untouched, repair agreement highlighting and event notices.
The two new literals are used as UI text and highlighter arguments, not keys.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from apply_1054 import readmap,encode,once

CLASS='com.fs.starfarer.api.impl.campaign.intel.bases.PirateBaseIntel'
OLD='TLUMACZENIA_JAR_1061.csv';NEW='TLUMACZENIA_JAR_1062.csv'
BASE_SHA='9efa72c67950a3f92ad776ad4c92172fa050f54d88556c8f159c3b1bec91f11b'
DRAFT={'OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_ONLY_NOT_INSTALLED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME'}
STATUS='REVIEWED_ORIGINAL_JVM_PIRATE_BASE_1062_PENDING_WINDOWS'
REPAIRS={
 'Agreement broken':'Zerwano porozumienie',
 'Agreement dissolved':'Rozwiazano porozumienie',
 'Agreement made with base commander':'Porozumienie zawarte z dowodca bazy',
 'Fleet log':'Fleet log', # TECHNICAL Set.contains() argument in getSortString()
 'Colony threats':'Colony threats', # TECHNICAL Set.add() category in getIntelTags()
}
ADDITIONS={'Agreement':'Porozumienie','agreement':'porozumienie'}
RELEASE_SUFFIX=('\nW wiadomosciach o bazach piratow poprawiono komunikaty o porozumieniu '
 'i podswietlane slowa (5 korekt i 2 nowe teksty UI). Przywrocono nienaruszone '
 'techniczne nazwy kategorii Fleet log i Colony threats. 31 historycznych '
 'wpisow API sprawdzono z oryginalnym JVM, bez zmian mechaniki gry.\n')

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def fp(row:dict)->str:return sha('\0'.join(row[k] for k in ('source_class','english_literal','polish_ascii_draft')).encode())

def build(rows:list[dict])->tuple[list[dict],dict]:
 if len(rows)!=5312 or len({(r['source_class'],r['english_literal']) for r in rows})!=5312:
  raise ValueError('Not exactly 1.0.61 mapping')
 if sha(encode(rows))!=BASE_SHA:raise ValueError('Historical base map is not the approved byte-exact 1.0.61 map')
 orig={r['english_literal']:r for r in rows if r['source_class']==CLASS}
 if len(orig)!=36 or set(REPAIRS)-set(orig) or set(ADDITIONS)&set(orig):
  raise ValueError('Pirate Base mapping scope differs from original JVM review')
 drafts=[r for r in orig.values() if r['status'] in DRAFT]
 if len(drafts)!=31 or sum(orig[k]['status'] in DRAFT for k in REPAIRS)!=5:
  raise ValueError('Wrong historical review or repair count')
 if any(orig[k]['polish_ascii_draft']==v for k,v in REPAIRS.items()):
  raise ValueError('An expected repair was already applied')
 out=[]; reviewed=[];corrected=[]
 for prev in rows:
  r=dict(prev)
  if r['source_class']==CLASS:
   k=r['english_literal'];before=r['polish_ascii_draft']
   if k in REPAIRS:
    after=REPAIRS[k]
    if any(before.count(x)!=after.count(x) for x in ('%s','%d','%f','\r','\n','\t')):
     raise ValueError(('Technical format tokens changed',k))
    r['polish_ascii_draft']=after
    corrected.append(k)
   if r['status'] in DRAFT:
    reviewed.append({'source_class':CLASS,'english_literal':k,'old_draft':before,
      'old_status':prev['status'],'new_draft':r['polish_ascii_draft'],
      'old_row_sha256':fp(prev),'new_row_sha256':fp(r),
      'english_key_sha256':sha(k.encode())})
    r['status']=STATUS
   if not r['polish_ascii_draft'].isascii():raise ValueError('Non-ASCII translation')
  out.append(r)
 for en,pl in ADDITIONS.items():
  if not en.isascii() or not pl.isascii():raise ValueError('Non-ASCII literal')
  out.append({'source_class':CLASS,'english_literal':en,'polish_ascii_draft':pl,'status':STATUS})
 if len(out)!=5314 or len({(r['source_class'],r['english_literal']) for r in out})!=5314:
  raise ValueError('Wrong resulting API mapping inventory')
 if len(reviewed)!=31 or len(corrected)!=5 or set(corrected)!=set(REPAIRS):raise ValueError('Unverified review or repair')
 # Recompute fingerprint after approval status (status is not part of the fingerprint).
 return out,{'reviews':reviewed,'corrected':corrected,'new_literals':list(ADDITIONS)}

def apply(root:Path)->dict:
 root=Path(root);api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';trans=api/'translations'
 src=trans/OLD;dest=trans/NEW
 if dest.exists() or sha(src.read_bytes())!=BASE_SHA:raise ValueError('Not genuine 1.0.61 baseline')
 old=readmap(src)
 if encode(old)!=src.read_bytes():raise ValueError('Map not byte-canonical')
 rows,review=build(old);updated=encode(rows)
 main=api/'main.go';go=main.read_text('utf8')
 for a,b in [('const version = "1061"','const version = "1062"'),
  ('const exeVersion = "1.0.61"','const exeVersion = "1.0.62"'),
  ('"1060", version}','"1060", "1061", version}'),
  ('PL ASCII patch up to 1.0.61','PL ASCII patch up to 1.0.62')]:go=once(go,a,b)
 installer=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
 ins=once(installer.read_text('utf8'),'const edition = "1.0.61"','const edition = "1.0.62"')
 info=root/'mod/mod_info.json';meta=json.loads(info.read_text('utf8'))
 if (meta['version'],meta['gameVersion'])!=('1.0.61','0.98a-RC8'):raise ValueError('Wrong mod base version')
 meta['version']='1.0.62';meta['description']=once(meta['description'],'1.0.61','1.0.62')
 guide=root/'mod/CZYTAJ.txt';readme=once(guide.read_text('utf8'),'STARSECTOR PL ASCII 1.0.61','STARSECTOR PL ASCII 1.0.62')+RELEASE_SUFFIX
 dest.write_bytes(updated);main.write_text(go,'utf8');installer.write_text(ins,'utf8')
 info.write_text(json.dumps(meta,ensure_ascii=True,indent=2)+'\n','utf8');guide.write_text(readme,'utf8')
 return {'release':'1.0.62','reviewed_historical_rows':len(review['reviews']),
  'repaired_existing_literals':len(review['corrected']),'added_missing_literals':len(ADDITIONS),
  'api_map_rows':len(rows),'api_map_sha256':sha(updated),'data_changed':0,
  'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args()
 print(json.dumps(apply(a.worktree),indent=2))
