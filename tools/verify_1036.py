#!/usr/bin/env python3
"""Strict 1.0.36 delta, one reflexive getter, composed Polish, optional real-JAR proof.

Never claim Windows gameplay coverage: only the original JAR + local patcher.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re,subprocess,zipfile
from pathlib import Path
from apply_1036 import BASE,EVENT,NEW,CORRECT,FIELDS,STATUS
from verify_story_1033 import class_entries,texts,proof_class_files

ORIG_API_SHA='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
PATCHED_API_SHA='892c20e354b0affa483894606461de4641e9afa3930b25ef83ba219e3f09a339'
DATA_COUNT=870

def sha(b):return hashlib.sha256(b).hexdigest()

def rows(p):
 with p.open('r',encoding='utf8',newline='') as f:
  r=csv.DictReader(f); assert r.fieldnames==FIELDS
  return list(r)

def mapdiff(root):
 a=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 old=rows(a/'translations/TLUMACZENIA_JAR_1033.csv')
 new=rows(a/'translations/TLUMACZENIA_JAR_1036.csv')
 assert len(old)==5242 and len(new)==5244
 expected={(cl,en):pl for cl,mp in CORRECT.items() for en,pl in mp.items()}
 corrected=set()
 for before,after in zip(old,new):
  k=(before['source_class'],before['english_literal'])
  target=expected.get(k)
  if target is None:assert before==after,('unapproved historical change',k)
  else:
   assert after['source_class']==before['source_class'] and after['english_literal']==before['english_literal']
   assert after['polish_ascii_draft']==target and after['status']==before['status']
   assert after['polish_ascii_draft']!=before['polish_ascii_draft']
   corrected.add(k)
 assert corrected==set(expected)
 extra=new[len(old):]
 assert len(extra)==2
 wanted={(cl,en):pl for cl,mp in NEW.items() for en,pl in mp.items()}
 assert {(r['source_class'],r['english_literal']):r['polish_ascii_draft'] for r in extra}==wanted
 assert all(r['status']==STATUS for r in extra)
 assert len({(r['source_class'],r['english_literal']) for r in new})==5244
 assert all(r['polish_ascii_draft'].isascii() for r in new)
 assert not any(r['source_class']==BASE and r['english_literal']=='her' for r in new),'Shared her cannot be patched safely'
 src=(a/'main.go').read_text('utf8')
 assert 'const version = "1036"' in src and 'const exeVersion = "1.0.36"' in src
 assert '"1032", "1033", version}' in src
 assert 'const edition = "1.0.36"' in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8')
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 assert meta['version']=='1.0.36' and meta['gameVersion']=='0.98a-RC8'
 assert len(meta['replace'])==41
 files={p.relative_to(root/'mod/data').as_posix():p for p in (root/'mod/data').rglob('*') if p.is_file()}
 assert len(files)==870 and all(p.read_bytes().isascii() for p in files.values())
 assert 'campaign/rules.csv' in files
 return {'prior_api_rows':5242,'new_api_rows':5244,'added_api':2,'corrected_api':4,'unchanged_obf_map':True,'localized_data_files':870}

def phrase(gender,first='Mara'):
 from_base=NEW[BASE]['himself' if gender=='male' else 'herself']
 # Build the same StringBuilder fragments, with a controlled noun and a visible
 # placeholder for MarketAPI.getOnOrAt() (a distinct, unreviewed dependency).
 result=('Stary kosmonauta opowiada ci, ze '+first+
         CORRECT[EVENT][' did not live the experience in such ']+
         CORRECT[EVENT]['stride as ']+from_base+
         CORRECT[EVENT][', and has taken to drinking themselves senseless ']+
         'na czesciowej emeryturze '+'<PRZYIMEK_LOKALIZACJI>'+' '+'<NAZWA_MIEJSCA>')
 assert result.startswith('Stary kosmonauta opowiada ci, ze '+first+' po tych wydarzeniach')
 assert (' niz on,' if gender=='male' else ' niz ona,') in result
 assert 'upija sie do nieprzytomnosci' in result
 assert 'himself' not in result and 'herself' not in result and 'krokiem' not in result
 return result

def verify_jars(orig,patched):
 assert sha(orig.read_bytes())==ORIG_API_SHA
 assert sha(patched.read_bytes())==PATCHED_API_SHA
 # A full method/attribute-by-attribute comparison is delegated to the already
 # independently tested 1.0.33 constant-pool validator.
 def pools(jar,cls):
  with zipfile.ZipFile(jar) as z:
   b=z.read(cls.replace('.','/')+'.class')
  t,_=class_entries(b)
  return texts(t),t
 enBase,tableBefore=pools(orig,BASE);plBase,tableAfter=pools(patched,BASE)
 for en,pl in NEW[BASE].items():
  assert en in enBase and pl in plBase
  assert en not in plBase,('untranslated getter value',en)
 assert enBase['her']==plBase['her'] and enBase['his']==plBase['his'] and enBase['him']==plBase['him'], 'Shared getter changed'
 a=tableBefore[143];b=tableAfter[143]
 assert a[0]==b[0]==8 and a==b, 'Shared her at #143 was altered'
 for jar in [orig,patched]:
  cmd=subprocess.run(['javap','-c','-p','-classpath',str(jar),EVENT],capture_output=True,check=True,text=True)
  calls=re.findall(r'^\s*(\d+):\s+invokevirtual\s+#[0-9]+\s+// Method getHimOrHerself:',cmd.stdout,re.M)
  assert calls==['663'],('Reflexive caller changed',calls)
  base=subprocess.run(['javap','-c','-p','-classpath',str(jar),BASE],capture_output=True,check=True,text=True).stdout
  assert re.search(r'(?s)getHimOrHer\(\).*?ldc\s+#143\s+// String her',base)
  assert re.search(r'(?s)getHisOrHer\(\).*?ldc\s+#143\s+// String her',base)
 enEvent,_=pools(orig,EVENT);plEvent,_=pools(patched,EVENT)
 for en,pl in CORRECT[EVENT].items():
  assert en in enEvent and pl in plEvent,('missing event fragment',en)
 return {'single_getHimOrHerself_jvm_callsite':True,'shared_her_intact':True,'original_sha256':ORIG_API_SHA,'patched_sha256':PATCHED_API_SHA}

def run(root,original=None,patched=None,previous_zip=None):
 d=mapdiff(root)
 a=phrase('male');b=phrase('female')
 assert a!=b and ' niz on,' in a and ' niz ona,' in b
 d['assembled_gender_variants']=2
 if previous_zip:
  with zipfile.ZipFile(previous_zip) as z:
   old={n.removeprefix('Starsector_PL_ASCII/data/'):z.read(n) for n in z.namelist() if n.startswith('Starsector_PL_ASCII/data/')}
  cur={p.relative_to(root/'mod/data').as_posix():p.read_bytes() for p in (root/'mod/data').rglob('*') if p.is_file()}
  assert len(old)==len(cur)==870 and old==cur, '1.0.36 must not modify data'
  d['data_identical_to_previous']=True
 if original or patched:
  assert original and patched
  full={(r['source_class'],r['english_literal']):r['polish_ascii_draft'] for r in rows(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1036.csv')}
  d.update(verify_jars(original,patched))
  structural=proof_class_files(original,patched,full)
  assert structural['modified_classes']==938 and structural['mapped_string_constants']==5242
  d.update(structural)
 return d

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--original-api',type=Path);p.add_argument('--patched-api',type=Path);p.add_argument('--previous-zip',type=Path)
 a=p.parse_args();print(json.dumps(run(a.worktree,a.original_api,a.patched_api,a.previous_zip),indent=2))
