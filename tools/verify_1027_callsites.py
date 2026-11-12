#!/usr/bin/env python3
"""Private-original-only audit: verify all mapped JVM strings occur at ldc callsites.

Do not publish literal dumps or original JAR. Only counts and class names.
"""
import argparse,hashlib,json,re,subprocess,sys,zipfile
from pathlib import Path
from apply_1027 import OBF,API
from audit_1015_jars import parse_class,EXPECTED_ORIG

def check(label,jar,mapping):
 assert hashlib.sha256(jar.read_bytes()).hexdigest()==EXPECTED_ORIG[label]
 stats={'classes':0,'approved_strings':0,'ldc_references':0,'method_scoped_ldc':0}
 with zipfile.ZipFile(jar) as z:
  for cl,changes in mapping.items():
   raw=z.read(cl.replace('.','/')+'.class');pool,_=parse_class(raw)
   strings={pool[x[3]][2].decode('utf8') for x in pool if x and x[0]==8 and pool[x[3]] and pool[x[3]][0]==1}
   assert set(changes)<=strings,(cl,'not in original pool',set(changes)-strings)
   p=subprocess.run(['javap','-c','-p','-classpath',str(jar),cl],text=True,capture_output=True)
   assert p.returncode==0,(cl,p.stderr[:200]);by={v:0 for v in changes}
   for line in p.stdout.splitlines():
    if '// String ' in line and re.search(r'\bldc(?:_w|_2_w)?\s+#\d+',line):
     literal=line.split('// String ',1)[1]
     if literal in by:by[literal]+=1
   assert all(by.values()),(cl,'no Java ldc usage',[(k,v) for k,v in by.items() if not v])
   stats['classes']+=1;stats['approved_strings']+=len(changes);stats['ldc_references']+=sum(by.values())
 return stats

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--obf',type=Path,required=True);p.add_argument('--api',type=Path,required=True)
 p.add_argument('--out',type=Path);args=p.parse_args()
 res={'OBF':check('OBF',args.obf,OBF),'API':check('API',args.api,API)}
 assert res['OBF']['approved_strings']==41 and res['API']['approved_strings']==30
 if args.out: args.out.write_text(json.dumps(res,indent=2)+'\n',encoding='utf8')
 print(json.dumps(res,indent=2))