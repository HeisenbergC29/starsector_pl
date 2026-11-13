#!/usr/bin/env python3
"""Byte-exact 1.0.52 translation-map delta and immutable game-data verifier."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
from apply_1052 import OLD,NEW,OLD_SHA,BASE,LUDDIC,SHIELD,ADDITIONS,CORRECTIONS,readmap,serialize,make,sha
OBF_GO_SHA='f53023d97c88615b353d4fbe78f7e7a41cd085c3e082fc2a00586592be8da9bc'
RULES_SHA='e9a6ad60da0caca6fa89af21370eddfa461de39324486368458aca2575e3b64a'
DATA_TREE_SHA='5bfda6c69b2f83e3913fa4e1475c6288e1f3a0d82914fd007abba381e8da0fc1'
def tree_digest(root):
 folder=Path(root)/'mod/data';h=hashlib.sha256();n=0
 for path in sorted(folder.rglob('*')):
  if not path.is_file() or path.relative_to(folder).as_posix()=='campaign/rules.csv':continue
  h.update(path.relative_to(folder).as_posix().encode()+b'\0'+hashlib.sha256(path.read_bytes()).digest());n+=1
 return h.hexdigest(),n

NEW_SHA='ddcec94935d80bcee715514352f79ffbea113ec299953c422746a94241ee179c'
PRIOR_GO_SHA='ea93eb50525724c253a6febde96ee9b07fb16ebfad9175c769088d4a287f25fc'
GO_REVERSE=[('const version = "1052"','const version = "1051"'),
('const exeVersion = "1.0.52"','const exeVersion = "1.0.51"'),
('"1048", "1049", "1050", "1051", version}','"1048", "1049", "1050", version}'),
('PL ASCII patch up to 1.0.52','PL ASCII patch up to 1.0.51')]

def check(root,previous_zip=None):
 root=Path(root);t=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations';old=t/OLD;new=t/NEW
 if sha(old.read_bytes())!=OLD_SHA or sha(new.read_bytes())!=NEW_SHA:raise ValueError('Baseline/target API map hash mismatch')
 a=readmap(old);b=readmap(new);expected=make(a)
 if len(a)!=5269 or len(b)!=5283 or serialize(expected)!=new.read_bytes():raise ValueError('API map differs from the exact reviewed inventory')
 delta=[(x['source_class'],x['english_literal']) for x,y in zip(a,b[:len(a)]) if x!=y]
 if set(delta)!=set(CORRECTIONS):raise ValueError(('Unexpected previous row modified',delta))
 add={(x['source_class'],x['english_literal']) for x in b[len(a):]}
 if add!=set(ADDITIONS) or len(delta)!=10 or len(add)!=14:raise ValueError('Wrong new/changed mapping inventory')
 gop=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go';go=gop.read_text('utf8')
 for newtag,oldtag in GO_REVERSE:
  if go.count(newtag)!=1:raise ValueError(('Missing/duplicated exact Go version change',newtag))
  go=go.replace(newtag,oldtag)
 if sha(go.encode())!=PRIOR_GO_SHA:raise ValueError('Go patcher changed beyond version constants')
 obf=root/'buildtools/NARZEDZIA_OBF/main.go'
 if obf.exists() and sha(obf.read_bytes())!=OBF_GO_SHA:raise ValueError('OBF Go patcher changed')
 info=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 if info['version']!='1.0.52' or info['gameVersion']!='0.98a-RC8' or len(info['replace'])!=41:raise ValueError('Bad mod version or replacement list')
 if 'const edition = "1.0.52"' not in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8'):
  raise ValueError('Old installer edition')
 if not (root/'mod/CZYTAJ.txt').read_text('utf8').startswith('STARSECTOR PL ASCII 1.0.52'):
  raise ValueError('Old instructions version')
 dat=root/'mod/data';files=[x for x in dat.rglob('*') if x.is_file()]
 if len(files)!=870 or sha((dat/'campaign/rules.csv').read_bytes())!=RULES_SHA:raise ValueError('Rules/data files unexpectedly modified')
 tree,n=tree_digest(root)
 if n!=869 or tree!=DATA_TREE_SHA:raise ValueError('Non-rules data modified')
 if previous_zip:
  with zipfile.ZipFile(previous_zip) as z:
   previous={n.removeprefix('Starsector_PL_ASCII/'):z.read(n) for n in z.namelist() if n.startswith('Starsector_PL_ASCII/data/')}
  if len(previous)!=870:raise ValueError('Wrong prior distribution')
  for p in files:
   rel=p.relative_to(root/'mod').as_posix()
   if p.read_bytes()!=previous.get(rel):raise ValueError(('Data differs from 1.0.51',rel))
 return {'version':'1.0.52','map_rows':5283,'new_context_literals':14,'corrected_dialogue_fragments':10,
  'changed_java_classes':3,'new_java_bytecode_edits':0,'prior_personality_jvm_exception_unchanged':True,
  'current_api_map_sha256':NEW_SHA,'original_1051_map_sha256':OLD_SHA,
  'game_data_files_unchanged':870,'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--previous-zip',type=Path)
 a=p.parse_args();print(json.dumps(check(a.worktree,a.previous_zip),indent=2))
