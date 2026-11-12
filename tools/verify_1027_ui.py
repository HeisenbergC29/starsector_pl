#!/usr/bin/env python3
"""Strict source-level regression for the 1.0.27 71-string translation delta."""
import argparse,csv,json,zipfile
from pathlib import Path
from apply_1027 import OBF,API,STATUS,OLD_OBF_SHA,NEW_OBF_SHA
FIELDS=['source_class','english_literal','polish_ascii_draft','status']

def rows(path):
 with path.open('r',newline='',encoding='utf8') as f:
  obj=csv.DictReader(f);assert obj.fieldnames==FIELDS
  return list(obj)

def verify_delta(old,new,mapping,expected_count):
 expected=[dict(source_class=cl,english_literal=en,polish_ascii_draft=pl,status=STATUS)
           for cl,items in mapping.items() for en,pl in items.items()]
 assert len(expected)==expected_count,(len(expected),expected_count)
 assert len(new)==len(old)+expected_count
 assert new[:len(old)]==old,'Existing historical translation changed'
 assert new[len(old):]==expected,'Unexpected added translation or ordering'
 assert len({(r['source_class'],r['english_literal']) for r in new})==len(new),'Duplicate map key'
 assert all(r['polish_ascii_draft'].isascii() and r['polish_ascii_draft']!=r['english_literal'] for r in expected)
 assert all(r['english_literal'].startswith(' ')==r['polish_ascii_draft'].startswith(' ') and
            r['english_literal'].endswith(' ')==r['polish_ascii_draft'].endswith(' ') and
            r['english_literal'].count('\n')==r['polish_ascii_draft'].count('\n') for r in expected)
 return True

def check(worktree,previous_zip=None):
 b=worktree/'buildtools';o=b/'NARZEDZIA_OBF';a=b/'NARZEDZIA_JAR/ZRODLA_EXE_GO'
 oldo=rows(o/'TLUMACZENIA_OBF_10126.csv');newo=rows(o/'TLUMACZENIA_OBF_10127.csv')
 olda=rows(a/'translations/TLUMACZENIA_JAR_1026.csv');newa=rows(a/'translations/TLUMACZENIA_JAR_1027.csv')
 assert len(oldo)==3380 and len(olda)==5150
 verify_delta(oldo,newo,OBF,41);verify_delta(olda,newa,API,30)
 go=(o/'main.go').read_text('utf8'); apisrc=(a/'main.go').read_text('utf8')
 assert 'const currentPatchState = "patched 10127"' in go
 assert 'loadTranslations("TLUMACZENIA_OBF_10127.csv")' in go
 assert f'"{OLD_OBF_SHA}": "10126"' in go
 assert 'const version = "1027"' in apisrc
 assert f'const expectedOBFPatched10127 = "{NEW_OBF_SHA}"' in apisrc
 assert 'hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10127' in apisrc
 assert 'const edition = "1.0.27"' in (b/'NARZEDZIA_INSTALATOR/main.go').read_text('utf8')
 for protection in ('CMENU_ASSAULT','SHIP_ACCELERATE','FOLLOW','HOLD','INTERCEPT','RAID_SYSTEM','fake_market','BUTTON_END','Military','Exploration','Missions'):
  assert not any(protection in m for m in OBF.values())
  assert not any(protection in m for m in API.values())
 assert OBF['com.fs.starfarer.campaign.ui.trade.new']['Cruiser']=='Krazownik'
 assert OBF['com.fs.starfarer.ui.impl.oO0O']['Allies']=='Sojusznicy'
 assert API['com.fs.starfarer.api.impl.campaign.FleetInteractionDialogPluginImpl']['Disengage']=='Zerwij kontakt'
 assert API['com.fs.starfarer.api.impl.campaign.rulecmd.salvage.MarketCMD']['Spoils']=='Zdobycz'
 assert API['com.fs.starfarer.api.impl.campaign.intel.PerseanLeagueMembership']['Colonies']=='Kolonie'
 meta=json.loads((worktree/'mod/mod_info.json').read_text('utf8'))
 assert meta['version']=='1.0.27' and meta['gameVersion']=='0.98a-RC8' and len(meta['replace'])==41
 files={p.relative_to(worktree/'mod').as_posix():p.read_bytes() for p in (worktree/'mod/data').rglob('*') if p.is_file()}
 assert len(files)==870 and all(c.isascii() for c in files.values())
 if previous_zip:
  with zipfile.ZipFile(previous_zip) as z:
   prior={n.removeprefix('Starsector_PL_ASCII/'):z.read(n) for n in z.namelist() if n.startswith('Starsector_PL_ASCII/data/')}
  assert files==prior,'Modified data files unexpectedly'
 return {'added_obf':41,'added_api':30,'total_obf_rows':len(newo),'total_api_rows':len(newa),'unchanged_data_files':870,'protected_ids_unchanged':True}
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('worktree',type=Path)
 parser.add_argument('--previous-zip',type=Path)
 x=parser.parse_args();print(json.dumps(check(x.worktree,x.previous_zip),indent=2))