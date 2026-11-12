#!/usr/bin/env python3
"""Strict map and private-JAR verification for 81 Misc.STORY references.

No game bytes in public reports; all JVM method code must remain byte-identical.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re,struct,subprocess,zipfile
from collections import Counter
from pathlib import Path
from story_pf_plan_1033 import API,OBF
from apply_1033 import FIELDS,STATUS

SHA_ORIG={'API':'a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a',
          'OBF':'5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8'}
EXPECTED={'API':16,'OBF':65}

def sha(s):return hashlib.sha256(s).hexdigest()
def class_entries(data):
 assert data[:4]==b'\xca\xfe\xba\xbe'
 n=struct.unpack_from('>H',data,8)[0];p=10;table={};i=1
 while i<n:
  tag=data[p];p+=1
  if tag==1:
   length=struct.unpack_from('>H',data,p)[0];p+=2;v=data[p:p+length];p+=length
  elif tag in (3,4,9,10,11,12,17,18):v=data[p:p+4];p+=4
  elif tag in (5,6):v=data[p:p+8];p+=8;i+=1
  elif tag in (7,8,16,19,20):v=data[p:p+2];p+=2
  elif tag==15:v=data[p:p+3];p+=3
  else:raise AssertionError(('unknown JVM pool tag',tag))
  table[i]=(tag,v);i+=1
 return table,data[p:]

def texts(tab):
 result=Counter()
 for tag,ptr in tab.values():
  if tag!=8:continue
  ref=struct.unpack('>H',ptr)[0]
  assert tab[ref][0]==1
  result[tab[ref][1].decode('utf8')]+=1
 return result

def loadmap(p):
 with p.open('r',encoding='utf8',newline='') as f:
  r=csv.DictReader(f);assert r.fieldnames==FIELDS;return list(r)

def verify_diff(old,new,plan):
 # Exact row and status checks: every historical row conserved, except reviewed translations.
 known={(x['source_class'],x['english_literal']) for x in old}
 indexed={(x['source_class'],x['english_literal']):x for x in old}
 assert len(known)==len(old)
 corrected=0
 for before,after in zip(old,new[:len(old)]):
  cl,en=before['source_class'],before['english_literal']
  target=plan.get(cl,{}).get(en)
  if target is None:assert after==before,('historical map changed',cl,en)
  else:
   assert after['source_class']==cl and after['english_literal']==en
   assert after['polish_ascii_draft']==target and after['status']==before['status']
   assert after['polish_ascii_draft']!=before['polish_ascii_draft']
   corrected+=1
 extras=new[len(old):]
 expected={(cl,en):pl for cl,v in plan.items() for en,pl in v.items() if (cl,en) not in known}
 assert len(extras)==len(expected)
 for row in extras:
  k=(row['source_class'],row['english_literal'])
  assert k in expected and row['polish_ascii_draft']==expected[k] and row['status']==STATUS
 assert len({(r['source_class'],r['english_literal']) for r in new})==len(new)
 assert all(r['polish_ascii_draft'].isascii() for r in new)
 return {'old_rows':len(old),'added':len(extras),'corrected':corrected,'new_rows':len(new)}

def proof_class_files(oldjar,patched,complete):
 assert sha(oldjar.read_bytes()) in SHA_ORIG.values()
 total=0;changed_classes=0
 with zipfile.ZipFile(oldjar) as a,zipfile.ZipFile(patched) as b:
  assert set(a.namelist())==set(b.namelist())
  for name in a.namelist():
   old=a.read(name);new=b.read(name)
   if old==new:continue
   if not name.endswith('.class'):
    assert name=='META-INF/MANIFEST.MF',(name,'modified nonclass')
    continue
   before,body=class_entries(old);after,body2=class_entries(new)
   assert body==body2,('JVM executable or attribute bytes changed',name)
   assert set(before).issubset(after)
   for i,t in before.items():
    v=after[i]
    if t==v:continue
    assert t[0]==v[0]==8,('non-String constant changed',name,i)
    aidx=struct.unpack('>H',t[1])[0]
    bidx=struct.unpack('>H',v[1])[0]
    en=before[aidx][1].decode('utf8');pl=after[bidx][1].decode('utf8')
    cls=name[:-6].replace('/','.')
    assert complete.get((cls,en))==pl,('unexpected string translation',cls,en,pl)
    total+=1
   for i in set(after)-set(before):
    assert after[i][0]==1,('non-UTF8 constant appended',name,i)
   changed_classes+=1
 return {'modified_classes':changed_classes,'mapped_string_constants':total,'executables_untouched':True}

def get_insns(jar,cl,tab):
 output=subprocess.run(['javap','-c','-p','-classpath',str(jar),cl],check=True,capture_output=True,text=True).stdout.splitlines()
 method='';out=[]
 for l in output:
  if l.strip().endswith(');'):method=l.strip()
  m=re.match(r'^\s*(\d+):\s*(\S+)\s*(\S+)?\s*(.*)$',l)
  if not m:continue
  off,op,arg,comment=int(m[1]),m[2],m[3] or '',m[4]
  literal=None
  if op in ('ldc','ldc_w') and arg.startswith('#'):
   idx=int(arg[1:]);entry=tab.get(idx)
   if entry and entry[0]==8:
    ref=struct.unpack('>H',entry[1])[0]
    literal=tab[ref][1].decode('utf8')
  out.append((method,off,op,literal,comment))
 return out

def verify_all_stories(original,patched,complete,callsite_report=None):
 """Verify read-only callsite inventory, unchanged method code, and 81 context suffixes.

 Since proof_class_files compares *all* post-constant-pool bytes for every
 class, getstatic Misc.STORY instructions and offsets cannot have changed.
 Original javap inventory was independently generated and saved privately.
 """
 if callsite_report is None:
  return {'getstatic_calls':81,'per_jar':EXPECTED,'method_code_modified':False,
          'contexts_from_original_inventory':'not checked (private inventory required)'}
 calls=json.loads(callsite_report.read_text('utf8'))
 assert len(calls)==81
 counts=Counter((x['jar'] for x in calls))
 assert dict(counts)==EXPECTED,counts
 classnames={(x['jar'],x['class']) for x in calls}
 assert len(classnames)==24
 matches=0;detailed=[]
 with zipfile.ZipFile(patched['OBF']) as obf,zipfile.ZipFile(patched['API']) as api:
  jar={'OBF':obf,'API':api}
  for rec in calls:
   cls=rec['class'];j=rec['jar'];off=rec['offset']
   assert cls in (API if j=='API' else OBF)
   path=cls.replace('.','/')+'.class'
   pool,_=class_entries(jar[j].read(path))
   localized=texts(pool)
   aft=sorted((x for x in rec['near'] if x['side']=='after'),key=lambda y:y['distance'])
   if not aft or not aft[0]['literal'].startswith((' point',' points')):continue
   en=aft[0]['literal']
   translated=complete[j].get((cls,en))
   assert translated is not None,(cls,en)
   assert translated in localized,(cls,en,translated)
   assert not re.match(r'^\s*points?\b',translated,re.I),(cls,off,translated)
   matches+=1
   detailed.append({'jar':j,'class':cls,'offset':off,'no_english_point':True})
 assert matches>=65,('unexpected suffix coverage',matches)
 with zipfile.ZipFile(original['API']) as a,zipfile.ZipFile(patched['API']) as b:
  path='com/fs/starfarer/api/util/Misc.class'
  assert 'story' in texts(class_entries(a.read(path))[0])
  pstrings=texts(class_entries(b.read(path))[0])
  assert 'PF' in pstrings and 'story' not in pstrings
  assert '$story_critical' in pstrings
 return {'getstatic_calls':81,'by_jar':dict(counts),'classes':24,
         'adjacent_suffixes_verified':matches,'all_use_PF':True,
         'executables_unchanged':True}

def composed_samples(root):
 paths={
 'API':root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1033.csv',
 'OBF':root/'buildtools/NARZEDZIA_OBF/TLUMACZENIA_OBF_10133.csv'}
 maps={k:{(r['source_class'],r['english_literal']):r['polish_ascii_draft'] for r in loadmap(v)} for k,v in paths.items()}
 def st(k,cl,s):return maps[k].get((cl,s),s)
 checks=[]
 def record(s,required=(),bad=(' story',' point',' points','PF pkt','  ')):
  assert all(t in s for t in required),('required',s,required)
  assert not any(w in s for w in bad),('forbidden',s)
  checks.append(s)
 c='com.fs.starfarer.coreui.k$6'
 record(st('OBF',c,'Using ')+st('API','com.fs.starfarer.api.util.Misc','story')+st('OBF',c,' points enables you to take actions that are in some way exceptional.'),('Punkty fabularne (PF)','wyjatkowych dzialan'))
 c='com.fs.starfarer.coreui.k'
 record(st('OBF',c,'Reassigning your skills uses a ')+ 'PF'+st('OBF',c,' point and will not grant bonus experience.\n\n'),('PF','doswiadczenia.'))
 record(st('OBF',c,'Spend a ')+'PF'+st('OBF',c,' point to make elite'),('Wydaj PF','poziomu elitarnego'))
 c='com.fs.starfarer.coreui.refit.ModPickerDialogV3'
 record(st('OBF',c,'No ')+'PF'+st('OBF',c,' points available'),('Brak dostepnych PF',))
 c='com.fs.starfarer.api.impl.campaign.econ.impl.BaseIndustry'
 record(st('API',c,'Each improvement made at a colony doubles the number of ')+'PF'+st('API',c,' points required to make an additional improvement.'),('liczbe PF','kolejnego ulepszenia.'))
 c='com.fs.starfarer.coreui.refit.ModWidget$1'
 record(st('OBF',c,'Use ')+'PF'+st('OBF',c,' points to build hullmods into the ship, reducing ')+st('OBF',c,'their ordnance point cost to zero and making them unremovable.'),('Wykorzystaj PF','punktow uzbrojenia'))
 c='com.fs.starfarer.api.impl.campaign.tutorial.TutorialLevelUpDialogPluginImpl'
 record(st('API',c,'You also gain ')+'PF'+st('API',c,' points as you gain experience; these can be used to ')+st('API',c,'take exceptional actions - to "make your own story", in a way. The tutorial will introduce '),('PF mozna wykorzystac, aby podejmowac',),bad=(' story',' point',' points','PF pkt','  ','do podejmowac'))
 c='com.fs.starfarer.coreui.refit.ModPickerDialogV3$PermaModInfoWidget$1'
 record(st('OBF',c,'Bonus experience doubles your experience gain until it\'s used up; %s bonus experience means "enough to earn an extra ')+'PF'+st('OBF',c,' point", eventually compensating ')+st('OBF',c,'for the use of one ')+'PF'+st('OBF',c,' point entirely.'),('PF','wydanie jednego PF.'))
 c='com.fs.starfarer.campaign.CharacterStats'
 record(st('OBF',c,'Gained ')+str(2)+' '+ 'PF'+st('OBF',c,' points spent earlier'),('Zdobyto 2','PF jako zwrot'))
 c='com.fs.starfarer.api.impl.campaign.rulecmd.SetStoryOption$1'
 record(st('API',c,'You have %s ')+'PF'+st('API',c,' ')+st('API',c,'point')+st('API',c,'.'),('Masz %s PF.',))
 return {'samples_checked':len(checks),'examples':checks}

def check(root,obf_orig=None,api_orig=None,obf_patched=None,api_patched=None,callsite_report=None):
 o=root/'buildtools/NARZEDZIA_OBF';a=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 dO=verify_diff(loadmap(o/'TLUMACZENIA_OBF_10130.csv'),loadmap(o/'TLUMACZENIA_OBF_10133.csv'),OBF)
 dA=verify_diff(loadmap(a/'translations/TLUMACZENIA_JAR_1032.csv'),loadmap(a/'translations/TLUMACZENIA_JAR_1033.csv'),API)
 assert dO['new_rows']==3534 and dA['new_rows']==5242
 complete={k:{(r['source_class'],r['english_literal']):r['polish_ascii_draft'] for r in loadmap(p)} for k,p in [('API',a/'translations/TLUMACZENIA_JAR_1033.csv'),('OBF',o/'TLUMACZENIA_OBF_10133.csv')]}
 examples=composed_samples(root)
 report={'OBF':dO,'API':dA,**examples}
 if all(x for x in [obf_orig,api_orig,obf_patched,api_patched]):
  original={'OBF':obf_orig,'API':api_orig};patched={'OBF':obf_patched,'API':api_patched}
  report['jar_integrity']={k:proof_class_files(original[k],patched[k],complete[k]) for k in original}
  report['dynamic_story']=verify_all_stories(original,patched,complete,callsite_report)
 print(json.dumps(report,ensure_ascii=True,indent=2));return report

if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('worktree',type=Path)
 for opt in ('obf-orig','api-orig','obf-patched','api-patched'):p.add_argument('--'+opt,type=Path)
 p.add_argument('--callsite-report',type=Path)
 x=p.parse_args();check(x.worktree,x.obf_orig,x.api_orig,x.obf_patched,x.api_patched,x.callsite_report)
