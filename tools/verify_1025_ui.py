#!/usr/bin/env python3
"""Regression-check the 1.0.25 OBF map delta, API parity and composed CR messages.

No proprietary game JAR necessary; can run from GitHub CI.
"""
import argparse,csv,hashlib,json,zipfile
from pathlib import Path
from apply_1025 import OBF,STATUS,OLD_OBF_SHA,NEW_OBF_SHA
FIELDS=['source_class','english_literal','polish_ascii_draft','status']

def rows(p):
 with p.open(encoding='utf8',newline='') as f:
  r=csv.DictReader(f);assert r.fieldnames==FIELDS
  return list(r)

def main(root,previous):
 b=root/'buildtools';o=b/'NARZEDZIA_OBF';a=b/'NARZEDZIA_JAR/ZRODLA_EXE_GO'
 old=rows(o/'TLUMACZENIA_OBF_10124.csv');new=rows(o/'TLUMACZENIA_OBF_10125.csv')
 assert len(old)==3213 and len(new)==3294
 assert new[:len(old)]==old,'Historical OBF map changed unexpectedly'
 extra=[{'source_class':cl,'english_literal':en,'polish_ascii_draft':pl,'status':STATUS} for cl,items in OBF.items() for en,pl in items.items()]
 assert len(extra)==81 and new[len(old):]==extra
 assert len({(r['source_class'],r['english_literal']) for r in new})==3294
 assert (a/'translations/TLUMACZENIA_JAR_1024.csv').read_bytes()==(a/'translations/TLUMACZENIA_JAR_1025.csv').read_bytes(), 'API map must be byte-identical'
 src=(o/'main.go').read_text('utf8');api=(a/'main.go').read_text('utf8')
 assert 'const currentPatchState = "patched 10125"' in src
 assert f'"{OLD_OBF_SHA}": "10124"' in src
 assert 'loadTranslations("TLUMACZENIA_OBF_10125.csv")' in src
 assert 'const version = "1025"' in api
 assert f'const expectedOBFPatched10125 = "{NEW_OBF_SHA}"' in api
 assert '"1024", version}' in api
 assert 'const edition = "1.0.25"' in (b/'NARZEDZIA_INSTALATOR/main.go').read_text('utf8')
 ship=OBF['com.fs.starfarer.campaign.accidents.ShipLoss']
 for ref,txt in {
   'short':(ship['lost ']+'17%'+ship[' CR']),
   'wing':(ship['a ']+'Osa'+ship[' losing ']+'17%'+ship[' CR']),
   'ship':(ship['the ']+'Jastrzab'+ship[' losing ']+'17%'+ship[' CR']),
 }.items():
  expected={'short':'utrata 17% GB','wing':'skrzydlo Osa - utrata 17% GB','ship':'okret Jastrzab - utrata 17% GB'}[ref]
  assert txt==expected,(ref,txt)
  assert '  ' not in txt and 'CR' not in txt
 assert 'HOLD' not in OBF['com.fs.starfarer.campaign.command.J'], 'Never translate technical enum IDs'
 assert OBF['com.fs.starfarer.campaign.command.ShipBlueprintBrowser']['Frigates']=='Fregaty'
 assert OBF['com.fs.starfarer.campaign.command.OutpostListPanel']['Admin']=='Admin.'
 assert OBF['com.fs.starfarer.campaign.command.CustomProductionPanel']['Qty']=='Ilosc'
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 assert meta['gameVersion']=='0.98a-RC8' and meta['version']=='1.0.25'
 assert len(meta['replace'])==len(set(meta['replace']))==41
 data=root/'mod/data';files={p.relative_to(root/'mod').as_posix():p.read_bytes() for p in data.rglob('*') if p.is_file()}
 assert len(files)==870 and all(blob.isascii() for blob in files.values())
 if previous:
  with zipfile.ZipFile(previous) as z:
   original={n.removeprefix('Starsector_PL_ASCII/'):z.read(n) for n in z.namelist() if n.startswith('Starsector_PL_ASCII/data/')}
  assert original==files,'Data file changed in OBF-only 1.0.25 release'
 print('1.0.25 UI MAP PASS: 81 new OBF labels, no API text changes, 3 correctly composed CR->GB messages, 870 data intact')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--previous-zip',type=Path);a=p.parse_args();main(a.worktree,a.previous_zip)