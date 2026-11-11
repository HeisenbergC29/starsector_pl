#!/usr/bin/env python3
"""Starsector PL 1.0.18: localize *subject* pronouns in three UI codepaths.

Intentional scope: 6 text literals in Java constant pools, preserving 1017
mapping and technical IDs. Do NOT touch 'her', 'him', 'his', or Misc.STORY;
those have genuinely distinct Polish inflections across callsites.
"""
import csv,json
from pathlib import Path

API_CLASSES = (
    'com.fs.starfarer.api.impl.campaign.intel.bar.events.BaseBarEventWithPerson',
    'com.fs.starfarer.api.impl.campaign.intel.bar.events.historian.HistorianData',
)
OBF_CLASSES = ('com.fs.starfarer.rpg.Person',)
PATTERNS = {'he':'on','she':'ona'}


def exact(s,old,new):
    n=s.count(old)
    if n!=1:raise AssertionError(f'Expected exactly one {old!r}, got {n}')
    return s.replace(old,new)


def map_extend(old,new,classes,expected_len):
    with old.open(newline='',encoding='utf-8') as f:
        r=csv.DictReader(f);fieldnames=r.fieldnames;items=list(r)
    assert fieldnames == ['source_class','english_literal','polish_ascii_draft','status']
    assert len(items)==expected_len,(len(items),expected_len)
    keys={(r['source_class'],r['english_literal']) for r in items}
    entries=[]
    for cls in classes:
        for en,pl in PATTERNS.items():
            assert (cls,en) not in keys,(cls,en)
            entries.append({'source_class':cls,'english_literal':en,'polish_ascii_draft':pl,
                            'status':'VERIFIED_SUBJECT_PRONOUN_1018'})
    with new.open('w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,fieldnames=fieldnames,lineterminator='\r\n')
        wr.writeheader();wr.writerows(items+entries)
    assert new.read_bytes().startswith(old.read_bytes())
    return len(items)+len(entries)


def main(root):
    obf=root/'buildtools/NARZEDZIA_OBF'
    api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
    num_o=map_extend(obf/'TLUMACZENIA_OBF_10117.csv',obf/'TLUMACZENIA_OBF_10118.csv',OBF_CLASSES,3140)
    num_a=map_extend(api/'translations/TLUMACZENIA_JAR_1017.csv',api/'translations/TLUMACZENIA_JAR_1018.csv',API_CLASSES,5096)
    path=obf/'main.go';s=path.read_text('utf-8')
    s=exact(s,'TLUMACZENIA_OBF_10116.csv TLUMACZENIA_OBF_10117.csv','TLUMACZENIA_OBF_10116.csv TLUMACZENIA_OBF_10117.csv TLUMACZENIA_OBF_10118.csv')
    s=exact(s,'const currentPatchState = "patched 10117"','const currentPatchState = "patched 10118"')
    s=exact(s,'table, e := loadTranslations("TLUMACZENIA_OBF_10117.csv")','table, e := loadTranslations("TLUMACZENIA_OBF_10118.csv")')
    s=exact(s,'var knownPreviousOBFHashes = map[string]string{','var knownPreviousOBFHashes = map[string]string{\n\t"c5035d4c06b747604652760b162ed163ebdf6a956d419963c38f594ad0fa1a11": "10117",')
    s=exact(s,'if state == currentPatchState || state == "patched 10116"','if state == currentPatchState || state == "patched 10117" || state == "patched 10116"')
    s=exact(s,'| OBF 1.0.17 | stan:','| OBF 1.0.18 | stan:')
    s=exact(s,'1.0.17: Lokalizacja tekstow OBF','1.0.18: Lokalizacja tekstow OBF')
    s=exact(s,'PL ASCII OBF 0.9.99-1.0.17','PL ASCII OBF 0.9.99-1.0.18')
    path.write_text(s,'utf-8')
    path=obf/'main_test.go';s=path.read_text('utf-8')
    s=exact(s,'if !alreadyThisRelease("patched 10117") {','if !alreadyThisRelease("patched 10118") {')
    s=exact(s,'[]string{"original", "patched 10116",','[]string{"original", "patched 10117", "patched 10116",')
    path.write_text(s,'utf-8')
    path=obf/'mapping_10117_test.go';s=path.read_text('utf-8')
    s=exact(s,'if !alreadyThisRelease("patched 10117") || alreadyThisRelease("patched 10116")',
              'if alreadyThisRelease("patched 10117") || alreadyThisRelease("patched 10116")')
    path.write_text(s,'utf-8')
    (obf/'mapping_10118_test.go').write_text('''package main
import "testing"
func TestOBF10118SubjectPronouns(t *testing.T) {
  m,err:=loadTranslations("TLUMACZENIA_OBF_10118.csv")
  if err!=nil { t.Fatal(err) }
  if len(m)!=533 { t.Fatalf("unexpected class count %d",len(m)) }
  if knownPreviousOBFHashes["c5035d4c06b747604652760b162ed163ebdf6a956d419963c38f594ad0fa1a11"]!="10117" { t.Fatal("missing prior release") }
  if !alreadyThisRelease("patched 10118") || alreadyThisRelease("patched 10117") { t.Fatal("version recognition") }
}
''',encoding='utf-8')
    path=api/'main.go';s=path.read_text('utf-8')
    s=exact(s,'const version = "1017"','const version = "1018"')
    s=exact(s,'const exeVersion = "1.0.17"','const exeVersion = "1.0.18"')
    s=exact(s,'"1013", "1014", "1015", "1016", version}', '"1013", "1014", "1015", "1016", "1017", version}')
    # The initial overlay uses a placeholder until we derive the exact current OBF checksum.
    s=exact(s,'const expectedOBFPatched10117 = "c5035d4c06b747604652760b162ed163ebdf6a956d419963c38f594ad0fa1a11"',
              'const expectedOBFPatched10117 = "c5035d4c06b747604652760b162ed163ebdf6a956d419963c38f594ad0fa1a11"\nconst expectedOBFPatched10118 = "c95b45715e4d7c1b982d154acdc6776a3cf60756e83eefb00ea526a96c5a6c92"')
    s=exact(s,'if hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10117',
              'if hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10118 && hash(obf) != expectedOBFPatched10117')
    s=exact(s,'PL ASCII patch up to 1.0.17','PL ASCII patch up to 1.0.18')
    path.write_text(s,'utf-8')
    path=root/'buildtools/NARZEDZIA_INSTALATOR/main.go';s=path.read_text('utf-8')
    s=exact(s,'const edition = "1.0.17"','const edition = "1.0.18"');path.write_text(s,'utf-8')
    path=root/'mod/mod_info.json';meta=json.loads(path.read_text('utf-8'))
    assert meta['version']=='1.0.17';meta['version']='1.0.18';meta['description']=meta['description'].replace('1.0.17','1.0.18')
    path.write_text(json.dumps(meta,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')
    path=root/'mod/CZYTAJ.txt';s=path.read_text('utf-8')
    s=exact(s,'STARSECTOR PL ASCII 1.0.17','STARSECTOR PL ASCII 1.0.18')
    s+='\nPrzetlumaczono zaimki podmiotowe w dialogach i w opisie postaci.\n'
    path.write_text(s,'utf-8')
    print(f'1.0.18: {num_o} OBF map rows, {num_a} API map rows; six subject pronouns only')

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('worktree',type=Path)
 main(ap.parse_args().worktree)