#!/usr/bin/env python3
"""Deterministic source overlay 1.0.15: OBF and API UI strings only.

Run after 1.0.13 and 1.0.14 overlays. Original proprietary game files are NOT
part of the repository. The script modifies only translation tables and patcher
source configuration, never game resources or original JVM bytecode.
"""
import csv
import json
from pathlib import Path

OBF = [{'source_class': 'com.fs.starfarer.campaign.command.IntelIncomePanel',
  'english_literal': '\n'
                     '\n'
                     'Asterisks (*) indicate values that are below the top level. Values without '
                     'asterisks are directly applied to your credit balance; values with asterisks are '
                     'included in those.',
  'polish_ascii_draft': '\n'
                        '\n'
                        'Gwiazdki (*) oznaczaja wartosci uwzglednione w pozycjach podrzednych. Kwoty '
                        'bez gwiazdek sa naliczane bezposrednio do salda kredytow, natomiast kwoty z '
                        'gwiazdkami zawieraja sie juz w pozycjach nadrzednych.',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1015'},
 {'source_class': 'com.fs.starfarer.campaign.ui.marketinfo.CommodityDetailDialog',
  'english_literal': 'Market name or "local production"; "current" after the name indicates that it\'s '
                     'the current supplier.',
  'polish_ascii_draft': 'Nazwa rynku lub "produkcja lokalna"; dopisek "obecny" po nazwie wskazuje '
                        'aktualnego dostawce.',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1015'},
 {'source_class': 'com.fs.starfarer.campaign.ui.marketinfo.GroundRaidTargetPickerDialog',
  'english_literal': 'Danger level your marines will face to achieve this objective. Higher danger '
                     'level increases casualties.\n'
                     '\n'
                     'Casualties are also affected by other factors; hover over the "Projected marine '
                     'casualties" for details.',
  'polish_ascii_draft': 'Poziom zagrozenia, na jakie narazona jest piechota morska podczas realizacji '
                        'tego celu. Wyzszy poziom zagrozenia oznacza wieksze straty.\n'
                        '\n'
                        'Na liczbe ofiar wplywaja takze inne czynniki. Najedz kursorem na "Przewidywane '
                        'straty piechoty morskiej", aby poznac szczegoly.',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1015'},
 {'source_class': 'com.fs.starfarer.campaign.ui.marketinfo.GroundRaidTargetPickerDialog',
  'english_literal': 'Danger level your marines will face to achieve this objective. Higher danger '
                     'level increases casualties.\n'
                     '\n'
                     'Certain commodities and items are inherently more dangerous to acquire.\n'
                     '\n'
                     'A commodity shortage makes an operation more dangerous, while excess stockpiles '
                     'are more easily accessible and decrease the risks faced by your marines. In '
                     "addition, a commodity that's locally produced - rather than imported - is less "
                     'dangerous to acquire.\n'
                     '\n'
                     'Casualties are also affected by other factors; hover over the "Projected marine '
                     'casualties" for details.',
  'polish_ascii_draft': 'Poziom zagrozenia, na jakie narazona jest piechota morska podczas realizacji '
                        'tego celu. Wyzszy poziom zagrozenia oznacza wieksze straty.\n'
                        '\n'
                        'Niektore towary i przedmioty z natury trudniej zdobyc.\n'
                        '\n'
                        'Niedobor towaru zwieksza ryzyko operacji, podczas gdy nadwyzki w magazynach sa '
                        'latwiej dostepne i zmniejszaja zagrozenie dla piechoty morskiej. Towary '
                        'wytwarzane na miejscu sa ponadto latwiejsze do zdobycia niz towary '
                        'importowane.\n'
                        '\n'
                        'Na liczbe ofiar wplywaja rowniez inne czynniki. Najedz kursorem na '
                        '"Przewidywane straty piechoty morskiej", aby poznac szczegoly.',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1015'},
 {'source_class': 'com.fs.starfarer.combat.CombatState',
  'english_literal': 'Are you sure?\n'
                     '\n'
                     'Ordering a full assault will cancel all existing assignments and make your ships '
                     'engage the enemy forces more aggressively, potentially exposing them to greater '
                     'danger.\n'
                     '\n'
                     'Creating a new assignment (other than "Eliminate" or "Fighter Strike") will '
                     'cancel this order; toggling it off directly uses a command point.',
  'polish_ascii_draft': 'Na pewno?\n'
                        '\n'
                        'Rozkaz pelnego natarcia anuluje wszystkie dotychczasowe zadania i sklania '
                        'okrety do bardziej agresywnego atakowania przeciwnika, przez co beda narazone '
                        'na wieksze niebezpieczenstwo.\n'
                        '\n'
                        'Utworzenie nowego zadania (innego niz "Wyeliminuj" lub "Atak mysliwcow") '
                        'anuluje ten rozkaz. Bezposrednie wylaczenie rozkazu zuzywa punkt dowodzenia.',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1015'}]
API = [{'source_class': 'com.fs.starfarer.api.impl.campaign.PlanetInteractionDialogPluginImpl',
  'english_literal': 'Your sensors officer hesitates, then calls for your attention. "Captain, there\'s '
                     'a... pattern. From the black hole. Or, rather," they pause, looking almost '
                     'embarrassed. "-The energy radiated by the accretion disc.\n'
                     '\n'
                     'They pull a collated sensor output map into the primary holo. "It\'s almost a '
                     'signal. See, if we chart these fluctuations in energy output over time...\n'
                     '\n'
                     'You see it now, an orderly series. Not quite a sequence of prime numbers, unless '
                     'you jig the math. Statistically this is nearly impossible. Possible explanations '
                     'are as unlikely: a series of planets - large moons? - with specific mass-ratio '
                     'relationships, all pulled into the accretion disc at just such an angle, like an '
                     'intentional message... or orderly annihilation of a constructed planetary system '
                     'at a scale beyond the wildest dreams of the most bloody-minded war-planners of '
                     'the Domain.\n'
                     '\n'
                     "It can't be known. The pattern disappears as quickly as it arose.",
  'polish_ascii_draft': 'Oficer czujnikow waha sie przez chwile, po czym zwraca na siebie twoja uwage. '
                        '"Kapitanie, dostrzegam pewien... wzorzec. Pochodzi z czarnej dziury. A '
                        'raczej..." - zawiesza glos, niemal zaklopotany. "Z energii emitowanej przez '
                        'dysk akrecyjny."\n'
                        '\n'
                        'Na glownym hologramie pojawia sie zestawienie odczytow. "To niemal sygnal. '
                        'Jesli przedstawimy zmiany emitowanej energii w czasie..."\n'
                        '\n'
                        'Teraz sam to widzisz: regularny ciag. Nie sa to dokladnie liczby pierwsze, '
                        'chyba ze odpowiednio nagiac obliczenia. Statystycznie cos takiego jest niemal '
                        'niemozliwe. Pozostale wyjasnienia wydaja sie rownie nieprawdopodobne: szereg '
                        'planet, moze wielkich ksiezycow, powiazanych okreslonymi stosunkami mas, '
                        'wciagnietych do dysku akrecyjnego pod odpowiednim katem, niczym celowo wyslana '
                        'wiadomosc... albo uporzadkowana zaglada sztucznie stworzonego ukladu '
                        'planetarnego na skale przekraczajaca najdziksze marzenia najbardziej '
                        'krwiozerczych strategow Domeny.\n'
                        '\n'
                        'Nie sposob poznac prawdy. Wzorzec znika rownie szybko, jak sie pojawil.',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1015'},
 {'source_class': 'com.fs.starfarer.api.impl.campaign.rulecmd.salvage.special.ShipRecoverySpecial',
  'english_literal': '"Commander, looks like we might be able to pull this off, though I\'ll say '
                     "you're not going to find what I'm going to do in any manual. And it wouldn't pass "
                     "any inspection, but then again we're not in the Hegemony fleet. These ships can "
                     'be made to fly again, though.',
  'polish_ascii_draft': '"Dowodco, chyba mozemy tego dokonac, ale nie znajdzie pan takiej procedury w '
                        'zadnym podreczniku. Nie przeszlaby tez zadnej inspekcji, ale przeciez nie '
                        'sluzymy we flocie Hegemonii. Te okrety mozna jeszcze przywrocic do lotu."',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1015'},
 {'source_class': 'com.fs.starfarer.api.impl.campaign.intel.bar.events.ScientistAICoreBarEvent',
  'english_literal': 'That, I get to keep. I’ll tell you exactly where to look if you agree to my '
                     'terms."',
  'polish_ascii_draft': 'Ten rdzen zostaje u mnie. Jesli przyjmiesz moje warunki, wskaze ci dokladnie, '
                        'gdzie szukac."',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1015'}]


def write_overlay(old,new,additions,expected_rows):
    with old.open(newline='',encoding='utf8') as f:
        items=list(csv.DictReader(f))
    assert len(items)==expected_rows,(old,len(items),expected_rows)
    known={(r['source_class'],r['english_literal']) for r in items}
    for a in additions:
        assert (a['source_class'],a['english_literal']) not in known
        assert a['polish_ascii_draft'].isascii()
        assert a['english_literal'].count('\n')==a['polish_ascii_draft'].count('\n')
        assert a['english_literal'].count('%s')==a['polish_ascii_draft'].count('%s')
    with new.open('w',newline='',encoding='utf8') as f:
        wr=csv.DictWriter(f,fieldnames=['source_class','english_literal','polish_ascii_draft','status'],lineterminator='\r\n')
        wr.writeheader();wr.writerows(items+additions)
    return len(items)+len(additions)


def exact_replace(s,a,b):
    assert s.count(a)==1,(a,s.count(a))
    return s.replace(a,b)


def main(worktree):
    obfdir=worktree/'buildtools/NARZEDZIA_OBF'
    apidir=worktree/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
    nr1=write_overlay(obfdir/'TLUMACZENIA_OBF_10109.csv',obfdir/'TLUMACZENIA_OBF_10115.csv',OBF,3116)
    nr2=write_overlay(apidir/'translations/TLUMACZENIA_JAR_1014.csv',apidir/'translations/TLUMACZENIA_JAR_1015.csv',API,5074)
    oldsha='86662fa0e5fe95d9cf3aa8010df80fcb1dc1994e3b752515f8fd2692fd853beb'
    p=obfdir/'main.go';s=p.read_text(encoding='utf8')
    s=exact_replace(s,'TLUMACZENIA_OBF_10108.csv TLUMACZENIA_OBF_10109.csv','TLUMACZENIA_OBF_10108.csv TLUMACZENIA_OBF_10109.csv TLUMACZENIA_OBF_10115.csv')
    s=exact_replace(s,'const currentPatchState = "patched 10109"','const currentPatchState = "patched 10115"')
    s=exact_replace(s,'table, e := loadTranslations("TLUMACZENIA_OBF_10109.csv")','table, e := loadTranslations("TLUMACZENIA_OBF_10115.csv")')
    s=exact_replace(s,'var knownPreviousOBFHashes = map[string]string{','var knownPreviousOBFHashes = map[string]string{\n\t"'+oldsha+'": "10109",')
    s=exact_replace(s,'if state == currentPatchState || state == "patched 10108"','if state == currentPatchState || state == "patched 10109" || state == "patched 10108"')
    s=exact_replace(s,'| OBF 1.0.10 | stan:','| OBF 1.0.15 | stan:')
    s=exact_replace(s,'1.0.7: Lokalizacja tekstow OBF','1.0.15: Lokalizacja tekstow OBF')
    s=exact_replace(s,'PL ASCII OBF 0.9.99-1.0.10','PL ASCII OBF 0.9.99-1.0.15')
    p.write_text(s,encoding='utf8')
    p=obfdir/'main_test.go';s=p.read_text(encoding='utf8')
    s=exact_replace(s,'if !alreadyThisRelease("patched 10109") {','if !alreadyThisRelease("patched 10115") {')
    s=exact_replace(s,'[]string{"original", "patched 10108"','[]string{"original", "patched 10109", "patched 10108"')
    p.write_text(s,encoding='utf8')
    (obfdir/'mapping_10115_test.go').write_text("""package main

import "testing"

func TestOBF10115MappedAndRecognizes10109Upgrade(t *testing.T) {
    m, err := loadTranslations("TLUMACZENIA_OBF_10115.csv")
    if err != nil { t.Fatal(err) }
    if len(m) != 526 { t.Fatalf("unexpected affected class count: %d",len(m)) }
    old := "86662fa0e5fe95d9cf3aa8010df80fcb1dc1994e3b752515f8fd2692fd853beb"
    if knownPreviousOBFHashes[old] != "10109" {t.Fatal("1.0.14 OBF is not recognized for upgrade")}
    if alreadyThisRelease("patched 10109") { t.Fatal("older OBF incorrectly treated as current") }
    if !alreadyThisRelease("patched 10115") { t.Fatal("latest OBF not recognized") }
}
""",encoding='utf8')
    p=apidir/'main.go';s=p.read_text(encoding='utf8')
    s=exact_replace(s,'const version = "1014"','const version = "1015"')
    s=exact_replace(s,'const exeVersion = "1.0.14"','const exeVersion = "1.0.15"')
    s=exact_replace(s,'"1010", "1013", version}','"1010", "1013", "1014", version}')
    # API validates the OBF hash on every operation. New OBF must be allowlisted
    # or the combined installer will fail after the first patcher succeeds.
    s=exact_replace(s,'const expectedOBF = "5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8"',
      'const expectedOBF = "5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8"\nconst expectedOBFPatched10115 = "6fbf5af6e570de156ef40c7f8a3684fafa582f1a981da51c2e1aeb5e4a24d087"')
    s=exact_replace(s,'if hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10108',
      'if hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10115 && hash(obf) != expectedOBFPatched10108')
    s=exact_replace(s,'PL ASCII patch up to 1.0.8','PL ASCII patch up to 1.0.15')
    s=exact_replace(s,'// Source text may use non-ASCII UTF-8, while replacements stay ASCII.\n\t\t// Avoid matching malformed sequences (e.g. modified UTF-8 null).',
        '// Class-file CONSTANT_Utf8 bytes are preserved verbatim. For common\n\t\t// non-ASCII characters (e.g. U+00D7 multiplication sign), JVM\n\t\t// modified UTF-8 agrees with UTF-8. Reject malformed variants here.')
    p.write_text(s,encoding='utf8')
    p=worktree/'buildtools/NARZEDZIA_INSTALATOR/main.go';s=p.read_text(encoding='utf8')
    s=exact_replace(s,'const edition = "1.0.14"','const edition = "1.0.15"')
    p.write_text(s,encoding='utf8')
    p=worktree/'mod/mod_info.json';j=json.loads(p.read_text(encoding='utf8'))
    assert j['version']=='1.0.14'
    j['version']='1.0.15';j['description']=j['description'].replace('1.0.14','1.0.15')
    p.write_text(json.dumps(j,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
    p=worktree/'mod/CZYTAJ.txt';s=p.read_text(encoding='utf8')
    s=exact_replace(s,'STARSECTOR PL ASCII 1.0.14','STARSECTOR PL ASCII 1.0.15')
    s += '\nDodano 5 opisow UI OBF i 3 teksty Java API (8 podmian).\n'
    p.write_text(s,encoding='utf8')
    print(f'1.0.15: OBF={nr1}, API={nr2}, 5 OBF + 3 API')

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('worktree',type=Path);args=ap.parse_args()
    main(args.worktree)