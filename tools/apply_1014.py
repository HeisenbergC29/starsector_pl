#!/usr/bin/env python3
"""Apply reviewed 1.0.14 localized Java UI strings to 1.0.13 worktree."""
import csv, io, json, re
from pathlib import Path

ADDITIONS = [{'source_class': 'com.fs.starfarer.api.impl.campaign.PlanetInteractionDialogPluginImpl', 'english_literal': 'Your officers respond promptly to the order, and move to the task with all alacrity. There is an edge to their call-and-response, however, as if they cannot help but acknowledge the deep sense of the gravity in this act.\n"Package ready to drop, captain," your ops chief says. "On your order."', 'polish_ascii_draft': 'Twoi oficerowie natychmiast wykonuja rozkaz i przystepuja do zadania z pelnym zaangazowaniem. W ich odpowiedziach slychac jednak napiecie, jakby nie potrafili ukryc swiadomosci powagi tego czynu.\n"Ladunek gotowy do zrzutu, kapitanie" - melduje szef operacyjny. "Czekamy na rozkaz."', 'status': 'REVIEWED_UI_CALLSITE_1014'}, {'source_class': 'com.fs.starfarer.api.impl.campaign.intel.PerseanLeagueMembership', 'english_literal': "You've joined the Persean League, though it's whispered that you only did so to avoid harassment, and your membership dues are nothing more than protection payments. However, the League still supports you politically, which for example makes it untenable for the Hegemony to insist on AI inspections in your space.", 'polish_ascii_draft': 'Dolaczyles do Ligi Perseanskiej, choc kraza pogloski, ze zrobiles to tylko po to, by uniknac nekania, a skladki czlonkowskie sa po prostu haraczem za ochrone. Mimo to Liga udziela ci poparcia politycznego, przez co Hegemonia nie moze w praktyce nalegac na kontrole SI na twoim terytorium.', 'status': 'REVIEWED_UI_CALLSITE_1014'}, {'source_class': 'com.fs.starfarer.api.impl.campaign.intel.bar.events.DiktatLobsterBarEvent', 'english_literal': "What this amounts to, you are told, is that the District 4 Gendarmerie's evidence locker - and maintenance bay, and several interrogation rooms - are filled with cases of cryo-stabilized Volturnian Lobster, nearly %s units in all. The officers eat like royalty, yes, but there's only so much one can take and the coolant cells won't last another week without replacement, so.\n\n", 'polish_ascii_draft': 'Jak sie dowiadujesz, magazyn dowodow Zandarmerii Dystryktu 4 - a takze warsztat naprawczy i kilka sal przesluchan - sa zapchane skrzyniami kriogenicznie zakonserwowanych homarow z Volturn, lacznie prawie %s jednostek. Funkcjonariusze jadaja jak krolowie, ale nawet oni maja swoje granice, a bez wymiany ogniw chlodzacych towar nie przetrwa kolejnego tygodnia.\n\n', 'status': 'REVIEWED_UI_CALLSITE_1014'}, {'source_class': 'com.fs.starfarer.api.impl.campaign.intel.bar.events.MercsOnTheRunBarEvent', 'english_literal': 'You prove yourself worth speaking to by partaking in a round of "Atmo Drops", a drink based largely on consuming eye-watering liquor as quickly as possible, with the mercenary band. They\'re drunk for sure, but are composed enough to speak around the precise details of why they\'re being investigated by local authorities.\n\nAfter a couple of the mercs head up to order a round of "Orbital Bombardments", their leader pulls you aside and sketches out a proposal. "We\'ve got %s suits, we fight in vac or black. I\'ll give you our contract for %s, and that\'s giving it away. Put us to work, or sell it off elsewhere, doesn\'t matter to me if you can get us outta this fix. What\'dya say?"', 'polish_ascii_draft': 'Aby zasluzyc na rozmowe z najemnikami, wypijasz z nimi kolejke "Zrzutow Atmosferycznych" - drinkow, ktore polegaja glownie na jak najszybszym pochlanianiu wyjatkowo mocnego alkoholu. Najemnicy sa pijani, ale zachowuja dosc przytomnosci, by omijac szczegoly sledztwa prowadzonego przeciw nim przez miejscowe wladze.\n\nKiedy kilku z nich idzie zamowic kolejna runde "Bombardowan Orbitalnych", dowodca bierze cie na bok i sklada propozycje. "Mamy %s kombinezonow. Walczymy w prozni i w kosmosie. Oddam ci nasz kontrakt za %s, a to i tak jak za darmo. Mozesz nas zatrudnic albo sprzedac kontrakt dalej. Bylebys wyciagnal nas z tego bagna. Co ty na to?"', 'status': 'REVIEWED_UI_CALLSITE_1014'}, {'source_class': 'com.fs.starfarer.api.impl.campaign.intel.bar.events.historian.HistorianBarEvent', 'english_literal': '"However, if you did find my information valuable, I would gladly accept... donations. Think of it as patronage to fuel my research, which in turn could produce valuable leads. Or it might help to think of it as an investment, but with no obligations incurred by either party. Consider it- you could enrich your own enterprises while contributing to the sum of human knowledge!"', 'polish_ascii_draft': '"Ale jesli moje informacje okazaly sie dla ciebie cenne, chetnie przyjme... darowizny. Potraktuj je jako mecenat wspierajacy moje badania, ktore z kolei moga doprowadzic do kolejnych wartosciowych odkryc. Albo uznaj to za inwestycje, tyle ze bez zobowiazan po zadnej ze stron. Pomysl: mozesz pomnozyc swoj majatek, a zarazem wzbogacic wiedze ludzkosci!"', 'status': 'REVIEWED_UI_CALLSITE_1014'}, {'source_class': 'com.fs.starfarer.api.impl.campaign.intel.bar.events.historian.HistorianBarEvent', 'english_literal': '"Welcome! I\'ve got something here that I think you\'ll find very interesting. Your actions over the past several cycles have caused quite a stir in certain corners, and I took it upon myself to look into your history, as it were. Here, let me transfer the synopsis."', 'polish_ascii_draft': '"Witaj! Mam cos, co moze cie bardzo zainteresowac. Twoje dokonania z ostatnich kilku cykli narobily sporo zamieszania w pewnych kregach, wiec postanowilem przyjrzec sie twojej historii. O, juz przesylam ci podsumowanie."', 'status': 'REVIEWED_UI_CALLSITE_1014'}, {'source_class': 'com.fs.starfarer.api.impl.campaign.skills.DefensiveSystems$Level3B', 'english_literal': 'Phase cloak time acceleration increased from 3× to 4×', 'polish_ascii_draft': 'Przyspieszenie czasu podczas maskowania fazowego wzrasta z 3x do 4x', 'status': 'REVIEWED_UI_CALLSITE_1014'}, {'source_class': 'com.fs.starfarer.api.impl.campaign.skills.RecoveryOperations$Level0', 'english_literal': 'The base chance to be recoverable is %d%% for disabled enemy ships, and %d%% for your ships. The base chance for weapons from disabled enemy ships to be recovered is %d%%, and %d%% for weapons from your ships. Ships that have broken apart have half the chance to be recoverable and always suffer lasting structural damage.', 'polish_ascii_draft': 'Podstawowa szansa odzyskania unieruchomionego wrogiego okretu wynosi %d%%, a wlasnego okretu %d%%. Podstawowa szansa odzyskania broni z unieruchomionych wrogich okretow wynosi %d%%, a z wlasnych okretow %d%%. Okrety, ktore rozpadly sie na czesci, maja dwukrotnie mniejsza szanse na odzyskanie i zawsze ponosza trwale uszkodzenia konstrukcji.', 'status': 'REVIEWED_UI_CALLSITE_1014'}, {'source_class': 'com.fs.starfarer.api.impl.campaign.tutorial.TutorialSustainedBurnDialogPluginImpl', 'english_literal': 'The %s ability is useful for long-distance travel. Activating it will briefly stop the fleet and reduce its acceleration to a minimum, but the maximum burn level will be much higher. A sustained burn can be interrupted by other fleets activating an interdiction pulse.', 'polish_ascii_draft': 'Zdolnosc %s przydaje sie podczas dalekich podrozy. Jej uruchomienie na chwile zatrzymuje flote i ogranicza przyspieszenie do minimum, ale znacznie zwieksza maksymalna predkosc przelotowa. Ciagly dopalacz moze zostac przerwany przez inne floty, ktore uruchomia impuls zaklocajacy.', 'status': 'REVIEWED_UI_CALLSITE_1014'}, {'source_class': 'com.fs.starfarer.api.impl.combat.dweller.ShroudedThunderheadHullmod', 'english_literal': 'The amount of damage and the flux generated depend on the size of the ship the hullmod is installed on. The probability of a bolt being fired increases with the number of hits landed over the previous %s seconds. Bolts are not triggered by weapons dealing soft flux damage, such as beams.', 'polish_ascii_draft': 'Wielkosc zadawanych obrazen i wytwarzanego strumienia zalezy od rozmiaru okretu z ta modyfikacja kadluba. Prawdopodobienstwo wystrzelenia blyskawicy rosnie wraz z liczba trafien zadanych w ciagu ostatnich %s sekund. Blyskawic nie wywoluja bronie zadajace obrazenia powodujace miekki strumien, na przyklad wiazki.', 'status': 'REVIEWED_UI_CALLSITE_1014'}, {'source_class': 'com.fs.starfarer.api.plugins.impl.CoreAutofitPlugin', 'english_literal': 'Buy weapons and fighter LPCs from market, if docked at one.\n\nOrdnance from your cargo will be preferred if that option is checked and if the alternatives are of equal quality.', 'polish_ascii_draft': 'Kupuj bron i schematy produkcyjne mysliwcow na rynku, jesli flota jest zacumowana.\n\nJesli zaznaczono odpowiednia opcje, pierwszenstwo ma uzbrojenie z ladowni, o ile dostepne zamienniki maja taka sama jakosc.', 'status': 'REVIEWED_UI_CALLSITE_1014'}, {'source_class': 'com.fs.starfarer.api.plugins.impl.CoreAutofitPlugin', 'english_literal': 'Buy weapons and fighter LPCs from the black market.\n\nNon-black-market options will be preferred if the alternatives are of equal quality.', 'polish_ascii_draft': 'Kupuj bron i schematy produkcyjne mysliwcow na czarnym rynku.\n\nGdy dostepne zamienniki maja taka sama jakosc, pierwszenstwo maja zakupy poza czarnym rynkiem.', 'status': 'REVIEWED_UI_CALLSITE_1014'}, {'source_class': 'com.fs.starfarer.api.plugins.impl.CoreAutofitPlugin', 'english_literal': 'Prioritizes installing the "Blast Doors" hullmod, which increases hull integrity and greatly reduces crew losses suffered due to hull damage.\n\n"Blast Doors" may still be added if this option isn\'t checked, provided there are enough ordnance points.', 'polish_ascii_draft': 'W pierwszej kolejnosci instaluje modyfikacje kadluba "Groddzie przeciwodlamkowe", ktora zwieksza wytrzymalosc kadluba i znacznie ogranicza straty zalogi po trafieniach.\n\n"Groddzie przeciwodlamkowe" moga zostac dodane takze bez zaznaczenia tej opcji, jesli wystarczy punktow uzbrojenia.', 'status': 'REVIEWED_UI_CALLSITE_1014'}, {'source_class': 'com.fs.starfarer.api.plugins.impl.CoreAutofitPlugin', 'english_literal': 'Prioritizes installing the "Reinforced Bulkheads" hullmod, which increases hull integrity and makes a ship virtually certain to be recoverable if lost in battle.\n\n"Reinforced Bulkheads" may still be added if this option isn\'t checked, provided there are enough ordnance points.', 'polish_ascii_draft': 'W pierwszej kolejnosci instaluje modyfikacje kadluba "Wzmocnione grodzie", ktora zwieksza wytrzymalosc kadluba i sprawia, ze okret utracony w bitwie niemal na pewno bedzie mozna odzyskac.\n\n"Wzmocnione grodzie" moga zostac dodane takze bez zaznaczenia tej opcji, jesli wystarczy punktow uzbrojenia.', 'status': 'REVIEWED_UI_CALLSITE_1014'}, {'source_class': 'com.fs.starfarer.api.plugins.impl.CoreAutofitPlugin', 'english_literal': "Remove everything possible prior to autofitting; generally results in a better fit.\n\nHowever, refitting outside of port reduces a ship's combat readiness, and this option tends to lead to more changes and more readiness lost.", 'polish_ascii_draft': 'Przed automatycznym dopasowaniem usuwa cale wyposazenie, ktore mozna zdemontowac. Zwykle pozwala to uzyskac lepsza konfiguracje.\n\nJednak przebudowa poza portem obniza gotowosc bojowa okretu. Ta opcja zwykle prowadzi do wiekszej liczby zmian i wiekszej utraty gotowosci.', 'status': 'REVIEWED_UI_CALLSITE_1014'}, {'source_class': 'com.fs.starfarer.api.plugins.impl.CoreAutofitPlugin', 'english_literal': 'Spend any unused ordnance points on flux vents, capacitors, and essential hullmods.\n\nWill not make any changes to weapon loadout, will not affect ship modules (if any), and will not spend any credits.', 'polish_ascii_draft': 'Wydaje wszystkie niewykorzystane punkty uzbrojenia na odpromienniki strumienia, kondensatory i niezbedne modyfikacje kadluba.\n\nNie zmienia uzbrojenia, nie modyfikuje modulow okretu (jesli takie posiada) i nie wydaje kredytow.', 'status': 'REVIEWED_UI_CALLSITE_1014'}, {'source_class': 'com.fs.starfarer.api.plugins.impl.CoreAutofitPlugin', 'english_literal': 'Use weapons better than the ones specified in the goal variant, if there are ordnance points left to mount them.\n\nWill add flux vents and capacitors up to the number specified in the goal variant first, then upgrade weapons, and then add more vents and some common hullmods.\n\nLeaving some unspent ordnance points in a goal variant can help take advantage of this option.', 'polish_ascii_draft': 'Montuje bron lepsza od przewidzianej w wariancie docelowym, jesli pozostana wolne punkty uzbrojenia.\n\nNajpierw dodaje odpromienniki strumienia i kondensatory do liczby okreslonej w wariancie docelowym, nastepnie ulepsza uzbrojenie, a na koniec dodaje kolejne odpromienniki i typowe modyfikacje kadluba.\n\nPozostawienie niewydanych punktow uzbrojenia w wariancie docelowym pozwala lepiej wykorzystac te opcje.', 'status': 'REVIEWED_UI_CALLSITE_1014'}]


TEST_SOURCE_UTF8 = r'''package main

import (
    "bytes"
    "encoding/binary"
    "testing"
)

func TestUnicodeSourceLiteralASCIIReplacement1014(t *testing.T) {
    en := "Phase cloak time acceleration increased from 3× to 4×"
    pl := "Przyspieszenie czasu maskowania fazowego wzrasta z 3x do 4x"
    // Minimal .class constant pool: [Utf8 (en), String #1].
    // This tests constant-pool rewriting; the trailing class bytes remain identical.
    b := []byte{0xca, 0xfe, 0xba, 0xbe, 0, 0, 0, 52, 0, 3, 1}
    length := make([]byte, 2)
    binary.BigEndian.PutUint16(length, uint16(len(en)))
    b = append(b, length...)
    b = append(b, []byte(en)...)
    b = append(b, 8, 0, 1)
    b = append(b, []byte("UNMODIFIED_TAIL")...)
    result, delta, err := patchClass(b, map[string]string{en: pl})
    if err != nil { t.Fatal(err) }
    if len(delta) != 1 || delta[0][0] != en || delta[0][1] != pl {t.Fatalf("wrong replacements: %#v",delta)}
    ent, pos, err := parseClass(result)
    if err != nil { t.Fatal(err) }
    if len(ent) != 4 || ent[2].kind != 8 || int(ent[2].ref) != 3 {t.Fatalf("invalid constant pool: %#v",ent)}
    if string(ent[3].payload) != pl { t.Fatalf("bad replacement payload: %q",ent[3].payload) }
    if !bytes.Equal(result[pos:], []byte("UNMODIFIED_TAIL")) {t.Fatal("class body was modified")}
}
'''

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('worktree',type=Path)
    root=ap.parse_args().worktree
    base=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1013.csv'
    target=base.with_name('TLUMACZENIA_JAR_1014.csv')
    with base.open(newline='',encoding='utf-8') as f:
        previous=list(csv.DictReader(f))
    assert len(previous)==5057,len(previous)
    existing={(r['source_class'],r['english_literal']) for r in previous}
    assert len(ADDITIONS)==17,len(ADDITIONS)
    for row in ADDITIONS:
        assert (row['source_class'],row['english_literal']) not in existing
        assert row['polish_ascii_draft'].isascii()
    with target.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f, fieldnames=['source_class','english_literal','polish_ascii_draft','status'],lineterminator='\r\n')
        writer.writeheader();writer.writerows(previous+ADDITIONS)
    go=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go'
    data=go.read_text()
    for old,new in [('const version = "1013"','const version = "1014"'),('const exeVersion = "1.0.13"','const exeVersion = "1.0.14"'),('"1010", version}','"1010", "1013", version}')]:
        assert data.count(old)==1,old
        data=data.replace(old,new)
    # Source literals in the original JVM pool can legitimately contain UTF-8
    # (for instance the multiplication sign U+00D7). Only replacements must be ASCII.
    assert data.count('\t"time"\n')==1
    data=data.replace('\t"time"\n','\t"time"\n\t"unicode/utf8"\n')
    assert data.count('if !isASCII(en) || !isASCII(pl) {')==1
    data=data.replace('if !isASCII(en) || !isASCII(pl) {','if !utf8.ValidString(en) || !isASCII(pl) {')
    before='\t\toriginal := ent[idx].payload\n\t\tif !isASCII(string(original)) {\n\t\t\tcontinue\n\t\t}\n\t\ten := string(original)'
    after='\t\toriginal := ent[idx].payload\n\t\ten := string(original)\n\t\t// Source text may use non-ASCII UTF-8, while replacements stay ASCII.\n\t\t// Avoid matching malformed sequences (e.g. modified UTF-8 null).\n\t\tif !utf8.ValidString(en) {\n\t\t\tcontinue\n\t\t}'
    assert data.count(before)==1
    data=data.replace(before,after)
    go.write_text(data)
    # The synthetic class fixture tests non-ASCII source literals without distributing game assets.
    (go.parent/'source_utf8_1014_test.go').write_text(TEST_SOURCE_UTF8,encoding='utf-8')
    inst=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
    data=inst.read_text()
    assert data.count('const edition = "1.0.13"')==1
    inst.write_text(data.replace('const edition = "1.0.13"','const edition = "1.0.14"'))
    meta=root/'mod/mod_info.json'
    info=json.loads(meta.read_text())
    assert info['version']=='1.0.13'
    info['version']='1.0.14'
    info['description']=info['description'].replace('1.0.13','1.0.14')
    meta.write_text(json.dumps(info,ensure_ascii=True,indent=2)+'\n')
    guide=root/'mod/CZYTAJ.txt';data=guide.read_text()
    assert data.count('1.0.13')==1
    data=data.replace('1.0.13','1.0.14')
    data += '\nDodano 17 tlumaczen opisow opcji automatycznego wyposazenia, dialogow i umiejetnosci.\n'
    guide.write_text(data)
    print('1.0.14: 17 API UI literal translations, total API map rows:',len(previous+ADDITIONS))
if __name__ == '__main__':main()