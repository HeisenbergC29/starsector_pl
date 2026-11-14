#!/usr/bin/env python3
"""Offline original-JVM evidence for three class-scoped v1.0.66 text maps."""
from __future__ import annotations
import argparse,json,re,subprocess,zipfile
from pathlib import Path
from audit_original_jvm_1063 import string_pool
from apply_1054 import readmap
from apply_1066 import SIM,IND,TUT,CLASSES,OLD,ADDITIONS,sha
ORIGINAL_API='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
COUNTS={SIM:(272,204),IND:(188,118),TUT:(209,147)}
TECHNICAL={SIM:{'behavior_aggressive','cat_default','quality_high','cores_gamma','officers_none'},
 IND:{'market_no_industries_allowed','industry','structure','ind_core','industryRefundFraction'},
 TUT:{'Story','$tutMadeContactAtAncyra','galatia_probe','REFIT_MANAGE_VARIANTS'}}

def audit(jar:Path,root:Path)->dict:
 jar=Path(jar);root=Path(root)
 if sha(jar.read_bytes())!=ORIGINAL_API:raise ValueError('Unrecognized original game API JAR SHA')
 old=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'/OLD
 source=readmap(old)
 report={};totalload=0;allmapped=0
 with zipfile.ZipFile(jar) as z:
  for cl,(expected_uses,unique) in COUNTS.items():
   original=z.read(cl.replace('.','/')+'.class');pool=string_pool(original)
   proc=subprocess.run(['javap','-classpath',str(jar),'-c','-p',cl],capture_output=True,text=True,timeout=90,check=True)
   method='';uses=[]
   for line in proc.stdout.splitlines():
    stripped=line.strip()
    if line.startswith('  ') and not line.startswith('    ') and (stripped.endswith(');') or stripped=='static {};'):
     method=stripped
    match=re.match(r'^\s*(\d+):\s+(ldc(?:_w|2_w)?)\s+#(\d+)\s+// String',line)
    if match:
     n=int(match[3]);literal=pool.get(n)
     if literal is None:raise ValueError(('Bad CONSTANT_String reference',cl,n))
     uses.append({'method':method,'offset':int(match[1]),'opcode':match[2],'cp_index':n,'literal':literal})
   unique_literals={x['literal'] for x in uses}
   if len(uses)!=expected_uses or len(unique_literals)!=unique:
    raise ValueError(('Original JVM literal inventory mismatch',cl,len(uses),len(unique_literals)))
   mapped=[r for r in source if r['source_class']==cl]
   if len(mapped)!=CLASSES[cl] or any(r['english_literal'] not in unique_literals for r in mapped):
    raise ValueError(('Existing source translations not backed by JVM',cl))
   addkeys={en for cc,en in ADDITIONS if cc==cl}
   if addkeys & {r['english_literal'] for r in mapped} or not addkeys.issubset(unique_literals):
    raise ValueError(('New translations not backed by JVM',cl))
   if not TECHNICAL[cl].issubset(unique_literals) or TECHNICAL[cl] & (set(r['english_literal'] for r in mapped)|addkeys):
    raise ValueError(('Engine identifiers inadvertently localized',cl))
   picked=[]
   for en in [r['english_literal'] for r in mapped]+sorted(addkeys):
    evidence=[{k:v for k,v in u.items() if k!='literal'} for u in uses if u['literal']==en]
    if not evidence:raise ValueError(('No JVM callsite',cl,en))
    picked.append({'english_literal':en,'english_key_sha256':sha(en.encode()),'new_1066':en in addkeys,'uses':evidence})
   report[cl]={'class_sha256':sha(original),'jvm_ldc_uses':len(uses),'distinct_source_literals':len(unique_literals),
      'existing_map_strings':len(mapped),'new_ui_literals':len(addkeys),
      'unmapped_distinct_literals':len(unique_literals)-len(mapped)-len(addkeys),
      'technical_unmodified':sorted(TECHNICAL[cl]),'mapped_callsites':picked}
   totalload+=len(uses);allmapped+=len(picked)
 return {'release':'1.0.66','game':'0.98a-RC8','original_api_sha256':ORIGINAL_API,
  'total_original_jvm_ldc_uses':totalload,'total_map_literals_after':allmapped,
  'classes':report,'never_modify_java_opcode':True,'native_game_tests':'after_1_1_release'}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--jar',type=Path,required=True)
 p.add_argument('--worktree',type=Path,required=True);p.add_argument('--out',type=Path)
 a=p.parse_args();data=audit(a.jar,a.worktree)
 if a.out:a.out.write_text(json.dumps(data,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'release':'1.0.66','original_jvm_calls':data['total_original_jvm_ldc_uses'],
    'mapped_literals':data['total_map_literals_after'],'new_literals':sum(len([x for x in v['mapped_callsites'] if x['new_1066']]) for v in data['classes'].values())},indent=2))
