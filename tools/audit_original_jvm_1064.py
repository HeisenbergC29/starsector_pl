#!/usr/bin/env python3
"""Original commercial JAR audit of v1.0.64 inspection and Path base strings.

Checks complete byte-accurate JVM constant-pool values and actual ldc bytecode.
Only publishes metadata/translation evidence; never serializes original .class.
"""
from __future__ import annotations
import argparse,json,re,subprocess,zipfile
from pathlib import Path
from audit_original_jvm_1063 import string_pool
from apply_1054 import readmap
from apply_1064 import INSPECTION,PATH_BASE,CLASSES,DRAFT_COUNTS,REPAIRS,TECHNICAL,OLD,sha,DRAFT
ORIGINAL_API='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
EXPECT={INSPECTION:(56,45),PATH_BASE:(94,89)}
GUARDS={
 (INSPECTION,'Colony threats'):('getIntelTags(',17,20,'Set.add:'),
 (PATH_BASE,'Colony threats'):('getIntelTags(',79,82,'Set.add:'),
 (PATH_BASE,'Fleet log'):('getSortString(',4,7,'Set.contains:')
}

def audit(jar:Path,worktree:Path)->dict:
 if sha(jar.read_bytes())!=ORIGINAL_API:raise ValueError('Wrong original Starsector API JAR hash')
 mapping=readmap(Path(worktree)/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'/OLD)
 groups=[];total_uses=0;total_mapped=0;total_draft=0
 with zipfile.ZipFile(jar) as z:
  for cl in (INSPECTION,PATH_BASE):
   original=z.read(cl.replace('.','/')+'.class');pool=string_pool(original)
   proc=subprocess.run(['javap','-classpath',str(jar),'-c','-p',cl],capture_output=True,text=True,check=True,timeout=50)
   method='';seen=[]
   for line in proc.stdout.splitlines():
    stripped=line.strip()
    if line.startswith('  ') and not line.startswith('    ') and (stripped.endswith(');') or stripped=='static {};'):
     method=stripped
    m=re.match(r'^\s*(\d+):\s+(ldc(?:_w|2_w)?)\s+#(\d+)\s+// String',line)
    if m:
     cp=int(m[3]);literal=pool.get(cp)
     if literal is None:raise ValueError(('Invalid JVM String cp',cl,cp))
     seen.append({'method':method,'offset':int(m[1]),'opcode':m[2],'cp_index':cp,'literal':literal})
   actual=set(x['literal'] for x in seen)
   if (len(seen),len(actual))!=EXPECT[cl]:raise ValueError(('Original JVM inventory changed',cl,len(seen),len(actual)))
   rows=[r for r in mapping if r['source_class']==cl]
   drafts=[r for r in rows if r['status'] in DRAFT]
   if len(rows)!=CLASSES[cl] or len(drafts)!=DRAFT_COUNTS[cl] or any(r['english_literal'] not in actual for r in rows):
    raise ValueError(('Unreachable or incomplete mapped JVM source strings',cl,len(rows),len(drafts)))
   text_evidence=[]
   for row in rows:
    uses=[{k:v for k,v in x.items() if k!='literal'} for x in seen if x['literal']==row['english_literal']]
    if not uses:raise ValueError(('Missing literal uses',cl,row['english_literal']))
    text_evidence.append({'english_literal':row['english_literal'],'source_sha256':sha(row['english_literal'].encode()),
     'old_status':row['status'],'reviewed_1064':row['status'] in DRAFT,
     'repaired_1064':(cl,row['english_literal']) in REPAIRS,'uses':uses})
   for (guardcl,lit),(meth,ldc_offset,setoffset,operation) in GUARDS.items():
    if guardcl!=cl:continue
    hit=[x for x in seen if x['literal']==lit and meth in x['method']]
    if len(hit)!=1 or hit[0]['offset']!=ldc_offset:
     raise ValueError(('Technical tag instruction missing',cl,lit,hit))
    pattern=rf'\b{ldc_offset}: ldc(?:_w)?\s+#\d+\s+// String {re.escape(lit)}\n\s+{setoffset}: invokeinterface\s+#\d+,\s+2\s+// InterfaceMethod java/util/{re.escape(operation)}'
    if not re.search(pattern,proc.stdout):raise ValueError(('Not a Set key operation',cl,lit))
   groups.append({'source_class':cl,'original_class_sha256':sha(original),
    'total_ldc_uses':len(seen),'unique_ldc_literals':len(actual),
    'mapped_source_literals':len(rows),'new_historical_reviews':len(drafts),
    'literal_evidence':text_evidence})
   total_uses+=len(seen);total_mapped+=len(rows);total_draft+=len(drafts)
 if (total_uses,total_mapped,total_draft)!=(150,56,48):raise ValueError('Unexpected combined coverage')
 return {'release':'1.0.64','original_jar_sha256':ORIGINAL_API,
  'mapped_classes':2,'original_jvm_ldc_uses':total_uses,'mapped_literals':total_mapped,
  'historic_draft_reviews':total_draft,'repaired_literals':len(REPAIRS),
  'technical_tags':[{'source_class':k[0],'source_literal':k[1],'method':v[0],
   'ldc_offset':v[1],'set_opcode_offset':v[2],'set_operation':v[3]} for k,v in GUARDS.items()],
  'classes':groups,'unresolved_dynamic_getters':[
   'FactionAPI.getDisplayNameHasOrHave()','FactionAPI.getDisplayNameIsOrAre()'],
  'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--jar',type=Path,required=True)
 p.add_argument('--worktree',type=Path,required=True);p.add_argument('--out',type=Path)
 a=p.parse_args();res=audit(a.jar,a.worktree)
 if a.out:a.out.write_text(json.dumps(res,ensure_ascii=True,indent=2)+'\n','utf8')
 print(json.dumps({k:v for k,v in res.items() if k!='classes'},indent=2))
