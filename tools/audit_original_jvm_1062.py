#!/usr/bin/env python3
"""Private original-JAR callsite evidence for all PirateBaseIntel strings in v1.0.62."""
from __future__ import annotations
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from apply_1062 import CLASS,OLD,ADDITIONS,REPAIRS,sha
from apply_1054 import readmap
ORIGINAL_SHA='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
EXPECTED_USES=42
HIGHLIGHTS={('addBulletPoints',174,'Agreement'),('createSmallDescription',356,'agreement'),('createSmallDescription',438,'agreement')}
TECHNICAL={('getSortString',4,'Fleet log'),('getIntelTags',59,'Colony threats'),('getIntelTags',81,'Colony threats')}

def audit(jar:Path,root:Path)->dict:
 jar=Path(jar);root=Path(root)
 if sha(jar.read_bytes())!=ORIGINAL_SHA:raise ValueError('Commercial source JAR checksum does not match 0.98a-RC8')
 t=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 old=readmap(t/OLD);keys={r['english_literal'] for r in old if r['source_class']==CLASS}
 if len(keys)!=36 or len(keys|set(ADDITIONS))!=38:raise ValueError('Incorrect 1.0.61 map class inventory')
 p=subprocess.run(['javap','-classpath',str(jar),'-c','-p',CLASS],capture_output=True,text=True,check=True,timeout=45)
 uses=[];method=None
 for line in p.stdout.splitlines():
  m=re.search(r'\b([A-Za-z_$][\w$]*)\([^;]*\);\s*$',line)
  if m and line.startswith('  '):method=m.group(1)
  match=re.match(r'^\s*(\d+):\s+ldc(?:_w)?\s+#(\d+)\s+// String\s*(.*)$',line)
  if not match:continue
  choices=[s for s in keys|set(ADDITIONS) if s.strip()==match.group(3).strip()]
  if len(choices)>1:raise ValueError(('Ambiguous Java literal token',match.group(3),choices))
  if len(choices)==1:uses.append({'method':method,'offset':int(match.group(1)),'constant_pool_index':int(match.group(2)),'english_literal':choices[0]})
 if len(uses)!=EXPECTED_USES or {x['english_literal'] for x in uses}!=keys|set(ADDITIONS):
  raise ValueError(('Incomplete original JVM callsite audit',len(uses),len({x['english_literal'] for x in uses})))
 have={(x['method'],x['offset'],x['english_literal']) for x in uses}
 if not (HIGHLIGHTS|TECHNICAL)<=have:raise ValueError('Required UI/technical context is missing')
 for method,offset,lit in TECHNICAL|HIGHLIGHTS:
  matched=[x for x in uses if (x['method'],x['offset'],x['english_literal'])==(method,offset,lit)]
  if len(matched)!=1:raise ValueError(('Wrong multiplicity for original JVM site',method,offset,lit))
 if any(x['method']=='getIntelTags' and x['english_literal']=='Fleet log' for x in uses):raise ValueError('Unexpected tag mutation context')
 if any(x['method']!='getIntelTags' and x['english_literal']=='Colony threats' for x in uses):raise ValueError('Colony threats is used outside tag set')
 # An approved correction must be an actual original JVM literal, not a fabricated term.
 if not set(REPAIRS)<={x['english_literal'] for x in uses}:raise ValueError('Unproved translation repair')
 return {'release':'1.0.62','game_version':'0.98a-RC8','original_jar_sha256':ORIGINAL_SHA,'source_class':CLASS,
  'original_mapped_literals':len(keys),'new_missing_literals':len(ADDITIONS),
  'confirmed_original_jvm_ldc_uses':len(uses),'unique_confirmed_literals':len({x['english_literal'] for x in uses}),
  'highlight_call_sites':sorted([{'method':a,'offset':b,'literal':c} for a,b,c in HIGHLIGHTS],key=lambda x:(x['method'],x['offset'])),
  'technical_tag_call_sites':sorted([{'method':a,'offset':b,'literal':c} for a,b,c in TECHNICAL],key=lambda x:(x['method'],x['offset'])),
  'uses':uses,'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--jar',required=True,type=Path);p.add_argument('--worktree',required=True,type=Path);p.add_argument('--out',type=Path)
 a=p.parse_args();r=audit(a.jar,a.worktree)
 if a.out:a.out.write_text(json.dumps(r,indent=2,ensure_ascii=True)+'\n','utf8')
 print(json.dumps({k:v for k,v in r.items() if k!='uses'},indent=2))
