#!/usr/bin/env python3
"""Strict 1.0.32 map/assembled sentence regression; optional private original and patched JAR proof.

No commercial data is committed. When given private JARs, compare every Java
class's post-constant-pool bytes to prove executable code is identical.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re,struct,zipfile
from collections import Counter
from pathlib import Path
from apply_1032 import CORRECTIONS,NEW,edits,FIELDS

ORIGINAL_API='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
PATCHED_1030='f1927b0fbea90e41c049e95b954f97acfcf9e59496c89371b774ad0e12cea4e6'

def sha(b):return hashlib.sha256(b).hexdigest()
def readrows(p):
 with p.open('r',encoding='utf8',newline='') as f:
  r=csv.DictReader(f);assert r.fieldnames==FIELDS
  return list(r)

def cp_class(data):
 assert data[:4]==b'\xca\xfe\xba\xbe'
 n=struct.unpack_from('>H',data,8)[0];pos=10;table={};i=1
 while i<n:
  tag=data[pos];pos+=1
  if tag==1:
   length=struct.unpack_from('>H',data,pos)[0];pos+=2;v=data[pos:pos+length];pos+=length
  elif tag in (3,4,9,10,11,12,17,18):v=data[pos:pos+4];pos+=4
  elif tag in (5,6):v=data[pos:pos+8];pos+=8;i+=1
  elif tag in (7,8,16,19,20):v=data[pos:pos+2];pos+=2
  elif tag==15:v=data[pos:pos+3];pos+=3
  else:raise AssertionError(('JVM tag',tag))
  table[i]=(tag,v);i+=1
 return table,data[pos:]

def strings(table):
 output=Counter()
 for i,(tag,val) in table.items():
  if tag==8:
   ref=struct.unpack('>H',val)[0]
   assert table[ref][0]==1
   output[table[ref][1].decode('utf8')]+=1
 return output

def compare_jars(original:Path,patched:Path,newmap):
 assert sha(original.read_bytes())==ORIGINAL_API
 changes=0;changed_classes=0; changed_entries=[];seen=set()
 with zipfile.ZipFile(original) as a,zipfile.ZipFile(patched) as b:
  assert set(a.namelist())==set(b.namelist()),'JAR entry set changed'
  for name in a.namelist():
   old=a.read(name);new=b.read(name)
   if old==new:continue
   if not name.endswith('.class'):
    assert name=='META-INF/MANIFEST.MF',('unexpected non-class change',name)
    continue
   before,tail=cp_class(old);after,tail2=cp_class(new)
   assert tail==tail2,('Java code/attributes modified',name)
   assert set(before).issubset(after),('constant index removed',name)
   for i,t in before.items():
    nt=after[i]
    if t==nt:continue
    assert t[0]==nt[0]==8,('non-String constant changed',name,i,t[0],nt[0])
    oldtext=before[struct.unpack('>H',t[1])[0]][1].decode('utf8')
    newtext=after[struct.unpack('>H',nt[1])[0]][1].decode('utf8')
    cl=name[:-6].replace('/','.')
    assert (cl,oldtext) in newmap,('unmapped change',cl,repr(oldtext))
    assert newmap[(cl,oldtext)]==newtext,('unexpected translation',cl,repr(oldtext),repr(newtext))
    changes+=1
    seen.add((cl,oldtext))
   for i in set(after)-set(before):
    assert after[i][0]==1,('unexpected appended constant',name,i,after[i][0])
   changed_classes+=1
  for (cl,en),pl in newmap.items():
   path=cl.replace('.','/')+'.class'
   if path not in a.namelist():continue  # two historic unmatched API map entries
   oldstrings=strings(cp_class(a.read(path))[0]);newstrings=strings(cp_class(b.read(path))[0])
   assert en in oldstrings and pl in newstrings and en not in newstrings,(cl,en,pl)
 return {'modified_classes':changed_classes,'modified_constant_string_refs':changes,'mapped_sites_seen':len(seen),'new_1032_sites':len(seen & set(newmap))}

def check(root:Path,original=None,patched=None):
 p=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 old=readrows(p/'TLUMACZENIA_JAR_1030.csv');new=readrows(p/'TLUMACZENIA_JAR_1032.csv')
 assert len(old)==5219 and len(new)==5225
 assert [(r['source_class'],r['english_literal']) for r in new[:5219]]==[(r['source_class'],r['english_literal']) for r in old]
 approved={(cl,en):(prior,target) for cl,entries in CORRECTIONS.items() for en,(prior,target) in entries.items()}
 assert len(approved)==edits()==25
 for oldrow,newrow in zip(old,new[:len(old)]):
  key=(oldrow['source_class'],oldrow['english_literal'])
  if key not in approved:assert oldrow==newrow,('unapproved historical change',key)
  else:
   prior,target=approved[key]
   assert oldrow['polish_ascii_draft']==prior and newrow['polish_ascii_draft']==target
   assert newrow['status']==oldrow['status']
 for row in new[5219:]:
  cl,en,pl=row['source_class'],row['english_literal'],row['polish_ascii_draft']
  assert NEW.get(cl,{}).get(en)==pl
  assert row['status']=='VERIFIED_COMPOSED_FUEL_TOOLTIP_1032'
 assert len({(r['source_class'],r['english_literal']) for r in new})==len(new)
 assert all(r['polish_ascii_draft'].isascii() for r in new)
 # Exact compositions from three original JVM StringBuilder pipelines.
 for cls in NEW:
  rowmap={r['english_literal']:r['polish_ascii_draft'] for r in new if r['source_class']==cls}
  pre='Jumping into hyperspace consumes %s light ' if cls.endswith('FractureJumpAbility') else 'Consumes %s light '
  suffixes=[' worth of fuel and reduces the combat readiness ']
  if cls.endswith('DurationAbilityWithCost2'):suffixes.append(' worth of fuel.')
  for qty,year in [('1',"year's"),('2',"years'")]:
   for suffix in suffixes:
    sentence=rowmap[pre].replace('%s',qty)+rowmap[year]+rowmap[suffix]
    assert 'roku swietlnego' in sentence if qty=='1' else 'lat swietlnych' in sentence
    assert not any(w in sentence for w in ("year's","years'",'worth of fuel','jednostek paliwa','latom swietlnym'))
    assert not re.search(r'\s{2,}',sentence)
    assert sentence.startswith(('Zuzywa paliwo','Skok w nadprzestrzen'))
 mod=root/'mod';meta=json.loads((mod/'mod_info.json').read_text())
 assert meta['version']=='1.0.32' and meta['gameVersion']=='0.98a-RC8' and len(meta['replace'])==41
 assert len(list(x for x in (mod/'data').rglob('*') if x.is_file()))==870
 go=(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go').read_text()
 assert 'const version = "1032"' in go and '"1030", version}' in go
 obf=(root/'buildtools/NARZEDZIA_OBF/main.go').read_text()
 assert 'const currentPatchState = "patched 10130"' in obf
 out={'new_entries':6,'corrected_existing_entries':25,'map_rows':5225,'assembled_templates_checked':8,'unchanged_data_files':870,'jar_code_integrity':'not checked (private JARs required)'}
 if original is not None and patched is not None:
  d={ (cl,en):target for cl,entries in CORRECTIONS.items() for en,(prev,target) in entries.items() }
  d.update({(cl,en):pl for cl,pairs in NEW.items() for en,pl in pairs.items()})
  # In addition to new corrections, full JAR includes all historical map entries.
  complete={(r['source_class'],r['english_literal']):r['polish_ascii_draft'] for r in new}
  jar=compare_jars(original,patched,complete)
  assert jar['new_1032_sites']==5223 and jar['modified_classes']==938
  assert all(key in complete for key in d)
  out['jar_proof']=jar;out['jar_code_integrity']='PASS: all Java method bytes unchanged'
 print(json.dumps(out,indent=2));return out

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('worktree',type=Path);ap.add_argument('--original',type=Path);ap.add_argument('--patched',type=Path)
 a=ap.parse_args();check(a.worktree,a.original,a.patched)
