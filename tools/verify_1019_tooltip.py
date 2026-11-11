#!/usr/bin/env python3
"""Fail-closed 1.0.19 correction audit of split-verb UI descriptions."""
from __future__ import annotations
import csv,json,sys
from pathlib import Path

TARGET='com.fs.starfarer.api.impl.campaign.abilities.ToggleAbilityWithCost'
CORRECTIONS={
    'onsumes %s light ':'uzywa paliwa odpowiadajacego przelotowi na dystansie %s ',
    ' worth of fuel and reduces the combat readiness ':' i zmniejsza gotowosc bojowa',
    ' worth of fuel.':'.',
    'onsumes %s fuel and reduces the combat readiness':'uzywa %s paliwa i zmniejsza gotowosc bojowa',
    'onsumes %s fuel.':'uzywa %s paliwa.',
    'educes the combat readiness':'mniejsza gotowosc bojowa',
    'of all ships by %s of a combat deployment.':' wszystkich okretow o %s kosztu wystawienia do walki.',
    ' of all ships, costing up to %s supplies to recover.':' wszystkich okretow, a przywrocenie ich gotowosci moze kosztowac do %s jednostek zaopatrzenia.',
}
NEW={'C':'Z',' c':' z','R':'Z',' r':' z',"year's":'roku swietlnego',"years'":'lat swietlnych'}

def load(p):
    with p.open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))

def main(root):
    d=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
    old=load(d/'TLUMACZENIA_JAR_1018.csv')
    new=load(d/'TLUMACZENIA_JAR_1019.csv')
    assert len(old)==5100 and len(new)==5106
    om={(r['source_class'],r['english_literal']):r for r in old}
    nm={(r['source_class'],r['english_literal']):r for r in new}
    assert len(om)==len(old) and len(nm)==len(new)
    assert set(nm)-set(om)=={(TARGET,k) for k in NEW}
    assert set(om)-set(nm)==set()
    corrections=[]
    for k,v in nm.items():
        if k in om and v!=om[k]:
            assert k==(TARGET,k[1]) and k[1] in CORRECTIONS
            assert v['polish_ascii_draft']==CORRECTIONS[k[1]]
            assert v['status']=='VERIFIED_COMPOSED_TOOLTIP_1019'
            corrections.append(k[1])
    assert set(corrections)==set(CORRECTIONS)
    for k,val in NEW.items():
        assert nm[(TARGET,k)]['polish_ascii_draft']==val
        assert nm[(TARGET,k)]['status']=='VERIFIED_COMPOSED_TOOLTIP_1019'
    assert all(row['polish_ascii_draft'].isascii() for row in new)
    assert json.loads((root/'mod/mod_info.json').read_text('utf8'))['version']=='1.0.19'
    assert 'const version = "1019"' in (root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go').read_text()
    assert 'const currentPatchState = "patched 10118"' in (root/'buildtools/NARZEDZIA_OBF/main.go').read_text()
    print(json.dumps({'release':'1.0.19','api_corrected':len(corrections),'api_new':len(NEW),
      'api_map_rows':len(new),'obf_component_release':'1.0.18','only_target_class':TARGET},indent=2))

if __name__=='__main__':
    assert len(sys.argv)==2
    main(Path(sys.argv[1]))