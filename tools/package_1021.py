#!/usr/bin/env python3
"""Package current Starsector PL 1.0.21 worktree without proprietary JARs.

Optional --previous checks byte-identical mod/data against v1.0.20 distribution.
"""
import argparse,csv,hashlib,json,zipfile
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
  ap=argparse.ArgumentParser();ap.add_argument('--worktree',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--previous',type=Path);a=ap.parse_args()
  root=a.worktree;mod=root/'mod';data=mod/'data';files=sorted(p for p in data.rglob('*') if p.is_file())
  assert len(files)==870 and all(p.read_bytes().isascii() for p in files)
  if a.previous:
    with zipfile.ZipFile(a.previous) as z:
      before={n.removeprefix('Starsector_PL_ASCII/'):z.read(n) for n in z.namelist() if n.startswith('Starsector_PL_ASCII/data/')}
    assert len(before)==870
    allow={"data/missions/coralnebula/MissionDefinition.java", "data/missions/coralnebula/mission_text.txt", "data/characters/skills/skill_data.csv"}
    changed={p.relative_to(mod).as_posix() for p in files if before[p.relative_to(mod).as_posix()]!=p.read_bytes()}
    assert changed==allow, ("Unexpected data delta",changed^allow)
  meta=json.loads((mod/'mod_info.json').read_text('utf8'));assert meta['version']=='1.0.21' and meta['gameVersion']=='0.98a-RC8'
  assert len(meta['replace'])==len(set(meta['replace']))==41
  assert all((mod/s).is_file() for s in meta['replace'])
  with (data/'campaign/rules.csv').open(newline='',encoding='ascii') as f:assert len(list(csv.DictReader(f)))==11107
  for f in ('Starsector_PL_Instalator.exe','api_windows.exe','obf_windows.exe'):
    assert (root/f).read_bytes()[:2]==b'MZ'
  with zipfile.ZipFile(a.out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
    for p in sorted((x for x in mod.rglob('*') if x.is_file()),key=lambda x:x.as_posix()):
      z.write(p,'Starsector_PL_ASCII/'+p.relative_to(mod).as_posix())
    z.write(root/'Starsector_PL_Instalator.exe','Starsector_PL_ASCII/Starsector_PL_Instalator.exe')
  with zipfile.ZipFile(a.out) as z:
    assert z.testzip() is None and len(z.namelist())==873
    assert sum(x.startswith('Starsector_PL_ASCII/data/') for x in z.namelist())==870
    assert not any(n.endswith('.jar') or '/src/' in n for n in z.namelist())
  print(json.dumps({'name':a.out.name,'bytes':a.out.stat().st_size,'sha256':sha(a.out),'entries':873,'data':870},indent=2))
if __name__=='__main__':main()