#!/usr/bin/env python3
"""Read-only, private-original JAR and JVM method audit of 92 verified labels.

A valid CONSTANT_String is only a necessary condition for a UI translation;
this also requires at least one ldc in a reviewed UI method per class.
Never publish original commercial JARs or entire decompilation excerpts.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,re,subprocess,sys,zipfile
from pathlib import Path
from apply_1028 import OBF,API
from audit_1015_jars import parse_class,EXPECTED_ORIG
METHOD=re.compile(r'^  (?:public|private|protected|static|final|synchronized).*\);$')
LDC=re.compile(r'\bldc(?:_w)?\s+#\d+\s+// String (.*)$')
FIELD=re.compile(r'\bgetstatic .*Misc\.STORY')

def audit(label,jar,table):
 assert hashlib.sha256(jar.read_bytes()).hexdigest()==EXPECTED_ORIG[label]
 records=[];total=0
 with zipfile.ZipFile(jar) as z:
  for cl,labels in table.items():
   path=cl.replace('.','/')+'.class'
   cp,_=parse_class(z.read(path))
   originals={cp[x[3]][2].decode('utf8','replace') for x in cp if x and x[0]==8 and cp[x[3]] and cp[x[3]][0]==1}
   assert set(labels)<=originals,('missing source in original JVM CP',cl,set(labels)-originals)
   output=subprocess.run(['javap','-p','-c','-classpath',str(jar),cl],capture_output=True,text=True,check=True).stdout.splitlines()
   methods=collections.defaultdict(list);method=''
   for line in output:
    if METHOD.match(line):method=line.strip()
    if 'static {};' in line:method='[static initializer]'
    m=LDC.search(line)
    if not m:continue
    literal=m.group(1)
    # javap removes literal trailing spaces; the exact value comes from raw CP.
    for en in labels:
     if literal==en or literal==en.rstrip(' '):methods[en].append(method)
   assert set(methods)==set(labels),('unreferenced JVM literal or parser issue',cl,set(labels)-set(methods))
   for en,uses in methods.items():
    for name in uses:
     assert not re.search(r'\b(?:getIntelTags|getSortString|createPersonalityPicker)\s*\(',name),('technical callsite',cl,en,name)
   total+=sum(len(v) for v in methods.values())
   records.append({'class':cl,'strings_verified':len(labels),'ldc_refs':sum(map(len,methods.values())), 'methods':sorted({m for v in methods.values() for m in v})})
 return {'jar':label,'verified_original_sha256':EXPECTED_ORIG[label],'verified_classes':len(records),'verified_new_labels':sum(len(x) for x in table.values()),'ldc_refs':total,'classes':records}

def main():
 p=argparse.ArgumentParser();p.add_argument('--obf',type=Path,required=True);p.add_argument('--api',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();results=[audit('OBF',a.obf,OBF),audit('API',a.api,API)]
 assert results[0]['verified_new_labels']==64 and results[1]['verified_new_labels']==28
 assert results[0]['verified_classes']==18 and results[1]['verified_classes']==9
 out={'game_version':'0.98a-RC8','release':'1.0.28','status':'confirmed literal + LDC + reviewed UI method, not native runtime','jars':results}
 a.out.write_text(json.dumps(out,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 print(json.dumps({x['jar']:{'classes':x['verified_classes'],'labels':x['verified_new_labels'],'ldc_references':x['ldc_refs']} for x in results},indent=2))
if __name__=='__main__':main()