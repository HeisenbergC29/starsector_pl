#!/usr/bin/env python3
"""Independent byte-exact API-map validation of 1.0.49 including empty plural-suffix mapping."""
from __future__ import annotations
import csv,hashlib,json,zipfile
from pathlib import Path
from apply_1049 import OLD,NEW,OLD_SHA,PLAN_PATH,SALVOR,plan,readmap,serialize,sha

NEW_SHA='3ae9e6c3e8675139a9aa3bc91ca88f32fc2b65301f5b7657e8936c85d81c5420'
PREV_GO_SHA='f4f9474b9ae73395958e74ba91e0454896bb912761ccba0589c635692cb5ddf9'
OBF_GO_SHA='f53023d97c88615b353d4fbe78f7e7a41cd085c3e082fc2a00586592be8da9bc'
RULES_SHA='e9a6ad60da0caca6fa89af21370eddfa461de39324486368458aca2575e3b64a'
DATA_TREE_SHA='5bfda6c69b2f83e3913fa4e1475c6288e1f3a0d82914fd007abba381e8da0fc1'
PLAN_SHA='09225228b79482db4d868ff14a8f9c9d850afd5e70be2f42c75ff215313e8aae'
GO_REVERSE=(('const version = "1049"','const version = "1048"'),
            ('const exeVersion = "1.0.49"','const exeVersion = "1.0.48"'),
            ('"1046", "1047", "1048", version}', '"1046", "1047", version}'),
            ('PL ASCII patch up to 1.0.49','PL ASCII patch up to 1.0.48'))
def tree_digest(root):
 folder=Path(root)/'mod/data';h=hashlib.sha256();n=0
 for f in sorted(folder.rglob('*')):
  if not f.is_file() or f.relative_to(folder).as_posix()=='campaign/rules.csv':continue
  h.update(f.relative_to(folder).as_posix().encode('utf8')+b'\0'+hashlib.sha256(f.read_bytes()).digest());n+=1
 return h.hexdigest(),n

def check(root,prior_zip=None):
 root=Path(root)
 trans=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 old=trans/OLD;new=trans/NEW
 if sha(PLAN_PATH.read_bytes())!=PLAN_SHA or sha(old.read_bytes())!=OLD_SHA or sha(new.read_bytes())!=NEW_SHA:raise ValueError('Source/plan/map SHA mismatch')
 previous=readmap(old);newer=readmap(new);edits,extra,items=plan(previous)
 if len(previous)!=5260 or len(newer)!=5261 or serialize(newer)!=new.read_bytes():raise ValueError('Unexpected API map format')
 if newer[-1]!={'source_class':SALVOR,'english_literal':'s','polish_ascii_draft':'','status':'REVIEWED_PLURAL_SUFFIX_1049'}:
  raise ValueError('Missing or tampered class-specific English plural removal')
 for pre,post in zip(previous,newer[:-1]):
  if any(pre[f]!=post[f] for f in ('source_class','english_literal','status')):
   raise ValueError(('Unauthorized technical field change',pre['source_class']))
  key=pre['source_class'],pre['english_literal'];want=edits[key]['new_polish'] if key in edits else pre['polish_ascii_draft']
  if post['polish_ascii_draft']!=want:raise ValueError(('Unreviewed translation changed',key))
 if len({x['source_class'] for x in items})!=7:raise ValueError('Unexpected changed class inventory')
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 if meta.get('version')!='1.0.49' or meta.get('gameVersion')!='0.98a-RC8' or len(meta.get('replace',[]))!=41:
  raise ValueError('Unexpected game or release metadata')
 readme=(root/'mod/CZYTAJ.txt').read_text('utf8')
 if not readme.startswith('STARSECTOR PL ASCII 1.0.49'):raise ValueError('Installer instructions not updated')
 installer_main=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
 if 'const edition = "1.0.49"' not in installer_main.read_text('utf8'):raise ValueError('Installer version not updated')
 go=(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go').read_text('utf8')
 for a,b in GO_REVERSE:
  if go.count(a)!=1:raise ValueError(('Unexpected Go version change',a))
  go=go.replace(a,b)
 if sha(go.encode())!=PREV_GO_SHA:raise ValueError('Unauthorized Go patcher code modification')
 obf=root/'buildtools/NARZEDZIA_OBF/main.go'
 if obf.exists() and sha(obf.read_bytes())!=OBF_GO_SHA:raise ValueError('OBF patcher modified')
 folder=root/'mod/data';files=[f for f in folder.rglob('*') if f.is_file()]
 if len(files)!=870 or sha((folder/'campaign/rules.csv').read_bytes())!=RULES_SHA:raise ValueError('Data/rules changed')
 data_tree,n=tree_digest(root)
 if n!=869 or data_tree!=DATA_TREE_SHA:raise ValueError('Non-rules data files changed')
 if prior_zip:
  with zipfile.ZipFile(prior_zip) as z:
   original={n.removeprefix('Starsector_PL_ASCII/'):z.read(n) for n in z.namelist() if n.startswith('Starsector_PL_ASCII/data/')}
  if len(original)!=870:raise ValueError('Incorrect baseline ZIP')
  for f in files:
   rel=f.relative_to(root/'mod').as_posix()
   if original.get(rel)!=f.read_bytes():raise ValueError(('Changed old game data',rel))
 return {'release':'1.0.49','base_map_rows':5260,'new_map_rows':5261,'existing_translations_fixed':13,
 'new_salvors_plural_suffix_mapping':1,'changed_classes':7,
 'previous_map_sha256':OLD_SHA,'new_map_sha256':NEW_SHA,'data_files_unchanged':870,
 'technical_identifiers_unchanged':True,'executable_java_bytecode_change_required':False,
 'native_windows_gameplay_tested':False}
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--prior-zip',type=Path)
 a=p.parse_args();print(json.dumps(check(a.worktree,a.prior_zip),indent=2))
