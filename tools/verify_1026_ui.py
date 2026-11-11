#!/usr/bin/env python3
"""Fail-closed 1.0.26 map delta and UI labels regression check.

Validates public overlay and local source state; no commercial JAR required.
"""
import argparse,csv,hashlib,json,zipfile
from pathlib import Path
from apply_1026 import OBF, STATUS, OLD_OBF_SHA, NEW_OBF_SHA
FIELDS=['source_class','english_literal','polish_ascii_draft','status']

def rows(p):
 with p.open('r',encoding='utf8',newline='') as f:
  r=csv.DictReader(f);assert r.fieldnames==FIELDS
  return list(r)

def validate(root,previous_zip=None):
 b=root/'buildtools';o=b/'NARZEDZIA_OBF';a=b/'NARZEDZIA_JAR/ZRODLA_EXE_GO'
 old=rows(o/'TLUMACZENIA_OBF_10125.csv');new=rows(o/'TLUMACZENIA_OBF_10126.csv')
 assert len(old)==3294 and len(new)==3380
 assert new[:len(old)]==old, 'A historical 1.0.25 translation was changed'
 extra=[dict(source_class=cl,english_literal=en,polish_ascii_draft=pl,status=STATUS) for cl,m in OBF.items() for en,pl in m.items()]
 assert len(extra)==86 and len(OBF)==20 and new[len(old):]==extra,'Missing, reordered or unapproved UI translation'
 assert len({(x['source_class'],x['english_literal']) for x in new})==3380,'Duplicate mapping key'
 assert all(x['polish_ascii_draft'].isascii() and x['polish_ascii_draft']!=x['english_literal'] for x in extra)
 assert all(x['english_literal'].startswith(' ')==x['polish_ascii_draft'].startswith(' ') and x['english_literal'].endswith(' ')==x['polish_ascii_draft'].endswith(' ') for x in extra)
 assert (a/'translations/TLUMACZENIA_JAR_1025.csv').read_bytes()==(a/'translations/TLUMACZENIA_JAR_1026.csv').read_bytes(), 'API map modified unexpectedly'
 go=(o/'main.go').read_text('utf8');api=(a/'main.go').read_text('utf8')
 assert 'const currentPatchState = "patched 10126"' in go
 assert 'loadTranslations("TLUMACZENIA_OBF_10126.csv")' in go
 assert f'"{OLD_OBF_SHA}": "10125"' in go
 assert 'const version = "1026"' in api
 assert f'const expectedOBFPatched10126 = "{NEW_OBF_SHA}"' in api
 assert 'hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10126' in api
 assert 'const edition = "1.0.26"' in (b/'NARZEDZIA_INSTALATOR/main.go').read_text('utf8')
 assert OBF['com.fs.starfarer.coreui.refit.Q']['Autofit...']=='Autodopasuj...'
 assert OBF['com.fs.starfarer.campaign.ui.intel.PlanetListV2']['Hazard']=='Zagrozenie'
 assert OBF['com.fs.starfarer.ui.newui.L']['Fleet']=='Flota'
 assert OBF['com.fs.starfarer.campaign.ui.marketinfo.IndustryPickerDialog']['Build']=='Buduj'
 assert OBF['com.fs.starfarer.ui.newui.FleetMemberRecoveryDialog']['Recover']=='Odzyskaj'
 assert OBF['com.fs.starfarer.campaign.ui.marketinfo.GroundRaidTargetPickerDialog']['Objective']=='Cel'
 for protected in ('FOLLOW','HOLD','INTERCEPT','RAID_SYSTEM','Off'):
  assert not any(protected in m for m in OBF.values()),('protected technical enum/key translated',protected)
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 assert meta['version']=='1.0.26' and meta['gameVersion']=='0.98a-RC8' and len(meta['replace'])==41
 data=root/'mod/data';files={p.relative_to(root/'mod').as_posix():p.read_bytes() for p in data.rglob('*') if p.is_file()}
 assert len(files)==870 and all(v.isascii() for v in files.values())
 if previous_zip:
  with zipfile.ZipFile(previous_zip) as z:
   original={n.removeprefix('Starsector_PL_ASCII/'):z.read(n) for n in z.namelist() if n.startswith('Starsector_PL_ASCII/data/')}
  assert files==original, 'Data changed between OBF-only releases'
 return {'new_obf_literals':86,'classes_reviewed':20,'obf_patched_literals':3380,'api_patched_literals':5148,'api_map_identical':True,'unchanged_data_files':870}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--previous-zip',type=Path)
 q=p.parse_args();print(json.dumps(validate(q.worktree,q.previous_zip),indent=2))