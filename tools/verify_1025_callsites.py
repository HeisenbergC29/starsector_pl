#!/usr/bin/env python3
"""Prove original JVM CONSTANT_String and bytecode ldc for all 81 OBF changes.

Requires private source jar and JDK javap; never include source jar in repository.
This check does not prove every execution path is reachable in all game modes.
"""
import argparse,hashlib,os,re,subprocess,zipfile,json
from pathlib import Path
from apply_1025 import OBF
from audit_1015_jars import parse_class,EXPECTED_ORIG

def main(jar,out):
 assert hashlib.sha256(jar.read_bytes()).hexdigest()==EXPECTED_ORIG['OBF']
 counts={}
 with zipfile.ZipFile(jar) as z:
  for cl, pairs in OBF.items():
   cp,_=parse_class(z.read(cl.replace('.','/')+'.class'))
   available={cp[node[3]][2].decode('utf8') for node in cp if node and node[0]==8 and cp[node[3]][0]==1}
   assert set(pairs).issubset(available),(cl,set(pairs)-available)
   p=subprocess.run(['javap','-c','-p','-classpath',str(jar),cl],capture_output=True,text=True,timeout=35)
   assert p.returncode==0,(cl,p.stderr)
   seen={}
   for en in pairs:
    # javap removes terminal whitespace in comments and prints ldc[_w] opcodes.
    pattern=re.compile(r'\bldc(?:_w)?\s+#\d+\s+// String '+re.escape(en.rstrip())+r'\s*$',re.M)
    seen[en]=len(pattern.findall(p.stdout))
    assert seen[en]>=1,(cl,repr(en),'missing display-linked ldc in bytecode')
   counts[cl]={'approved_labels':len(pairs),'total_ldc_sites':sum(seen.values())}
 report={'original_obf_sha256':EXPECTED_ORIG['OBF'],'classes':counts,
         'approved_labels':sum(x['approved_labels'] for x in counts.values()),
         'limitations':'StringBuilder and UI codepaths verified in bytecode; not a runtime game playtest. Short strings can have multiple consumers.'}
 assert report['approved_labels']==81
 out.write_text(json.dumps(report,indent=2,ensure_ascii=True)+'\n',encoding='utf8')
 print(json.dumps({'approved_labels':81,'classes':len(counts),'total_ldc_sites':sum(x['total_ldc_sites'] for x in counts.values())},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--obf',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();main(a.obf,a.out)