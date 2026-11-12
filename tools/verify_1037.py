#!/usr/bin/env python3
"""Strict mapping and optional complete class-pool proof for Starsector PL 1.0.37.

Six independently reconstructed on/ona fragments from the original JVM. None
of these checks claim native Windows UI/gameplay validation.
"""
from __future__ import annotations
import argparse,collections,csv,hashlib,json,re,subprocess,zipfile
from pathlib import Path
from apply_1037 import FIELDS,CORRECT,NEW,CALLS,STATUS
from verify_story_1033 import proof_class_files,class_entries,texts

ORIGINAL_SHA='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
PATCHED_SHA='5eb063221593fd4c9edecd5da37f024a01f87f3fd9e411a74b187fc09d7646e1'
BASE='com.fs.starfarer.api.impl.campaign.intel.bar.events.BaseBarEventWithPerson'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def rows(p):
 with p.open('r',encoding='utf8',newline='') as f:
  x=csv.DictReader(f);assert x.fieldnames==FIELDS
  return list(x)

def mapdiff(root):
 a=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';t=a/'translations'
 prior=rows(t/'TLUMACZENIA_JAR_1036.csv');current=rows(t/'TLUMACZENIA_JAR_1037.csv')
 assert len(prior)==5244 and len(current)==5245
 wanted={(cl,en):(before,after) for cl,items in CORRECT.items() for en,(before,after) in items.items()}
 found=set()
 for before,after in zip(prior,current):
  key=(before['source_class'],before['english_literal'])
  if key not in wanted: assert before==after,('unexpected historical change',key)
  else:
   old,new=wanted[key]
   assert before['polish_ascii_draft']==old and after['polish_ascii_draft']==new
   assert before['status']==after['status'] and before['english_literal']==after['english_literal']
   found.add(key)
 assert found==set(wanted) and len(found)==5
 assert current[-1]=={'source_class':next(iter(NEW)), 'english_literal':' says. ',
                     'polish_ascii_draft':' mowi. ', 'status':STATUS}
 keys=[(r['source_class'],r['english_literal']) for r in current]
 assert len(set(keys))==len(keys) and all(r['polish_ascii_draft'].isascii() for r in current)
 assert not any(c==BASE and e in ('her','him','his') for c,e in keys)
 assert 'const version = "1037"' in (a/'main.go').read_text('utf8')
 assert '"1033", "1036", version}' in (a/'main.go').read_text('utf8')
 assert 'const edition = "1.0.37"' in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8')
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 assert meta['version']=='1.0.37' and meta['gameVersion']=='0.98a-RC8' and len(meta['replace'])==41
 data=list((root/'mod/data').rglob('*'));files=[x for x in data if x.is_file()]
 assert len(files)==870 and all(x.read_bytes().isascii() for x in files)
 return {'corrected_existing_api':5,'added_api':1,'api_map_rows':5245,'data_files':870}

def phrases():
 a={cl:{en:after for en,(_,after) in items.items()} for cl,items in CORRECT.items()}
 a.update(NEW)
 cl=list(CORRECT)
 # Every test assembles with both getter outputs and surrounding exact fragments.
 # No simulated outcomes for other, unresolved getters in the same screen.
 results={}
 for sex,p in [('male','on'),('female','ona')]:
  cap=p.capitalize()
  s={
   'contact': 'Jesli rozwiniesz ten kontakt, '+p+a[cl[0]][' will periodically ']+'bedzie miec dla ciebie zadania.',
   'delivery':'"Umiesz sie targowac! Dobrze, umowa stoi." '+cap+a[cl[1]][' does not appear too displeased. You consider that the initial offer ']+'byla zapewne zanizona.',
   'scientist_bar':'Wyglada na to, ze '+p+a[cl[2]][' was a bit unhinged, after all - ']+'nie ma tu niczego wartego zbadania.',
   'scientist_intel':'Zatrzymujesz dla siebie rdzen SI obiecany naukowcowi. Zapewne '+p+a[cl[3]][' was no-one important.'],
   'tritach_loan':p+a[cl[4]][' seems thrown off-balance by your savvy, and never quite recovers that signature megacorp implacability.'],
   'tritach_major':'"Ten rocznik pochodzi sprzed Upadku, wiesz?" - '+p+a[next(iter(NEW))][' says. ']+'"Podoba mi sie mysl o posiadaniu malego udzialu w historii."'
  }
  assert len(s)==6
  for name,v in s.items():
   assert v.isascii() and '  ' not in v and '\n' not in v
   assert not any(f in v for f in (' bedzie okresowo bedzie',' niezadowolonego',' nie mial',' nie byl',' wydaje sie wytracony',' says. '))
   assert ((' '+p+' ') in v or v.startswith(p+' ') or (' '+cap+' ') in v),(name,sex,v)
  results[sex]=s
 return results

def verify_jars(original,patched,root):
 assert sha(original)==ORIGINAL_SHA and sha(patched)==PATCHED_SHA
 mapping={(r['source_class'],r['english_literal']):r['polish_ascii_draft'] for r in rows(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1037.csv')}
 structural=proof_class_files(original,patched,mapping)
 assert structural['modified_classes']==938 and structural['mapped_string_constants']==5243
 with zipfile.ZipFile(original) as x,zipfile.ZipFile(patched) as y:
  for cl,mp in CORRECT.items():
   name=cl.replace('.','/')+'.class';e=texts(class_entries(x.read(name))[0]);p=texts(class_entries(y.read(name))[0])
   for en,(before,after) in mp.items():
    assert en in e and after in p and en not in p and before not in p,(cl,en)
  for cl,mp in NEW.items():
   name=cl.replace('.','/')+'.class';e=texts(class_entries(x.read(name))[0]);p=texts(class_entries(y.read(name))[0])
   for en,after in mp.items():assert en in e and en not in p and after in p
  base=BASE.replace('.','/')+'.class'
  b=class_entries(x.read(base))[0];a=class_entries(y.read(base))[0]
  assert b[143]==a[143] and texts(b)['her']>=1 and texts(a)['her']>=1
 for cl,(_,offset) in CALLS.items():
  for jar in (original,patched):
   r=subprocess.run(['javap','-classpath',str(jar),'-c','-p',cl],capture_output=True,text=True,check=True)
   needle=re.compile(r'^\s*'+str(offset)+r':\s+invoke(?:virtual|interface)\s+#[0-9]+(?:,\s*\d+)?\s+// (?:Method|InterfaceMethod) [^\n]*getHeOrShe:',re.M)
   assert needle.search(r.stdout),('getter at offset changed',cl,offset)
 return {'real_jvm_getter_calls_checked':len(CALLS),'shared_her_pool_unchanged':True,
         'original_api_sha256':ORIGINAL_SHA,'patched_api_sha256':PATCHED_SHA,**structural}

def verify(root,original=None,patched=None,previous_zip=None):
 d=mapdiff(root);p=phrases();assert len(p['male'])==len(p['female'])==6
 d['composed_gender_variants']=12
 if previous_zip:
  with zipfile.ZipFile(previous_zip) as z:
   prior={k.removeprefix('Starsector_PL_ASCII/'):z.read(k) for k in z.namelist() if k.startswith('Starsector_PL_ASCII/data/')}
  current={f.relative_to(root/'mod').as_posix():f.read_bytes() for f in (root/'mod/data').rglob('*') if f.is_file()}
  assert prior==current and len(current)==870
  d['unchanged_data_files']=870
 if original or patched:
  assert original and patched
  d.update(verify_jars(original,patched,root))
 return d

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--original-api',type=Path);p.add_argument('--patched-api',type=Path)
 p.add_argument('--previous-zip',type=Path)
 q=p.parse_args();print(json.dumps(verify(q.worktree,q.original_api,q.patched_api,q.previous_zip),indent=2))
