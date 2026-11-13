#!/usr/bin/env python3
"""Private original-Starfarer-API proof: exact constant IDs, ldc uses and no bytecode changes.

Only hashes/indexes/source strings in output; NEVER ship the commercial JAR.
"""
from __future__ import annotations
import argparse,hashlib,json,re,subprocess,zipfile
from pathlib import Path
from apply_1055 import BLOCK,KNIGHTS,GENERIC,ADDITIONS,REPAIRS,OLD,NEW
from apply_1054 import readmap,sha
from verify_review_1055 import chosen
from private_jvm_1051 import parse_class,getstr,verify_literal_only
ORIGINAL='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
PREVIOUS='b5c256c78f92fb174456cb297660945d81690c33d21d513627b0547ed783eb14'

def run(root,previous_review,original,prior,current):
 root=Path(root);original,prior,current=map(Path,(original,prior,current))
 if sha(original.read_bytes())!=ORIGINAL or sha(prior.read_bytes())!=PREVIOUS:
  raise ValueError('Unexpected proprietary original or previous JAR')
 if sha(current.read_bytes())==PREVIOUS:raise ValueError('New patch has no effect')
 _,selected=chosen(root,previous_review)
 updated=readmap(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'/NEW)
 mapkeys={(r['source_class'],r['english_literal']):r for r in updated}
 target=[mapkeys[k] for k in sorted(set(ADDITIONS)|set(REPAIRS))]
 if len(target)!=10:raise ValueError('Wrong new map target inventory')
 classes={BLOCK,KNIGHTS,GENERIC}
 with zipfile.ZipFile(original) as a,zipfile.ZipFile(prior) as b,zipfile.ZipFile(current) as c:
  names=a.namelist()
  if names!=b.namelist() or names!=c.namelist() or any(z.testzip() for z in (a,b,c)):
   raise ValueError('ZIP structure/order or CRC changed')
  changed={name for name in names if b.read(name)!=c.read(name)}
  want={cl.replace('.','/')+'.class' for cl in classes}
  if changed!=want:raise ValueError(('Unexpected JVM entries changed',sorted(changed^want)))
  out=[];historical=[];summaries=[]
  for cl in sorted(classes):
   path=cl.replace('.','/')+'.class';orig,old,new=(z.read(path) for z in (a,b,c))
   verify_literal_only(old,new,path)   # 0 added executable instructions
   cp,_,_=parse_class(orig)
   vals={i:getstr(orig,cp,i) for i,e in enumerate(cp) if e and e[0]==8}
   code=subprocess.check_output(['javap','-cp',str(original),'-p','-c',cl],text=True,timeout=45)
   translated=[r for r in target if r['source_class']==cl]
   reviewed=[r for r in selected if r['source_class']==cl]
   for row,records in [(r,out) for r in translated]+[(r,historical) for r in reviewed]:
    en=row['english_literal'];ids=[i for i,v in vals.items() if v==en]
    if len(ids)!=1:raise ValueError(('Ambiguous original CONSTANT_String',cl,en,ids))
    i=ids[0]
    cnt=len(re.findall(r'^\s*\d+:\s+ldc(?:_w)?\s+#'+str(i)+r'\s+// String',code,re.M))
    if cnt<1:raise ValueError(('String not actually used by JVM',cl,en))
    finalcp,_,_=parse_class(new)
    final=getstr(new,finalcp,i)
    if final!=row['polish_ascii_draft']:raise ValueError(('CP field not translated',cl,en,final))
    records.append({'class':cl,'english':en,'polish':row['polish_ascii_draft'],'constant_index':i,
      'original_ldc_uses':cnt,'original_class_sha256':sha(orig),'source_status':row['status']})
   summaries.append({'class':cl,'original_class_sha256':sha(orig),'previous_class_sha256':sha(old),
     'new_class_sha256':sha(new),'new_literal_changes':len(translated),
     'historical_reviewed_count':len(reviewed),'all_executable_instructions_unchanged':True})
  if len(out)!=10 or len(historical)!=48:raise ValueError('Lost original constant evidence')
 return {'release':'1.0.55','original_api_sha256':ORIGINAL,'previous_api_sha256':PREVIOUS,
  'current_api_sha256':sha(current.read_bytes()),'changed_java_classes':3,
  'new_jvm_executable_bytecode_changes':0,
  'reviewed_historical_source_literals':48,'new_literal_and_corrected_rows':10,
  'exact_original_constant_and_ldc_evidence':out,
  'previous_draft_reviews_original_ldc_evidence':historical,
  'changed_class_summaries':summaries,'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--worktree',type=Path,required=True)
 for s in ('previous-review','original','prior','current','report'):p.add_argument('--'+s,type=Path,required=True)
 a=p.parse_args();result=run(a.worktree,a.previous_review,a.original,a.prior,a.current)
 a.report.write_text(json.dumps(result,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 print(json.dumps({k:v for k,v in result.items() if not isinstance(v,list)},indent=2))
