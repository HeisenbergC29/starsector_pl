#!/usr/bin/env python3
"""Apply one verified Starsector 1.0.19 API UI-text correction over v1.0.18.

The English words were split in original bytecode as C + onsumes / R + educes,
including singular/plural light-year suffixes. The old mapping generated
'Czuzywa'/'Rzmniejsza'. All edits are localized text fields, not Java code.
The OBF patch state remains 10118, because OBF text is not changed in 1019.
"""
import argparse,csv,json,shutil
from pathlib import Path

CLASS='com.fs.starfarer.api.impl.campaign.abilities.ToggleAbilityWithCost'
OLD={
    'onsumes %s light ':'Zuzywa %s lat swietlnych ',
    ' worth of fuel and reduces the combat readiness ':' paliwa i zmniejsza gotowosc bojowa ',
    ' worth of fuel.':' paliwa.',
    'onsumes %s fuel and reduces the combat readiness':'zuzywa %s paliwa i zmniejsza gotowosc bojowa',
    'onsumes %s fuel.':'zuzywa %s paliwa.',
    'educes the combat readiness':'zmniejsza gotowosc bojowa',
    'of all ships by %s of a combat deployment.':'dla wszystkich okretow o %s kosztu wystawienia do walki.',
    ' of all ships, costing up to %s supplies to recover.':' wszystkich okretow, co moze wymagac do %s jednostek zaopatrzenia na przywrocenie stanu.',
}
NEW_TEXT={
    'onsumes %s light ':'uzywa paliwa odpowiadajacego przelotowi na dystansie %s ',
    ' worth of fuel and reduces the combat readiness ':' i zmniejsza gotowosc bojowa',
    ' worth of fuel.':'.',
    'onsumes %s fuel and reduces the combat readiness':'uzywa %s paliwa i zmniejsza gotowosc bojowa',
    'onsumes %s fuel.':'uzywa %s paliwa.',
    'educes the combat readiness':'mniejsza gotowosc bojowa',
    'of all ships by %s of a combat deployment.':' wszystkich okretow o %s kosztu wystawienia do walki.',
    ' of all ships, costing up to %s supplies to recover.':' wszystkich okretow, a przywrocenie ich gotowosci moze kosztowac do %s jednostek zaopatrzenia.',
}
APPEND={'C':'Z',' c':' z','R':'Z',' r':' z',"year's":'roku swietlnego',"years'":'lat swietlnych'}

def exact(s,old,new):
    assert s.count(old)==1,(old,s.count(old))
    return s.replace(old,new)

def update_map(root):
    dr=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
    src=dr/'TLUMACZENIA_JAR_1018.csv'; dst=dr/'TLUMACZENIA_JAR_1019.csv'
    with src.open(newline='',encoding='utf8') as f:
        r=csv.DictReader(f);head=r.fieldnames;rows=list(r)
    assert head==['source_class','english_literal','polish_ascii_draft','status'],head
    assert len(rows)==5100,len(rows)
    fixed=set()
    for row in rows:
        k=row['english_literal']
        if row['source_class']==CLASS and k in OLD:
            assert row['polish_ascii_draft']==OLD[k],(k,row['polish_ascii_draft'])
            row['polish_ascii_draft']=NEW_TEXT[k]
            row['status']='VERIFIED_COMPOSED_TOOLTIP_1019'
            fixed.add(k)
    assert fixed==set(OLD),fixed
    keys={(r['source_class'],r['english_literal']) for r in rows}
    for src_text,pl in APPEND.items():
        assert (CLASS,src_text) not in keys
        rows.append({'source_class':CLASS,'english_literal':src_text,'polish_ascii_draft':pl,'status':'VERIFIED_COMPOSED_TOOLTIP_1019'})
    assert all(x['polish_ascii_draft'].isascii() for x in rows)
    with dst.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=head,lineterminator='\r\n');w.writeheader();w.writerows(rows)
    assert len(rows)==5106
    return len(fixed),len(APPEND)

def main(root):
    assert (root/'mod/mod_info.json').is_file()
    edited,added=update_map(root)
    path=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go';s=path.read_text('utf8')
    s=exact(s,'const version = "1018"','const version = "1019"')
    s=exact(s,'const exeVersion = "1.0.18"','const exeVersion = "1.0.19"')
    s=exact(s,'"1013", "1014", "1015", "1016", "1017", version}', '"1013", "1014", "1015", "1016", "1017", "1018", version}')
    s=exact(s,'PL ASCII patch up to 1.0.18','PL ASCII patch up to 1.0.19')
    path.write_text(s,'utf8')
    source_test=Path(__file__).with_name('tooltip_1019_test.go')
    assert source_test.is_file(),source_test
    shutil.copyfile(source_test,root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/tooltip_1019_test.go')
    path=root/'buildtools/NARZEDZIA_INSTALATOR/main.go';s=path.read_text('utf8')
    s=exact(s,'const edition = "1.0.18"','const edition = "1.0.19"');path.write_text(s,'utf8')
    path=root/'mod/mod_info.json';j=json.loads(path.read_text('utf8'))
    assert j['version']=='1.0.18';j['version']='1.0.19';j['description']=j['description'].replace('1.0.18','1.0.19')
    path.write_text(json.dumps(j,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
    path=root/'mod/CZYTAJ.txt';s=path.read_text('utf8')
    s=exact(s,'STARSECTOR PL ASCII 1.0.18','STARSECTOR PL ASCII 1.0.19')
    s+='\nPoprawiono skladane komunikaty kosztow zdolnosci (paliwo i gotowosc bojowa).\n'
    path.write_text(s,'utf8')
    print(f'1.0.19 API tooltip: {edited} corrected map rows, {added} newly mapped literals; OBF unchanged')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
    main(p.parse_args().worktree)