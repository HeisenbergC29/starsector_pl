#!/usr/bin/env python3
"""Fail-closed 1.0.50 API delta, metadata, Go and immutable game-data verifier."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
from apply_1050 import OLD,NEW,OLD_SHA,CLASS,CHANGES,STATUS,plan,readmap,serialize,sha
from verify_1049 import tree_digest,OBF_GO_SHA,RULES_SHA,DATA_TREE_SHA
NEW_SHA='d2f6b355c58a8d2f0c9a5674e19bcaf7e24862ac4a3c28ad6ace97ce0024b41e'
PREVIOUS_GO_SHA='a232cb157e9ab9118dc9515e31c0e5868d4344e50b139360fbb49957c2c3b50b'
GO_REVERSE=[('const version = "1050"','const version = "1049"'),('const exeVersion = "1.0.50"','const exeVersion = "1.0.49"'),
 ('"1047", "1048", "1049", version}','"1047", "1048", version}'),
 ('PL ASCII patch up to 1.0.50','PL ASCII patch up to 1.0.49')]
def check(root,prior_zip=None):
 root=Path(root);folder=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations';old=folder/OLD;new=folder/NEW
 if sha(old.read_bytes())!=OLD_SHA or sha(new.read_bytes())!=NEW_SHA:raise ValueError('Source/target API map SHA changed')
 original=readmap(old);latest=readmap(new);added=plan(original)
 if len(latest)!=5269 or len(original)!=5261 or serialize(latest)!=new.read_bytes():raise ValueError('Wrong map rows/format')
 if latest[:5261]!=original or latest[5261:]!=added:raise ValueError('Unreviewed mapping modified or duration fragments changed')
 if len({(v['source_class'],v['english_literal']) for v in latest})!=5269:raise ValueError('Duplicate mapping key')
 data=root/'mod/data';files=[p for p in data.rglob('*') if p.is_file()]
 if len(files)!=870 or sha((data/'campaign/rules.csv').read_bytes())!=RULES_SHA:raise ValueError('Unauthorized rules data change')
 digest,count=tree_digest(root)
 if count!=869 or digest!=DATA_TREE_SHA:raise ValueError('Unauthorized other game data changes')
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 if meta.get('version')!='1.0.50' or meta.get('gameVersion')!='0.98a-RC8' or len(meta['replace'])!=41:raise ValueError('Wrong metadata')
 if not (root/'mod/CZYTAJ.txt').read_text('utf8').startswith('STARSECTOR PL ASCII 1.0.50'):raise ValueError('Wrong installation instructions')
 if 'const edition = "1.0.50"' not in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8'):raise ValueError('Wrong installer edition')
 g=(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go').read_text('utf8')
 for a,b in GO_REVERSE:
  if g.count(a)!=1:raise ValueError(('Changed Go source beyond version constants',a))
  g=g.replace(a,b)
 if sha(g.encode('utf8'))!=PREVIOUS_GO_SHA:raise ValueError('Unauthorized executable Go code change')
 obf=root/'buildtools/NARZEDZIA_OBF/main.go'
 if obf.exists() and sha(obf.read_bytes())!=OBF_GO_SHA:raise ValueError('OBF patcher code changed')
 if prior_zip:
  with zipfile.ZipFile(prior_zip) as z:
   prior={n.removeprefix('Starsector_PL_ASCII/'):z.read(n) for n in z.namelist() if n.startswith('Starsector_PL_ASCII/data/')}
  if len(prior)!=870:raise ValueError('Wrong prior ZIP inventory')
  for p in files:
   rel=p.relative_to(root/'mod').as_posix()
   if prior.get(rel)!=p.read_bytes():raise ValueError(('Prior 1.0.49 data changed',rel))
 return {'release':'1.0.50','previous_map_rows':5261,'current_map_rows':5269,'new_class_scoped_fragments':8,
  'current_map_sha256':NEW_SHA,'unchanged_game_data_files':870,'jvm_methods_changed':False,
  'expected_original_jvm_ldc_users':17,'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--prior-zip',type=Path)
 a=p.parse_args();print(json.dumps(check(a.worktree,a.prior_zip),indent=2))
