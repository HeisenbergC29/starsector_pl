#!/usr/bin/env python3
"""Idempotent source overlay 1.0.15 -> 1.0.16 (no original game files bundled).

Only string literals and configuration of patchers are changed.
Requires the prior 1.0.12 -> 1.0.13 -> 1.0.14 -> 1.0.15 overlays.
"""
import csv, json, re
from pathlib import Path

OBF = [{'source_class': 'com.fs.starfarer.campaign.ui.marketinfo.CommodityDetailDialog',
  'english_literal': 'Market name; "current" after the name indicates that ',
  'polish_ascii_draft': 'Nazwa rynku; dopisek "obecny" po nazwie oznacza, ze ',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1016'},
 {'source_class': 'com.fs.starfarer.campaign.ui.intel.H$3',
  'english_literal': 'Store the current planet filter settings so they can be loaded later. Can also press '
                     '{{Ctrl-S}}.',
  'polish_ascii_draft': 'Zapisz biezace ustawienia filtrow planet, aby moc je pozniej przywrocic. Mozesz tez '
                        'nacisnac {{Ctrl-S}}.',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1016'},
 {'source_class': 'com.fs.starfarer.launcher.opengl.ooOO',
  'english_literal': 'Warning - memory settings will not apply because the JVM will not be restarted on launch '
                     'due to settings.json configuration',
  'polish_ascii_draft': 'Uwaga - ustawienia pamieci nie zostana zastosowane, poniewaz konfiguracja settings.json '
                        'nie pozwala na ponowne uruchomienie JVM przy starcie gry.',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1016'},
 {'source_class': 'com.fs.starfarer.campaign.save.CampaignGameManager',
  'english_literal': 'Save game operation produced a corrupted file. Your previous save is unaffected.\n'
                     '\n'
                     'Please try saving again; if that doesn\'t work, use the "Save Copy" option from the '
                     'campaign menu.',
  'polish_ascii_draft': 'Operacja zapisu utworzyla uszkodzony plik. Poprzedni zapis gry pozostal nienaruszony.\n'
                        '\n'
                        'Sprobuj zapisac gre ponownie. Jesli to nie pomoze, uzyj opcji "Zapisz kopie" w menu '
                        'kampanii.',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1016'}]

API = [{'source_class': 'com.fs.starfarer.api.impl.campaign.intel.bar.events.LuddicFarmerBarEvent',
  'english_literal': ' says with a wink, "As pious folk, we need not bother with the Church’s tariff.",',
  'polish_ascii_draft': ' mowi z mrugnieciem oka: "Jako pobozni ludzie nie musimy przejmowac sie oplata pobierana '
                        'przez Kosciol.",',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1016'},
 {'source_class': 'com.fs.starfarer.api.impl.campaign.intel.bar.events.ScientistAICoreBarEvent',
  'english_literal': '"The data doesn’t lie!" ',
  'polish_ascii_draft': '"Dane nie klamia!" - ',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1016'},
 {'source_class': 'com.fs.starfarer.api.impl.campaign.intel.bar.events.ScientistAICoreBarEvent',
  'english_literal': 'though you can’t make sense of the arcane tables scrolling ',
  'polish_ascii_draft': 'chociaz nie potrafisz zrozumiec zagadkowych tabel przewijajacych sie ',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1016'},
 {'source_class': 'com.fs.starfarer.api.impl.campaign.intel.bar.events.ScientistAICoreBarEvent',
  'english_literal': 'on ',
  'polish_ascii_draft': 'na ',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1016'},
 {'source_class': 'com.fs.starfarer.api.impl.campaign.intel.bar.events.ScientistAICoreBarEvent',
  'english_literal': ' greasy TriPad. "There’s an enormous stock of ',
  'polish_ascii_draft': ' zatluszczonym TriPadzie. "W tym ukladzie sa ogromne zasoby ',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1016'},
 {'source_class': 'com.fs.starfarer.api.impl.campaign.intel.bar.events.historian.HistorianBarEvent',
  'english_literal': '"I am what you might call a historian-adventurer; a rogue archaelogist uncovering the '
                     'history of the Sector despite the danger of this exceptional era. In the course of my '
                     'studies I often chance upon hints about where certain pieces of technology might be found. '
                     "Retrieving those artifacts is, naturally, your role in our arrangement. ... Only if you're "
                     "interested, of course - but I've done my research on your exploits and I'm sure that you "
                     'will be interested."\n'
                     '\n'
                     'Speech complete, ',
  'polish_ascii_draft': '"Jestem, mozna powiedziec, historykiem-poszukiwaczem przygod; archeologiem poza prawem, '
                        'ktory mimo niebezpieczenstw naszych czasow odkrywa historie Sektora. Podczas badan '
                        'czesto natrafiam na wskazowki, gdzie mozna znalezc dawne technologie. Odzyskiwanie tych '
                        'artefaktow to oczywiscie twoja rola w naszym ukladzie. ... O ile jestes zainteresowany. '
                        'Zbadalem twoje dokonania i jestem pewien, ze tak bedzie."\n'
                        '\n'
                        'Po tych slowach ',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1016'},
 {'source_class': 'com.fs.starfarer.api.impl.campaign.intel.bar.events.historian.HistorianBarEvent',
  'english_literal': '"I understand why you would assume that; this is a mercenary age. But no, nothing quite so '
                     'transactional. History is an uncertain trade, and such an approach would lead to '
                     "expectations, disappointment, and recrimination. All of which I'm eager to avoid, "
                     'especially the last." An additional wrinkle forms on ',
  'polish_ascii_draft': '"Rozumiem, dlaczego tak sadzisz; zyjemy w epoce najemnikow. Ale nie, nie chodzi mi o tak '
                        'prosta transakcje. Historia jest niepewnym zajeciem, a taki uklad prowadzilby do '
                        'oczekiwan, rozczarowan i wzajemnych oskarzen. Wole uniknac wszystkiego, zwlaszcza tego '
                        'ostatniego." Kolejna zmarszczka pojawia sie na ',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1016'},
 {'source_class': 'com.fs.starfarer.api.impl.campaign.procgen.PlayerFleetGenPluginImpl',
  'english_literal': "Add officers (number / level / elite skills based on your character's skills)",
  'polish_ascii_draft': 'Dodaj oficerow (liczba, poziom i umiejetnosci elitarne zalezne od umiejetnosci postaci)',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1016'},
 {'source_class': 'com.fs.starfarer.api.impl.campaign.procgen.PlayerFleetGenPluginImpl',
  'english_literal': 'Average of 2 s-mods; allow some Omega weapons to be mounted',
  'polish_ascii_draft': 'Srednio 2 wbudowane modyfikacje; mozna zamontowac niektore bronie Omega',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1016'},
 {'source_class': 'com.fs.starfarer.api.impl.campaign.procgen.PlayerFleetGenPluginImpl',
  'english_literal': 'Average of 3 s-mods; allow some Omega weapons to be mounted',
  'polish_ascii_draft': 'Srednio 3 wbudowane modyfikacje; mozna zamontowac niektore bronie Omega',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1016'},
 {'source_class': 'com.fs.starfarer.api.impl.campaign.fleets.SDFLeague',
  'english_literal': 'Pride of Hannan',
  'polish_ascii_draft': 'Duma Hannana',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1016'},
 {'source_class': 'com.fs.starfarer.api.impl.campaign.fleets.SDFLeague',
  'english_literal': 'Pride of Kato',
  'polish_ascii_draft': 'Duma Kato',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1016'},
 {'source_class': 'com.fs.starfarer.api.impl.campaign.fleets.SDFLeague',
  'english_literal': 'Pride of Yaribay',
  'polish_ascii_draft': 'Duma Yaribaya',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1016'},
 {'source_class': 'com.fs.starfarer.api.impl.campaign.fleets.SDFLeague',
  'english_literal': "Reynard's Gift",
  'polish_ascii_draft': 'Dar Reynarda',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1016'},
 {'source_class': 'com.fs.starfarer.api.impl.campaign.fleets.SDFLeague',
  'english_literal': "Fortuna's Gift",
  'polish_ascii_draft': 'Dar Fortuny',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1016'},
 {'source_class': 'com.fs.starfarer.api.impl.campaign.fleets.SDFLeague',
  'english_literal': 'Mairaath Remembered',
  'polish_ascii_draft': 'Pamiec o Mairaath',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1016'},
 {'source_class': 'com.fs.starfarer.api.impl.campaign.fleets.SDFLeague',
  'english_literal': 'All-League Aegis',
  'polish_ascii_draft': 'Egida calej Ligi',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1016'}]



def replace_exact(data, old, new):
    count=data.count(old)
    if count!=1:raise AssertionError(f'Expected one match, found {count}: {old[:100]!r}')
    return data.replace(old,new)


def add_rows(old,output,rows,expected):
    with old.open(newline='',encoding='utf-8') as f:
        items=list(csv.DictReader(f))
    if len(items)!=expected:raise AssertionError((old,len(items),expected))
    prev={(r['source_class'],r['english_literal']) for r in items}
    for row in rows:
        if (row['source_class'],row['english_literal']) in prev:raise AssertionError('duplicate translation')
        if not row['polish_ascii_draft'].isascii():raise AssertionError('non ASCII target')
        if row['english_literal'].count('\n')!=row['polish_ascii_draft'].count('\n'):raise AssertionError('newline drift')
        def marks(s):return sorted(re.findall(r'\{\{[^{}]+\}\}|\$[A-Za-z_][\w]*|%(?:(?:\d+)\$)?[-+# 0,(]*(?:\d+)?(?:\.\d+)?[a-zA-Z%]',s))
        if marks(row['english_literal'])!=marks(row['polish_ascii_draft']):raise AssertionError('format marks drift '+row['english_literal'][:60])
    with output.open('w',newline='',encoding='utf-8') as stream:
        wr=csv.DictWriter(stream,fieldnames=['source_class','english_literal','polish_ascii_draft','status'],lineterminator='\r\n')
        wr.writeheader();wr.writerows(items+rows)
    return len(items)+len(rows)


def main(worktree):
    obfdir=worktree/'buildtools/NARZEDZIA_OBF'
    apidir=worktree/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
    n1=add_rows(obfdir/'TLUMACZENIA_OBF_10115.csv',obfdir/'TLUMACZENIA_OBF_10116.csv',OBF,3121)
    n2=add_rows(apidir/'translations/TLUMACZENIA_JAR_1015.csv',apidir/'translations/TLUMACZENIA_JAR_1016.csv',API,5077)
    p=obfdir/'main.go';s=p.read_text(encoding='utf-8')
    s=replace_exact(s,'TLUMACZENIA_OBF_10109.csv TLUMACZENIA_OBF_10115.csv','TLUMACZENIA_OBF_10109.csv TLUMACZENIA_OBF_10115.csv TLUMACZENIA_OBF_10116.csv')
    s=replace_exact(s,'const currentPatchState = "patched 10115"','const currentPatchState = "patched 10116"')
    s=replace_exact(s,'table, e := loadTranslations("TLUMACZENIA_OBF_10115.csv")','table, e := loadTranslations("TLUMACZENIA_OBF_10116.csv")')
    s=replace_exact(s,'var knownPreviousOBFHashes = map[string]string{','var knownPreviousOBFHashes = map[string]string{\n\t"6fbf5af6e570de156ef40c7f8a3684fafa582f1a981da51c2e1aeb5e4a24d087": "10115",')
    s=replace_exact(s,'if state == currentPatchState || state == "patched 10109"','if state == currentPatchState || state == "patched 10115" || state == "patched 10109"')
    s=replace_exact(s,'| OBF 1.0.15 | stan:', '| OBF 1.0.16 | stan:')
    s=replace_exact(s,'1.0.15: Lokalizacja tekstow OBF','1.0.16: Lokalizacja tekstow OBF')
    s=replace_exact(s,'PL ASCII OBF 0.9.99-1.0.15','PL ASCII OBF 0.9.99-1.0.16')
    p.write_text(s,encoding='utf-8')
    p=obfdir/'main_test.go';s=p.read_text(encoding='utf-8')
    s=replace_exact(s,'if !alreadyThisRelease("patched 10115") {','if !alreadyThisRelease("patched 10116") {')
    s=replace_exact(s,'[]string{"original", "patched 10109"','[]string{"original", "patched 10115", "patched 10109"')
    p.write_text(s,encoding='utf-8')
    p=obfdir/'mapping_10115_test.go';s=p.read_text(encoding='utf-8')
    s=replace_exact(s,'if !alreadyThisRelease("patched 10115") { t.Fatal("latest OBF not recognized") }','if alreadyThisRelease("patched 10115") { t.Fatal("older OBF incorrectly treated as current") }')
    p.write_text(s,encoding='utf-8')
    (obfdir/'mapping_10116_test.go').write_text("""package main
import "testing"
func TestOBF10116MappingAnd10115Upgrade(t *testing.T) {
  m,err:=loadTranslations("TLUMACZENIA_OBF_10116.csv")
  if err!=nil { t.Fatal(err) }
  if len(m)!=527 { t.Fatalf("unexpected class count %d",len(m)) }
  if knownPreviousOBFHashes["6fbf5af6e570de156ef40c7f8a3684fafa582f1a981da51c2e1aeb5e4a24d087"]!="10115" {t.Fatal("old patch missing")}
  if alreadyThisRelease("patched 10115") { t.Fatal("old treated as current") }
  if !alreadyThisRelease("patched 10116") {t.Fatal("new not current")}
}
""",encoding='utf-8')
    p=apidir/'main.go';s=p.read_text(encoding='utf-8')
    s=replace_exact(s,'const version = "1015"','const version = "1016"')
    s=replace_exact(s,'const exeVersion = "1.0.15"','const exeVersion = "1.0.16"')
    s=replace_exact(s,'"1013", "1014", version}', '"1013", "1014", "1015", version}')
    s=replace_exact(s,'const expectedOBFPatched10115 = "6fbf5af6e570de156ef40c7f8a3684fafa582f1a981da51c2e1aeb5e4a24d087"', 'const expectedOBFPatched10115 = "6fbf5af6e570de156ef40c7f8a3684fafa582f1a981da51c2e1aeb5e4a24d087"\nconst expectedOBFPatched10116 = "c3dcae2341f5fa96cb92b6a1cb1a59ec5f32cdf4579f77fe5ad30985764ee78c"')
    s=replace_exact(s,'if hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10115','if hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10116 && hash(obf) != expectedOBFPatched10115')
    s=replace_exact(s,'PL ASCII patch up to 1.0.15','PL ASCII patch up to 1.0.16')
    p.write_text(s,encoding='utf-8')
    p=worktree/'buildtools/NARZEDZIA_INSTALATOR/main.go';s=p.read_text(encoding='utf-8')
    s=replace_exact(s,'const edition = "1.0.15"','const edition = "1.0.16"')
    p.write_text(s,encoding='utf-8')
    p=worktree/'mod/mod_info.json';meta=json.loads(p.read_text(encoding='utf-8'))
    if meta['version']!='1.0.15':raise AssertionError('expected base 1.0.15')
    meta['version']='1.0.16';meta['description']=meta['description'].replace('1.0.15','1.0.16')
    p.write_text(json.dumps(meta,ensure_ascii=True,indent=2)+'\n',encoding='utf-8')
    p=worktree/'mod/CZYTAJ.txt';s=p.read_text(encoding='utf-8')
    s=replace_exact(s,'STARSECTOR PL ASCII 1.0.15','STARSECTOR PL ASCII 1.0.16')
    s+='\nDodano opisy UI, rozmowy i przetlumaczono nazwy okretow Ligi.\n'
    p.write_text(s,encoding='utf-8')
    print(f'1.0.16: OBF map {n1} rows (+{len(OBF)}), API map {n2} rows (+{len(API)})')

if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('worktree',type=Path)
    main(a.parse_args().worktree)