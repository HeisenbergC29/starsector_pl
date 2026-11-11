#!/usr/bin/env python3
"""Fail-closed, reproduction-friendly regression for 1.0.23 UI label translations."""
import argparse,csv,json,zipfile,collections
from pathlib import Path
from apply_1023 import OBF,API,STATUS

FIELDS=['source_class','english_literal','polish_ascii_draft','status']

def read_csv(p):
    with p.open(encoding='utf8',newline='') as f:
        r=csv.DictReader(f);assert r.fieldnames==FIELDS,p
        return list(r)

def check_map(older,newer,delta):
    old,cur=read_csv(older),read_csv(newer)
    assert cur[:len(old)]==old,('previous rows modified',newer)
    expected=[{'source_class':cl,'english_literal':en,'polish_ascii_draft':pl,'status':STATUS}
      for cl,pairs in delta.items() for en,pl in pairs.items()]
    assert cur[len(old):]==expected,(newer,'missing/unapproved translation delta')
    assert len({(r['source_class'],r['english_literal']) for r in cur})==len(cur)
    assert all(r['english_literal']!=r['polish_ascii_draft'] and r['polish_ascii_draft'].isascii() for r in expected)
    for r in expected:
        a,b=r['english_literal'],r['polish_ascii_draft']
        assert (' '==a[:1])==(' '==b[:1]),('leading whitespace',a,b)
        if a.endswith(' '):
            # One intentional dynamic composition: English has excess space,
            # next fragment already starts with one. Polish must not double it.
            assert r['source_class'].endswith('ToggleAbilityWithCost') and a=='educes the combat readiness '
        else:assert not b.endswith(' '),('trailing whitespace',a,b)
    return len(old),len(cur)

def main(root,previous):
    a=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
    o=root/'buildtools/NARZEDZIA_OBF'
    before,after=check_map(a/'TLUMACZENIA_JAR_1021.csv',a/'TLUMACZENIA_JAR_1023.csv',API)
    assert (before,after)==(5108,5134)
    before,after=check_map(o/'TLUMACZENIA_OBF_10121.csv',o/'TLUMACZENIA_OBF_10123.csv',OBF)
    assert (before,after)==(3144,3185)
    assert sum(map(len,API.values()))==26 and sum(map(len,OBF.values()))==41
    assert 'Administrator' not in API['com.fs.starfarer.api.impl.campaign.econ.impl.BaseIndustry']
    obfmap=read_csv(o/'TLUMACZENIA_OBF_10123.csv')
    apimap=read_csv(a/'TLUMACZENIA_JAR_1023.csv')
    assert not any(r['source_class'].endswith('MarketCMD$RaidDangerLevel') and r['english_literal'] in ('HIGH','LOW','NONE','MINIMAL','EXTREME','MEDIUM') for r in apimap), 'Enum identifiers inadvertently translated'
    marker={(r['source_class'],r['english_literal']):r['polish_ascii_draft'] for r in apimap}
    cl='com.fs.starfarer.api.impl.campaign.abilities.ToggleAbilityWithCost'
    assert 'Z'+marker[(cl,'educes the combat readiness ')]+marker[(cl,' of all ships, costing up to %s supplies to recover.')]=='Zmniejsza gotowosc bojowa wszystkich okretow, a przywrocenie ich gotowosci moze kosztowac do %s jednostek zaopatrzenia.'
    assert OBF['com.fs.starfarer.ui.impl.CargoTooltipFactory']['Perfect']=='Idealna', 'weapon accuracy adjective must agree with feminine celnosc'
    meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
    assert meta['version']=='1.0.23' and meta['gameVersion']=='0.98a-RC8'
    assert '10123' in (o/'main.go').read_text('utf8')
    assert 'const version = "1023"' in (root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go').read_text('utf8')
    files={p.relative_to(root/'mod').as_posix():p.read_bytes() for p in (root/'mod/data').rglob('*') if p.is_file()}
    assert len(files)==870 and all(v.isascii() for v in files.values())
    if previous:
        with zipfile.ZipFile(previous) as z:
            prefix='Starsector_PL_ASCII/'
            old={n.removeprefix(prefix):z.read(n) for n in z.namelist() if n.startswith(prefix+'data/')}
            assert old==files,('data files modified between 1.0.22 and 1.0.23')
    print('1.0.23 UI REGRESSION PASS: OBF +41/API +26; no old rows modified, 870 data unchanged; dynamic sentence correct')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--previous-zip',type=Path)
    ar=p.parse_args();main(ar.worktree,ar.previous_zip)