#!/usr/bin/env python3
"""1.0.55: original-JVM-verified duration fragments in two blockade tooltips.

Keep event IDs and JVM code untouched. Also repair a grammatically duplicated
GenericRaidFGI 'no target colony' sentence across two existing constants.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from apply_1054 import readmap,encode,sha,once

OLD='TLUMACZENIA_JAR_1054.csv'
NEW='TLUMACZENIA_JAR_1055.csv'
OLD_SHA='d7256e12565e62d3cce7c67479014af9857a1b9357e252bcca26a7ae79067ce0'
API='com.fs.starfarer.api.impl.campaign.intel.group.'
BLOCK=API+'BlockadeFGI'
KNIGHTS=API+'KnightsOfLuddTakeoverExpedition'
GENERIC=API+'GenericRaidFGI'
STATUS='VERIFIED_ORIGINAL_JVM_UI_COMPOSITION_1055_OFFLINE_PENDING_WINDOWS'
# Both classes dynamically concatenate: localized sentence + number + optional
# "more " + day/days. English "more " cannot be translated word-for-word after
# a numeral in Polish without a grammar error; omit only this redundant token.
ADDITIONS={(cl,en):pl for cl in (BLOCK,KNIGHTS) for en,pl in (
    ('day','dzien'),('days','dni'),('more ',''),('Assessment','Ocena'))}
# Existing Polish fragments duplicated 'do zaatakowania' across an inserted
# operation name. Quoting that name keeps grammatical correctness for any
# nominative noun (including user/mod supplied terms).
REPAIRS={
 (GENERIC,'There are no colonies for the '):(
   'Nie ma kolonii, ktore moglyby zostac zaatakowane przez ',
   'W tym ukladzie nie ma kolonii dostepnych jako cel operacji: "'),
 (GENERIC,' to target in the system.'):(' do zaatakowania w ukladzie.','".'),
}
GO_EDITS=(
 ('const version = "1054"','const version = "1055"'),
 ('const exeVersion = "1.0.54"','const exeVersion = "1.0.55"'),
 ('"1051", "1052", "1053", version}', '"1051", "1052", "1053", "1054", version}'),
 ('PL ASCII patch up to 1.0.54','PL ASCII patch up to 1.0.55'),
)
EXPECTED_ROWS=5298

def plan(base):
 if len(base)!=5290:raise ValueError('Not v1.0.54 mapping')
 ids={(x['source_class'],x['english_literal']) for x in base}
 if len(ids)!=len(base) or ids.intersection(ADDITIONS):raise ValueError('Duplicate/new literal collision')
 edited=set();out=[]
 for original in base:
  r=dict(original);key=r['source_class'],r['english_literal']
  if key in REPAIRS:
   src,dst=REPAIRS[key]
   if r['polish_ascii_draft']!=src:raise ValueError(('Unexpected previous translation',key))
   if r['status'] not in ('OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_ONLY_NOT_INSTALLED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME'):
    raise ValueError(('Previous row already verified; reject implicit replacement',key))
   if any(src.count(t)!=dst.count(t) for t in ('%s','%d','%f','\n','\t')):raise ValueError('Format mismatch')
   r['polish_ascii_draft']=dst;edited.add(key)
  out.append(r)
 if edited!=set(REPAIRS):raise ValueError(('Missing old mapping',set(REPAIRS)-edited))
 for (cl,en),pl in ADDITIONS.items():
  if not en.isascii() or not pl.isascii() or en.count('%s')!=pl.count('%s'):
   raise ValueError(('Non-ASCII or format change',cl,en))
  out.append(dict(source_class=cl,english_literal=en,polish_ascii_draft=pl,status=STATUS))
 if len(out)!=EXPECTED_ROWS or len({(r['source_class'],r['english_literal']) for r in out})!=EXPECTED_ROWS:
  raise ValueError('Unexpected map cardinality')
 return out

def apply(root):
 root=Path(root);api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';translation=api/'translations'
 a,b=translation/OLD,translation/NEW
 if b.exists():raise FileExistsError('Patch v1055 already present')
 if sha(a.read_bytes())!=OLD_SHA:raise ValueError('Unexpected 1054 base map hash')
 src=readmap(a)
 if encode(src)!=a.read_bytes():raise ValueError('CSV format mismatch')
 content=encode(plan(src));b.write_bytes(content)
 p=api/'main.go';s=p.read_text('utf8')
 for x,y in GO_EDITS:s=once(s,x,y)
 p.write_text(s,'utf8')
 p=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
 p.write_text(once(p.read_text('utf8'),'const edition = "1.0.54"','const edition = "1.0.55"'),'utf8')
 p=root/'mod/mod_info.json';m=json.loads(p.read_text('utf8'))
 if m['version']!='1.0.54' or m['gameVersion']!='0.98a-RC8':raise ValueError('Unexpected mod version')
 m['version']='1.0.55';m['description']=once(m['description'],'1.0.54','1.0.55')
 p.write_text(json.dumps(m,ensure_ascii=True,indent=2)+'\n','utf8')
 p=root/'mod/CZYTAJ.txt';p.write_text(once(p.read_text('utf8'),'STARSECTOR PL ASCII 1.0.54','STARSECTOR PL ASCII 1.0.55')+
 '\nNaprawiono jednostki czasu i naglowki Ocena w dwoch blokadach oraz gramatyke komunikatu o braku celow w GenericRaidFGI. Nie zmieniono mechaniki gry.\n','utf8')
 return {'version':'1.0.55','new_api_literals':8,'corrected_historical_fragments':2,
  'new_map_sha256':sha(content),'total_rows':EXPECTED_ROWS,'affected_classes':3,'unchanged_data_files':870,'new_jvm_bytecode_changes':0}

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('worktree',type=Path);args=a.parse_args()
 print(json.dumps(apply(args.worktree),indent=2))
