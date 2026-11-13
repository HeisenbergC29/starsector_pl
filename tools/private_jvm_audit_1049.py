#!/usr/bin/env python3
"""Optional private-JAR audit for Starsector 0.98a-RC8; game files never uploaded."""
import argparse,zipfile,struct,hashlib,re,subprocess,json
from pathlib import Path
from apply_1049 import readmap,plan,SALVOR,OLD,NEW,sha

def cp_split(data):
 if data[:4]!=b'\xca\xfe\xba\xbe':raise ValueError('Not Java class')
 n=struct.unpack_from('>H',data,8)[0];pos=10;items=[None]*n;refs=set();i=1
 while i<n:
  start=pos;tag=data[pos];pos+=1
  if tag==1:
   k=struct.unpack_from('>H',data,pos)[0];pos+=2+k
  elif tag in (3,4,9,10,11,12,17,18):pos+=4
  elif tag in (5,6):pos+=8
  elif tag in (7,8,16,19,20):
   if tag==8:refs.add(struct.unpack_from('>H',data,pos)[0])
   pos+=2
  elif tag==15:pos+=3
  else:raise ValueError(('Invalid JVM CP tag',tag,i))
  items[i]=(tag,data[start+1:pos],data[start:pos]);
  if tag in (5,6):i+=1
  i+=1
 return items,pos,refs

def class_strings(data):
 items,tail,refs=cp_split(data);found=[]
 for i,x in enumerate(items):
  if not x or x[0]!=8:continue
  ref=struct.unpack('>H',x[1])[0]
  if items[ref] is None or items[ref][0]!=1:raise ValueError('Broken String ref')
  raw=items[ref][1];length=struct.unpack_from('>H',raw,0)[0]
  found.append(raw[2:2+length].decode('utf8'))
 return found

def class_structure_check(source,patched):
 a,at,arefs=cp_split(source);b,bt,brefs=cp_split(patched)
 if source[at:]!=patched[bt:]:raise ValueError('Changed executable Java bytecode or structure')
 if len(b)<len(a):raise ValueError('CP shrank')
 changes=0
 for i,(x,y) in enumerate(zip(a,b)):
  if x==y:continue
  if x is None or y is None:raise ValueError('CP null changed')
  if x[0]!=y[0]:raise ValueError('CP kind changed')
  if x[0]==1 and i in arefs:pass
  elif x[0]==8 and len(x[1])==len(y[1])==2:pass
  else:raise ValueError(('Not authorized CP String patch',i,x[0]))
  changes+=1
 for x in b[len(a):]:
  if x is not None and x[0]!=1:raise ValueError('Non-UTF8 CP append')
 return changes

def audit(original_api,patched_api,mapping,static_ids=(),previous_api=None):
 old=readmap(mapping)
 plan_file=Path(__file__).parent.parent/'docs/API_TEXT_CORRECTIONS_1049.json';edits,extra,_=plan(readmap(Path(mapping).with_name(OLD)),plan_file)
 originals={r['source_class']:set() for r in old if r['source_class'].startswith('com.fs.starfarer.')}
 checked=set();changed=[]
 with zipfile.ZipFile(original_api) as a,zipfile.ZipFile(patched_api) as b:
  if set(a.namelist())!=set(b.namelist()):raise ValueError('Changed JAR member inventory')
  matches={};keys={(cl,en) for cl,en in edits}|{(SALVOR,'s')}|set(static_ids)
  for cl,en in sorted(keys):
   entry=cl.replace('.','/')+'.class'
   if entry not in a.namelist():raise ValueError(('Missing original JVM class',entry))
   strings=class_strings(a.read(entry))
   if strings.count(en)!=1:raise ValueError(('Original source literal not unique',cl,en,strings.count(en)))
   matches[(cl,en)]=True
  for name in a.namelist():
   x=a.read(name);y=b.read(name)
   if x==y:continue
   if not name.endswith('.class'):raise ValueError(('Non-class JAR member changed',name))
   class_structure_check(x,y)
   changed.append(name)
 # Explicit bytecode evidence: SalvorsTallyIntel suffix literal loaded 6 times,
 # all in the pluralizing lines of addPostDescriptionSection.
 javap=subprocess.check_output(['javap','-classpath',str(original_api),'-c','-p',SALVOR],text=True)
 suffix_uses=re.findall(r'^\s*\d+:\s+ldc\s+#128\s+// String s\s*$',javap,re.M)
 if len(suffix_uses)!=6:raise ValueError(('Unexpected plural suffix callsites',len(suffix_uses)))
 if len(changed)!=938:raise ValueError(('Expected 938 patched classes vs original',len(changed)))
 with zipfile.ZipFile(previous_api) as prev,zipfile.ZipFile(patched_api) as current:
  delta=[]
  for name in prev.namelist():
   if prev.read(name)!=current.read(name):
    if not name.endswith('.class'):raise ValueError('Non-class delta between versions')
    class_structure_check(prev.read(name),current.read(name));delta.append(name)
  if len(delta)!=7:raise ValueError(('Unexpected class count vs 1.0.48',len(delta)))
 return {'original_jar_sha256':sha(Path(original_api).read_bytes()),'patched_jar_sha256':sha(Path(patched_api).read_bytes()),
         'verified_original_constant_strings':len(matches),'patched_classes':len(changed),'newly_changed_classes':len(delta),'suffix_ldc_uses':len(suffix_uses),
         'suffix_pl_translation':'', 'no_java_executable_code_changed':True,'native_windows_gameplay_tested':False,
         'changed_classes_from_1048':delta}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--original-api',type=Path,required=True);p.add_argument('--patched-api',type=Path,required=True);p.add_argument('--previous-api',type=Path,required=True);p.add_argument('--map',type=Path,required=True);p.add_argument('--static-review',type=Path)
 a=p.parse_args();ids=[]
 if a.static_review:
  j=json.loads(a.static_review.read_text());ids=[(x['source_class'],x['english_literal']) for x in j['reviewed']]
 print(json.dumps(audit(a.original_api,a.patched_api,a.map,ids,a.previous_api),indent=2))
