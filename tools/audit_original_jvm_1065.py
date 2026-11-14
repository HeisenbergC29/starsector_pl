#!/usr/bin/env python3
"""Inspect source-class Java literals on the user's private original Starsector API JAR.

This script does not serialize or distribute original .class bytes. It records
only SHA-256, active ldc call sites and source literals already published in
translation CSV, with method/bytecode offsets for reproducibility.
"""
from __future__ import annotations
import argparse,json,re,subprocess,zipfile
from pathlib import Path
from audit_original_jvm_1063 import string_pool
from apply_1054 import readmap
from apply_1065 import CLASS,OLD,DRAFT,REPAIRS,sha
ORIGINAL_API='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
TOTAL_LOADS=363
UNIQUE_LITERALS=240
MAPPED=111
HISTORIC_DRAFTS=104

def audit(jar:Path,root:Path)->dict:
 if sha(jar.read_bytes())!=ORIGINAL_API:raise ValueError('Different private game API JAR')
 rows=[r for r in readmap(Path(root)/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'/OLD)
       if r['source_class']==CLASS]
 if len(rows)!=MAPPED or sum(r['status'] in DRAFT for r in rows)!=HISTORIC_DRAFTS:
  raise ValueError('Wrong baseline MarketCMD inventory')
 with zipfile.ZipFile(jar) as z:
  original=z.read(CLASS.replace('.','/')+'.class')
  pool=string_pool(original)
 proc=subprocess.run(['javap','-classpath',str(jar),'-c','-p',CLASS],capture_output=True,text=True,check=True,timeout=60)
 method='';uses=[]
 for line in proc.stdout.splitlines():
  stripped=line.strip()
  if line.startswith('  ') and not line.startswith('    ') and (stripped.endswith(');') or stripped=='static {};'):
   method=stripped
  m=re.match(r'^\s*(\d+):\s+(ldc(?:_w|2_w)?)\s+#(\d+)\s+// String',line)
  if m:
   cp=int(m[3]);literal=pool.get(cp)
   if literal is None:raise ValueError(('Unrecognized String pool index',cp))
   uses.append({'method':method,'offset':int(m[1]),'opcode':m[2],
     'cp_index':cp,'literal':literal})
 if len(uses)!=TOTAL_LOADS or len({x['literal'] for x in uses})!=UNIQUE_LITERALS:
  raise ValueError(('Changed original MarketCMD bytecode constants',len(uses)))
 selected=[]
 for r in rows:
  evidence=[{k:v for k,v in u.items() if k!='literal'} for u in uses if u['literal']==r['english_literal']]
  if not evidence:raise ValueError(('Translation never loaded by JVM',r['english_literal']))
  selected.append({'english_literal':r['english_literal'],'source_sha256':sha(r['english_literal'].encode()),
   'prior_status':r['status'],'draft_reviewed_1065':r['status'] in DRAFT,
   'corrected_1065':r['english_literal'] in REPAIRS,'uses':evidence})
 if len(selected)!=MAPPED or sum(x['draft_reviewed_1065'] for x in selected)!=HISTORIC_DRAFTS:
  raise ValueError('Incomplete review evidence')
 return {'release':'1.0.65','original_jar_sha256':ORIGINAL_API,
  'source_class':CLASS,'original_class_sha256':sha(original),
  'jvm_ldc_uses':len(uses),'unique_jvm_literal_texts':UNIQUE_LITERALS,
  'mapped_source_literals':MAPPED,'historical_draft_reviews':HISTORIC_DRAFTS,
  'repaired_fragments':len(REPAIRS),'unmapped_original_jvm_literals':UNIQUE_LITERALS-MAPPED,
  'mapped_literal_evidence':selected,'gameplay_test_policy':'after_1_1_release',
  'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--jar',type=Path,required=True)
 p.add_argument('--worktree',type=Path,required=True);p.add_argument('--out',type=Path)
 a=p.parse_args();v=audit(a.jar,a.worktree)
 if a.out:a.out.write_text(json.dumps(v,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 print(json.dumps({k:v for k,v in v.items() if k!='mapped_literal_evidence'},indent=2))
