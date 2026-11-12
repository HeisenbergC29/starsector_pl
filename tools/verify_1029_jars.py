#!/usr/bin/env python3
"""Audit a release's patched JARs against the corresponding commercial originals.
Only uses original binaries privately, does not include them in output.
"""
import argparse,zipfile,struct,hashlib,json,collections
from pathlib import Path

def split_class(data):
 assert data[:4]==b'\xca\xfe\xba\xbe'
 count=struct.unpack_from('>H',data,8)[0];pos=10;cp=[None];string_refs=set()
 idx=1
 while idx<count:
  start=pos;tag=data[pos];pos+=1
  if tag==1:
   n=struct.unpack_from('>H',data,pos)[0];pos+=2+n
  elif tag in (3,4,9,10,11,12,17,18):pos+=4
  elif tag in (5,6):pos+=8
  elif tag in (7,8,16,19,20):
   if tag==8:string_refs.add(struct.unpack_from('>H',data,pos)[0])
   pos+=2
  elif tag==15:pos+=3
  else:raise RuntimeError(f'unknown constant tag {tag}')
  cp.append((tag,data[start+1:pos]))
  if tag in (5,6):cp.append(None);idx+=1
  idx+=1
 return cp,string_refs,data[pos:]

def verify_class(orig,patched,jarname,entry):
 a,arefs,atail=split_class(orig);b,brefs,btail=split_class(patched)
 assert atail==btail,(jarname,entry,'executable class structure changed')
 assert len(b)>=len(a),(jarname,entry,'constant pool shrunk')
 bad=[];changed=0
 for i,(x,y) in enumerate(zip(a,b)):
  if x==y:continue
  if x is None:assert y is None;continue
  tag=x[0];assert y and y[0]==tag,(entry,i,'tag changed')
  if tag==1:assert i in arefs,(entry,i,'non-string UTF8 modified')
  elif tag==8:
   assert len(x[1])==2 and len(y[1])==2
  else:raise AssertionError((entry,i,'non-text CP entry changed',tag))
  changed+=1
 for i,y in enumerate(b[len(a):],len(a)):
  assert y is None or y[0]==1,(entry,i,'unexpected appended CP tag')
 return {'changed_cp_entries':changed,'new_cp_entries':len(b)-len(a)}

def verify_one(source,patched,kind):
 rs={'kind':kind,'original_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'patched_sha256':hashlib.sha256(patched.read_bytes()).hexdigest()}
 counter=collections.Counter();nchanged=0;changed_classes=[]
 with zipfile.ZipFile(source) as a, zipfile.ZipFile(patched) as b:
  originals=set(a.namelist());modified=set(b.namelist());assert originals==modified,kind
  for entry in sorted(originals):
   old=a.read(entry);new=b.read(entry)
   if old==new:counter['entries_unchanged']+=1;continue
   if entry.endswith('.class'):
    result=verify_class(old,new,kind,entry)
    for key,value in result.items():counter[key]+=value
    nchanged+=1;changed_classes.append(entry)
   elif kind=='OBF' and entry.upper()=='META-INF/MANIFEST.MF':
    counter['manifest_changed']+=1
   else:raise AssertionError((kind,entry,'unexpected non-class change'))
 rs['changed_classes']=nchanged
 rs.update(counter)
 return rs

if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--original-obf',type=Path,required=True)
 p.add_argument('--patched-obf',type=Path,required=True)
 p.add_argument('--original-api',type=Path,required=True)
 p.add_argument('--patched-api',type=Path,required=True)
 args=p.parse_args()
 r=[verify_one(args.original_obf,args.patched_obf,'OBF'),verify_one(args.original_api,args.patched_api,'API')]
 assert r[0]['changed_classes']==538,r[0]
 assert r[1]['changed_classes']==938,r[1]
 print(json.dumps(r,indent=2))
