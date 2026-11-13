#!/usr/bin/env python3
"""Private JAR checker for the only allowed two-byte UI-specific JVM exception.

Independent of Go patcher. Compares all original/modified class tails and
CONSTANT_String indexes. Never publishes or copies game-owned class bytes.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,struct,zipfile
from pathlib import Path

CLASS='com/fs/starfarer/api/impl/campaign/FactionPersonalityPickerPluginImpl.class'
ORIGINAL_CLASS_SHA='f1c37918b1ae8542f5f3673775e9343e34bd04c3c075c2a5752f6433ef354949'
ORIGINAL_JAR_SHA='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
PATCHED_1050_SHA='35e086aed9380cf481bd6e48bfc29017cb5ee94012e5292953c9d53e44a540df'
EXPECTED_1051_SHA='cf26c3aa2885df954f4914b584ff1552b3b3c8f8d9290adfb8a03a9d6dff7a13'
PAT=bytes.fromhex('2b 12 52 25 19 04 05 bd 00 44 59 03 12 2c 53 59 04 12 2f 53')
def sha(b):return hashlib.sha256(b).hexdigest()
def u16(data,i):return struct.unpack_from('>H',data,i)[0]

def parse_class(data):
 if data[:4]!=b'\xca\xfe\xba\xbe':raise ValueError('Invalid class magic')
 total=u16(data,8);entries=[None]*total;pos=10;i=1;strRefs=set()
 while i<total:
  p=pos;tag=data[pos];pos+=1
  if tag==1:
   n=u16(data,pos);pos+=2+n
  elif tag in (3,4,9,10,11,12,17,18):pos+=4
  elif tag in (5,6):pos+=8
  elif tag in (7,8,16,19,20):
   if tag==8:strRefs.add(u16(data,pos))
   pos+=2
  elif tag==15:pos+=3
  else:raise ValueError(('Unknown JVM CP type',tag))
  if pos>len(data):raise ValueError('Truncated class')
  entries[i]=(tag,data[p+1:pos]);i+=2 if tag in (5,6) else 1
 return entries,strRefs,pos

def getstr(data,cp,index):
 if cp[index][0]!=8:raise ValueError(('Not string index',index))
 ref=u16(cp[index][1],0)
 if cp[ref][0]!=1:raise ValueError('Bad JVM UTF8 pointer')
 b=cp[ref][1];n=u16(b,0);return b[2:2+n].decode('utf8')

def verify_literal_only(original,translated,entry):
 a,refs,aend=parse_class(original);b,brefs,bend=parse_class(translated)
 if len(b)<len(a):raise ValueError(('Shrunk JVM CP',entry))
 if original[aend:]!=translated[bend:]:raise ValueError(('Executable method modified outside explicit exception',entry))
 for i in range(1,len(a)):
  aa=a[i];bb=b[i]
  if aa==bb:continue
  if aa is None:
   if bb is not None:raise ValueError(('Illegal JVM CP reserved slot',entry,i))
   continue
  if bb is None or aa[0]!=bb[0]:raise ValueError(('JVM constant kind changed',entry,i))
  if aa[0]==1:
   if i not in refs:raise ValueError(('Non-string JVM UTF8 modified',entry,i))
  elif aa[0]==8:
   if len(aa[1])!=2 or len(bb[1])!=2:raise ValueError('Corrupt CONSTANT_String reference')
  else:raise ValueError(('Changed a non-string JVM constant',entry,i,aa[0]))
 for i in range(len(a),len(b)):
  if b[i] is not None and b[i][0]!=1:raise ValueError(('Appended non-UTF8 CP entry',entry,i))
 return True

def verify(original_api,previous_api,new_api):
 originals=[Path(p).read_bytes() for p in (original_api,previous_api,new_api)]
 expect=[ORIGINAL_JAR_SHA,PATCHED_1050_SHA,EXPECTED_1051_SHA]
 if [sha(b) for b in originals]!=expect:raise ValueError('Original/previous/current JAR SHA mismatch')
 with zipfile.ZipFile(original_api) as old,zipfile.ZipFile(previous_api) as prev,zipfile.ZipFile(new_api) as new:
  keys=old.namelist()
  if keys!=prev.namelist() or keys!=new.namelist() or any(z.testzip() is not None for z in (old,prev,new)):
   raise ValueError('ZIP member/CRC mismatch')
  if CLASS not in keys:raise ValueError('Missing audited class')
  changed_prev_current=[];changed_orig=[]
  for k in keys:
   aa=old.read(k);bb=prev.read(k);cc=new.read(k)
   if bb!=cc:changed_prev_current.append(k)
   if aa==cc:continue
   if not k.endswith('.class'):raise ValueError(('Non-class entry changed',k))
   changed_orig.append(k)
   if k!=CLASS:
    verify_literal_only(aa,cc,k);continue
   if sha(aa)!=ORIGINAL_CLASS_SHA:raise ValueError('Original class SHA mismatch')
   acp,_,aend=parse_class(aa);bcp,_,bend=parse_class(bb);ccp,_,cend=parse_class(cc)
   for idx,en,pl in [(44,'aggressive','aggressive'),(47,'reckless','reckless'),(80,'Aggressive','Agresywny'),(84,'Reckless','Brawurowy')]:
    if getstr(aa,acp,idx)!=en or getstr(cc,ccp,idx)!=pl:raise ValueError(('Technical or UI personality CP was changed incorrectly',idx))
   if aa[aend:].count(PAT)!=1:raise ValueError('JVM UI bytecode pattern not unique in source')
   orig_tail=aa[aend:];prior_tail=bb[bend:];new_tail=cc[cend:]
   if prior_tail!=orig_tail:raise ValueError('Previous 1.0.50 already changed instructions')
   p=orig_tail.find(PAT)
   diffs=[i for i,(a,b) in enumerate(zip(orig_tail,new_tail)) if a!=b]
   if len(orig_tail)!=len(new_tail) or diffs!=[p+13,p+18] or new_tail[p+13:p+14]!=b'\x50' or new_tail[p+18:p+19]!=b'\x54':
    raise ValueError(('Unexpected JVM bytecode delta',diffs))
   restored=bytearray(cc);restored[cend+p+13]=0x2c;restored[cend+p+18]=0x2f
   verify_literal_only(aa,bytes(restored),k)
  if changed_prev_current != [CLASS]:raise ValueError(('More than one class differs since 1.0.50',changed_prev_current))
  if len(changed_orig)!=938:raise ValueError(('Unexpected number of translated classes',len(changed_orig)))
  return {'release':'1.0.51','changed_classes_against_original':len(changed_orig),
   'changed_classes_against_1050':1,'class_path':CLASS,
   'source_class_sha256':ORIGINAL_CLASS_SHA,
   'technical_ids_unchanged':['cautious','steady','aggressive','reckless'],
   'display_ldc_operands_modified':2,'display_ldc_cp_indices_before':[44,47],
   'display_ldc_cp_indices_after':[80,84],
   'other_executable_instruction_bytes_modified':0,
   'original_api_sha256':ORIGINAL_JAR_SHA,'previous_api_sha256':PATCHED_1050_SHA,
   'current_api_sha256':EXPECTED_1051_SHA,'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--original-api',type=Path,required=True);p.add_argument('--previous-api',type=Path,required=True);p.add_argument('--current-api',type=Path,required=True);p.add_argument('--report',type=Path)
 a=p.parse_args();result=verify(a.original_api,a.previous_api,a.current_api)
 if a.report:a.report.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
