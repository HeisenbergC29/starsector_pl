#!/usr/bin/env python3
"""Regression test for 1.0.24: exact 44 UI values, no mutated earlier rows or data.

CI without commercial originals runs this on restored worktree.
"""
import argparse,csv,hashlib,json,zipfile
from pathlib import Path
from apply_1024 import OBF,API,STATUS,NEW_OBF,OLD_OBF

FIELDS=['source_class','english_literal','polish_ascii_draft','status']

def rows(path):
    with path.open(encoding='utf8',newline='') as f:
        r=csv.DictReader(f);assert r.fieldnames==FIELDS,path
        return list(r)

def check(older,newer,new,old_count):
    a,b=rows(older),rows(newer)
    assert len(a)==old_count,(older,len(a),old_count)
    newrows=[{'source_class':cl,'english_literal':source,'polish_ascii_draft':target,'status':STATUS}
             for cl,items in new.items() for source,target in items.items()]
    assert b[:len(a)]==a,('prior translation map altered',newer)
    assert b[len(a):]==newrows,('unapproved UI entry',newer)
    assert len({(r['source_class'],r['english_literal']) for r in b})==len(b)
    for r in newrows:
        s,t=r['english_literal'],r['polish_ascii_draft']
        assert t and t.isascii() and t!=s and len(t)<100 and s.startswith(' ')==t.startswith(' ') and s.endswith(' ')==t.endswith(' '),(s,t)
    return len(b)

def main(root,previous):
    b=root/'buildtools';obf=b/'NARZEDZIA_OBF';api=b/'NARZEDZIA_JAR/ZRODLA_EXE_GO'
    assert check(obf/'TLUMACZENIA_OBF_10123.csv',obf/'TLUMACZENIA_OBF_10124.csv',OBF,3185)==3213
    assert check(api/'translations/TLUMACZENIA_JAR_1023.csv',api/'translations/TLUMACZENIA_JAR_1024.csv',API,5134)==5150
    assert sum(map(len,OBF.values()))==28 and sum(map(len,API.values()))==16
    # These enum names are program identifiers. Their human-facing labels are distinct.
    enum_map=API['com.fs.starfarer.api.campaign.FleetAssignment']
    assert all(name not in enum_map for name in ['FOLLOW','HOLD','INTERCEPT','RAID_SYSTEM','ATTACK_LOCATION','GO_TO_LOCATION'])
    assert 'Off' not in OBF['com.fs.starfarer.launcher.opengl.ooOO'], 'do not alter settings selector without inspecting comparisons'
    assert len(OBF['com.fs.starfarer.title.C'])==8
    assert OBF['com.fs.starfarer.title.C']['Quit']=='Wyjdz'
    assert API['com.fs.starfarer.api.impl.PlanetSearchData$2']['Claimed']=='Objete roszczeniami'
    assert API['com.fs.starfarer.api.campaign.impl.items.BaseSpecialItemPlugin']['Price: ']=='Cena: '
    obfsrc=(obf/'main.go').read_text('utf8');apisrc=(api/'main.go').read_text('utf8')
    assert 'const currentPatchState = "patched 10124"' in obfsrc
    assert f'"{OLD_OBF}": "10123"' in obfsrc
    assert 'loadTranslations("TLUMACZENIA_OBF_10124.csv")' in obfsrc
    assert 'const version = "1024"' in apisrc
    assert 'const expectedOBFPatched10124 = "'+NEW_OBF+'"' in apisrc
    assert 'const edition = "1.0.24"' in (b/'NARZEDZIA_INSTALATOR/main.go').read_text('utf8')
    meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
    assert meta['version']=='1.0.24' and meta['gameVersion']=='0.98a-RC8'
    assert len(meta['replace'])==len(set(meta['replace']))==41
    data=root/'mod/data'; files={p.relative_to(root/'mod').as_posix():p.read_bytes() for p in data.rglob('*') if p.is_file()}
    assert len(files)==870 and all(v.isascii() for v in files.values())
    if previous:
        with zipfile.ZipFile(previous) as z:
            older={n.removeprefix('Starsector_PL_ASCII/'):z.read(n) for n in z.namelist() if n.startswith('Starsector_PL_ASCII/data/')}
        assert files==older, 'unapproved data edit in 1.0.24'
    print('1.0.24 REGRESSION PASS: 28 OBF +16 API; 44 approved UI labels, all previous mappings preserved; 870 data files checked')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--previous-zip',type=Path)
    x=p.parse_args();main(x.worktree,x.previous_zip)