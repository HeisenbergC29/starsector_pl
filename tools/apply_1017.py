#!/usr/bin/env python3
"""Apply verified 1.0.17 translations on a 1.0.16 worktree.
Only modifies translation maps, patcher version/update configuration, and mod metadata.
Requires sequential 1.0.12 base and overlays 1013, 1014, 1015, 1016.
No commercial binary or original game files are bundled.
"""
import csv,json,re
from pathlib import Path

OBF = [{'source_class': 'com.fs.starfarer.tutorial.oOOO.G',
  'english_literal': 'Welcome to the fleet command tutorial.\n'
                     '\n'
                     'At the start of a battle, you will want to deploy some of your ships. To do so, click on ship '
                     'icons to mark them for deployment and then press the "Deploy" button.\n'
                     '\n'
                     'Deploying ships requires fleet points. Right now, you only have a few points, so go ahead and '
                     '<highlight>deploy just the Wasp interceptor wing after dismissing this dialog.</highlight>',
  'polish_ascii_draft': 'Witaj w samouczku dowodzenia flota.\n'
                        '\n'
                        'Na poczatku bitwy wybierasz okrety, ktore chcesz wystawic. Kliknij ikony jednostek, aby '
                        'zaznaczyc je do wystawienia, a nastepnie nacisnij przycisk "Wystaw".\n'
                        '\n'
                        'Wystawianie jednostek wymaga punktow floty. Na razie masz ich niewiele, wiec <highlight>po '
                        'zamknieciu tego okna wystaw tylko skrzydlo mysliwcow Wasp.</highlight>',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1017'},
 {'source_class': 'com.fs.starfarer.tutorial.oOOO.F',
  'english_literal': 'You can press %s to open and close the map, and %s to pause and unpause. To pan your view, '
                     'right-click on an empty spot on the map and drag.\n'
                     '\n'
                     'You can also see what your ships are doing by clicking on them and then selecting "Show Video '
                     'Feed" from the context menu.\n'
                     '\n'
                     '<highlight>With the map open, select your interceptor wing and click "Show Video Feed" to follow '
                     'along as it captures the Comm Relay.</highlight>',
  'polish_ascii_draft': 'Nacisnij %s, aby otworzyc lub zamknac mape, a %s, aby wlaczyc lub wylaczyc pauze. Aby '
                        'przesunac widok, kliknij prawym przyciskiem myszy puste miejsce na mapie i przeciagnij.\n'
                        '\n'
                        'Mozesz tez sledzic dzialania okretow: kliknij wybrany okret i wybierz z menu "Pokaz obraz '
                        'wideo".\n'
                        '\n'
                        '<highlight>Na otwartej mapie wybierz skrzydlo mysliwcow przechwytujacych i kliknij "Pokaz '
                        'obraz wideo", aby obserwowac przejmowanie przekaznika lacznosci.</highlight>',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1017'},
 {'source_class': 'com.fs.starfarer.tutorial.oOOO.F',
  'english_literal': "Good! You'll need additional fleet points to deploy the rest of your fleet, and you can get them "
                     'by capturing objectives.\n'
                     '\n'
                     "<highlight>There's a Comm Relay nearby - these give more fleet points than other objectives. "
                     'Order its capture by clicking on the objective and then selecting "Capture" from the context '
                     'menu.</highlight>\n'
                     '\n'
                     "Creating an assignment costs a command point, and you can't give any more orders once command "
                     'points run out.',
  'polish_ascii_draft': 'Dobrze! Aby wystawic reszte floty, potrzebujesz dodatkowych punktow floty. Mozesz je zdobyc, '
                        'przejmujac cele na polu bitwy.\n'
                        '\n'
                        '<highlight>W poblizu znajduje sie przekaznik lacznosci, ktory zapewnia wiecej punktow floty '
                        'niz inne cele. Kliknij go, a nastepnie wybierz "Przejmij" z menu kontekstowego.</highlight>\n'
                        '\n'
                        'Wydanie rozkazu zuzywa punkt dowodzenia. Gdy skoncza ci sie punkty dowodzenia, nie wydasz '
                        'kolejnych rozkazow.',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1017'},
 {'source_class': 'com.fs.starfarer.tutorial.oOOO.O0OO',
  'english_literal': "Now that you've got more ships on the field, let's go take another objective. <highlight>There's "
                     'a Sensor Array nearby - switch back to the map by pressing %s and order its capture. Remember to '
                     'unpause the game afterwards by pressing %s, as switching to the map automatically pauses '
                     'it.</highlight>\n'
                     '\n'
                     "Note that as Fleet Commander, you're giving the assignment to your whole fleet and not to a "
                     'specific ship. Your subordinates will work out the details of which ships get which assignments.',
  'polish_ascii_draft': 'Teraz, gdy masz wiecej jednostek na polu bitwy, przejmijmy kolejny cel. <highlight>W poblizu '
                        'znajduje sie siec czujnikow. Wroc do mapy, naciskajac %s, i wydaj rozkaz jej przejecia. '
                        'Pamietaj, aby potem wznowic gre klawiszem %s, poniewaz otwarcie mapy automatycznie wlacza '
                        'pauze.</highlight>\n'
                        '\n'
                        'Jako dowodca floty przydzielasz zadanie calej flocie, a nie jednemu okretowi. Twoi podwladni '
                        'sami zdecyduja, ktore jednostki je wykonaja.',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1017'},
 {'source_class': 'com.fs.starfarer.tutorial.oOOO.o0OO',
  'english_literal': "Well done! Now you've got more fleet points to play with (and an extra couple of command points "
                     "from that Comm Relay, too), and it's time to deploy the rest of your fleet.\n"
                     '\n'
                     '<highlight>Go back to the map by pressing %s and click the "Reinforcements" button in the upper '
                     'right corner of the screen, then deploy all of the remaining ships.</highlight>',
  'polish_ascii_draft': 'Doskonale! Masz teraz wiecej punktow floty, a dzieki przekaznikowi lacznosci otrzymales tez '
                        'kilka dodatkowych punktow dowodzenia. Czas wystawic reszte floty.\n'
                        '\n'
                        '<highlight>Wroc do mapy klawiszem %s, nacisnij przycisk "Posilki" w prawym gornym rogu '
                        'ekranu, a nastepnie wystaw wszystkie pozostale jednostki.</highlight>',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1017'},
 {'source_class': 'com.fs.starfarer.tutorial.oOOO.o0OO',
  'english_literal': 'Your flagship will enter the battlefield shortly. You can pilot it directly when the map is '
                     'closed and give orders to other ships in your fleet when the map is open (remember, press %s to '
                     'toggle the map).\n'
                     '\n'
                     "You can also toggle the autopilot by pressing %s. It's useful when you want your flagship to "
                     "fight while you're looking at the map, but do not want to pause the game.\n"
                     '\n'
                     '<highlight>Now, turn off the map and fly around for a bit. Remember to press %s to unpause, if '
                     'needed.</highlight>',
  'polish_ascii_draft': 'Twoj okret flagowy wkrotce wejdzie do bitwy. Gdy mapa jest zamknieta, mozesz sam nim '
                        'pilotowac, a po otwarciu mapy wydawac rozkazy innym jednostkom floty (pamietaj, ze klawisz %s '
                        'przelacza widok mapy).\n'
                        '\n'
                        'Autopilota mozesz wlaczyc lub wylaczyc klawiszem %s. To przydatne, gdy chcesz, aby okret '
                        'flagowy walczyl podczas przegladania mapy, ale nie chcesz zatrzymywac gry.\n'
                        '\n'
                        '<highlight>Teraz zamknij mape i przez chwile popilotuj okret. Jesli trzeba, wznow gre '
                        'klawiszem %s.</highlight>',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1017'},
 {'source_class': 'com.fs.starfarer.tutorial.oOOO.C',
  'english_literal': "Let's set up to give it a warm welcome. First, organize a strike force midway up the map - a "
                     'couple of grid squares to the left of the Sensor Array we just captured is good.\n'
                     '\n'
                     '<highlight>Left click on the desired spot to create a waypoint, and then select "Rally Strike '
                     'Force" from the context menu.</highlight> The Dagger torpedo bombers, being the only strike '
                     'craft in your fleet, will go there.',
  'polish_ascii_draft': 'Przygotujmy przeciwnikowi gorace powitanie. Najpierw zbierz grupe uderzeniowa mniej wiecej w '
                        'polowie mapy, kilka pol na lewo od przejetej przed chwila sieci czujnikow.\n'
                        '\n'
                        '<highlight>Kliknij lewym przyciskiem myszy wybrane miejsce, aby utworzyc punkt zborny, i '
                        'wybierz z menu "Zbiorka grupy uderzeniowej".</highlight> Bombowce torpedowe Dagger, jako '
                        'jedyne jednostki uderzeniowe twojej floty, skieruja sie w to miejsce.',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1017'},
 {'source_class': 'com.fs.starfarer.tutorial.oOOO.C',
  'english_literal': 'Good, the bombers are on their way.\n'
                     '\n'
                     'In the meantime, the interceptors have decided to attack the cruiser on their own, and the '
                     "Gemini is moving up to do so as well. We don't want that - the Gemini is a freighter/carrier, "
                     'and no match for a cruiser in direct combat, and neither are the interceptors.\n'
                     '\n'
                     '<highlight>Left click behind your lines to make another waypoint, and select "Rally Carrier '
                     'Group" to keep the Gemini there and out of trouble.</highlight>',
  'polish_ascii_draft': 'Dobrze, bombowce sa juz w drodze.\n'
                        '\n'
                        'Tymczasem mysliwce przechwytujace same ruszyly na krazownik, a Gemini takze sie do niego '
                        'zbliza. Nie chcemy tego: Gemini jest transportowcem i lotniskowcem, ktory w bezposrednim '
                        'starciu nie ma szans z krazownikiem. Podobnie jest z mysliwcami przechwytujacymi.\n'
                        '\n'
                        '<highlight>Kliknij lewym przyciskiem myszy za swoimi liniami, aby utworzyc kolejny punkt '
                        'zborny, i wybierz "Zbiorka grupy lotniskowcow", aby Gemini pozostal tam i uniknal '
                        'niebezpieczenstwa.</highlight>',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1017'},
 {'source_class': 'com.fs.starfarer.tutorial.oOOO.C',
  'english_literal': "But what about the interceptors? They're not much use against a cruiser, so let's just get them "
                     'off the battlefield.\n'
                     '\n'
                     '<highlight>Click on the interceptors and select "Retreat", under "Direct Orders".</highlight>\n'
                     '\n'
                     'This costs a command point, and the order can be rescinded ("Rescind Orders" in the context '
                     'menu).',
  'polish_ascii_draft': 'A co z mysliwcami przechwytujacymi? Niewiele zdzialaja przeciwko krazownikowi, wiec wycofajmy '
                        'je z pola bitwy.\n'
                        '\n'
                        '<highlight>Kliknij skrzydlo mysliwcow przechwytujacych i wybierz "Odwrot" w sekcji "Rozkazy '
                        'bezposrednie".</highlight>\n'
                        '\n'
                        'Ten rozkaz kosztuje punkt dowodzenia. Mozesz go tez anulowac, wybierajac "Odwolaj rozkazy" w '
                        'menu kontekstowym.',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1017'},
 {'source_class': 'com.fs.starfarer.tutorial.oOOO.B',
  'english_literal': "Excellent, your forces are in position! Now, let's order a strike on the unsuspecting enemy "
                     'cruiser. <highlight>Click on it and select "Strike" from the context menu.</highlight>\n'
                     '\n'
                     'After that\'s done, you can either watch the bombers carry out their strike ("Show Video Feed" '
                     'from their context menu) or get into the battle yourself.\n'
                     '\n'
                     'Either way, make sure the enemy cruiser is destroyed.',
  'polish_ascii_draft': 'Swietnie! Twoje sily zajely pozycje. Teraz wydajmy rozkaz ataku na niczego niespodziewajacy '
                        'sie wrogi krazownik. <highlight>Kliknij krazownik i wybierz "Uderzenie" z menu '
                        'kontekstowego.</highlight>\n'
                        '\n'
                        'Gdy wydasz rozkaz, mozesz obserwowac atak bombowcow (wybierz "Pokaz obraz wideo" z ich menu) '
                        'albo sam wlaczyc sie do walki.\n'
                        '\n'
                        'Tak czy inaczej, dopilnuj, aby wrogi krazownik zostal zniszczony.',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1017'},
 {'source_class': 'com.fs.starfarer.tutorial.oOOO.oOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO',
  'english_literal': "We're almost done.\n"
                     '\n'
                     'You can transfer your command to another ship during the battle. This is particularly useful if '
                     'your flagship is disabled, or if you just want to start the battle in a faster ship, but then '
                     'switch over to a heavier one in the later stages.\n'
                     '\n'
                     "To try it, let's transfer command to the Gemini. <highlight>Click on the Gemini and select "
                     '"Transfer Command" from the context menu.</highlight>',
  'polish_ascii_draft': 'To juz prawie koniec.\n'
                        '\n'
                        'Podczas bitwy mozesz przekazac dowodzenie na inny okret. Jest to szczegolnie przydatne, gdy '
                        'okret flagowy zostal unieruchomiony, albo gdy chcesz zaczac walke szybsza jednostka, a '
                        'pozniej przesiasc sie na ciezszy okret.\n'
                        '\n'
                        'Sprobujmy przekazac dowodzenie na Gemini. <highlight>Kliknij Gemini i wybierz "Przekaz '
                        'dowodzenie" z menu kontekstowego.</highlight>',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1017'},
 {'source_class': 'com.fs.starfarer.tutorial.oOOO.oOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO',
  'english_literal': "Congratulations, you've completed the Starfarer fleet command tutorial!\n"
                     '\n'
                     '<highlight>Press Escape to go back to the main menu</highlight>, and use your newfound skills in '
                     'some missions.',
  'polish_ascii_draft': 'Gratulacje! Samouczek dowodzenia flota Starfarera zostal ukonczony!\n'
                        '\n'
                        '<highlight>Nacisnij Escape, aby wrocic do menu glownego</highlight>, i wykorzystaj nowo '
                        'zdobyte umiejetnosci w kolejnych misjach.',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1017'},
 {'source_class': 'com.fs.starfarer.coreui.refit.wgd2.WeaponGroupDialogV2',
  'english_literal': 'Flux per second generated by the sustained firing of this group. Some weapons are capable of '
                     'higher burst fire - due to ammo, charges, and similar mechanics; this value does not reflect the '
                     'resultant higher initial flux generation.',
  'polish_ascii_draft': 'Strumien na sekunde wytwarzany podczas ciaglego ostrzalu z tej grupy uzbrojenia. Niektore '
                        'bronie moga przez krotki czas strzelac intensywniej, np. dzieki amunicji lub ladunkom. '
                        'Wyswietlona wartosc nie uwzglednia wiekszego poczatkowego przyrostu strumienia.',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1017'},
 {'source_class': 'com.fs.starfarer.coreui.refit.ModPickerDialogV3$1',
  'english_literal': 'A hullmod that has requirements that must be met to be removed; the requirements are met.',
  'polish_ascii_draft': 'Modyfikacja kadluba, ktorej usuniecie wymaga spelnienia okreslonych warunkow. Wszystkie '
                        'warunki zostaly spelnione.',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1017'},
 {'source_class': 'com.fs.starfarer.coreui.refit.ModPickerDialogV3$1',
  'english_literal': 'A hullmod that has requirements that must be met to be removed; the requirements are not met.',
  'polish_ascii_draft': 'Modyfikacja kadluba, ktorej usuniecie wymaga spelnienia okreslonych warunkow. Nie wszystkie '
                        'warunki sa spelnione.',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1017'}]
API = [{'source_class': 'com.fs.starfarer.api.impl.campaign.missions.SwordOfEventide',
  'english_literal': 'Princess of Persea',
  'polish_ascii_draft': 'Ksiezniczka Persei',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1017'},
 {'source_class': 'com.fs.starfarer.api.impl.campaign.intel.events.LuddicChurchHostileActivityFactor',
  'english_literal': 'Knights of Ludd ',
  'polish_ascii_draft': 'Rycerze Ludda ',
  'status': 'VERIFIED_JAVAP_UI_CALLSITE_1017'}]
CORRECTIONS = [('com.fs.starfarer.api.impl.campaign.population.CoreImmigrationPluginImpl',
  'Larger non-hostile colony in same system',
  'Wieksza nieprzyjazna kolonia w tym samym ukladzie',
  'Wieksza niewroga kolonia w tym samym ukladzie')]


def replace_exact(s,old,new):
  assert s.count(old)==1,(old[:80],s.count(old))
  return s.replace(old,new)

def add_rows(source,target,rows,expected_count,fixes=()):
  with source.open(newline='',encoding='utf-8') as stream:
    items=list(csv.DictReader(stream))
  assert len(items)==expected_count,(source,len(items),expected_count)
  for cl,eng,previous,corrected in fixes:
    matching=[r for r in items if r['source_class']==cl and r['english_literal']==eng]
    assert len(matching)==1 and matching[0]['polish_ascii_draft']==previous,(cl,eng,matching)
    matching[0]['polish_ascii_draft']=corrected
    matching[0]['status']='CORRECTED_SEMANTIC_1017'
  keys={(r['source_class'],r['english_literal']) for r in items}
  for r in rows:
    assert (r['source_class'],r['english_literal']) not in keys,r
    assert r['polish_ascii_draft'].isascii(),r
    assert r['english_literal'].count('\n')==r['polish_ascii_draft'].count('\n'),r
  with target.open('w',newline='',encoding='utf-8') as stream:
    writer=csv.DictWriter(stream,fieldnames=['source_class','english_literal','polish_ascii_draft','status'],lineterminator='\r\n')
    writer.writeheader();writer.writerows(items+rows)
  return len(items)+len(rows)

def main(worktree):
  obfdir=worktree/'buildtools/NARZEDZIA_OBF'
  apidir=worktree/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
  num_obf=add_rows(obfdir/'TLUMACZENIA_OBF_10116.csv',obfdir/'TLUMACZENIA_OBF_10117.csv',OBF,3125)
  num_api=add_rows(apidir/'translations/TLUMACZENIA_JAR_1016.csv',apidir/'translations/TLUMACZENIA_JAR_1017.csv',API,5094,CORRECTIONS)
  path=obfdir/'main.go';s=path.read_text('utf-8')
  s=replace_exact(s,'TLUMACZENIA_OBF_10115.csv TLUMACZENIA_OBF_10116.csv','TLUMACZENIA_OBF_10115.csv TLUMACZENIA_OBF_10116.csv TLUMACZENIA_OBF_10117.csv')
  s=replace_exact(s,'const currentPatchState = "patched 10116"','const currentPatchState = "patched 10117"')
  s=replace_exact(s,'table, e := loadTranslations("TLUMACZENIA_OBF_10116.csv")','table, e := loadTranslations("TLUMACZENIA_OBF_10117.csv")')
  # Prior 1.0.16 patched OBF version must be recognized for safe upgrade.
  s=replace_exact(s,'var knownPreviousOBFHashes = map[string]string{', 'var knownPreviousOBFHashes = map[string]string{\n\t"c3dcae2341f5fa96cb92b6a1cb1a59ec5f32cdf4579f77fe5ad30985764ee78c": "10116",')
  s=replace_exact(s,'if state == currentPatchState || state == "patched 10115"', 'if state == currentPatchState || state == "patched 10116" || state == "patched 10115"')
  s=replace_exact(s,'| OBF 1.0.16 | stan:', '| OBF 1.0.17 | stan:')
  s=replace_exact(s,'1.0.16: Lokalizacja tekstow OBF','1.0.17: Lokalizacja tekstow OBF')
  s=replace_exact(s,'PL ASCII OBF 0.9.99-1.0.16','PL ASCII OBF 0.9.99-1.0.17')
  path.write_text(s,encoding='utf-8')
  path=obfdir/'main_test.go';s=path.read_text(encoding='utf-8')
  s=replace_exact(s,'if !alreadyThisRelease("patched 10116") {','if !alreadyThisRelease("patched 10117") {')
  s=replace_exact(s,'[]string{"original", "patched 10115",','[]string{"original", "patched 10116", "patched 10115",')
  path.write_text(s,encoding='utf-8')
  path=obfdir/'mapping_10116_test.go';s=path.read_text(encoding='utf-8')
  s=replace_exact(s,'if !alreadyThisRelease("patched 10116") {t.Fatal("new not current")}', 'if alreadyThisRelease("patched 10116") {t.Fatal("previous release incorrectly treated as current")}' )
  path.write_text(s,encoding='utf-8')
  (obfdir/'mapping_10117_test.go').write_text("""package main
import "testing"
func TestOBF10117UpgradeAndUIMap(t *testing.T) {
  m,err:=loadTranslations("TLUMACZENIA_OBF_10117.csv")
  if err!=nil {t.Fatal(err)}
  if len(m)!=532 {t.Fatalf("Unexpected class count %d",len(m))}
  if knownPreviousOBFHashes["c3dcae2341f5fa96cb92b6a1cb1a59ec5f32cdf4579f77fe5ad30985764ee78c"]!="10116" {t.Fatal("missing prior 1.0.16 OBF hash")}
  if !alreadyThisRelease("patched 10117") || alreadyThisRelease("patched 10116") {t.Fatal("version recognition broken")}
}
""",encoding='utf-8')
  path=apidir/'main.go';s=path.read_text('utf-8')
  s=replace_exact(s,'const version = "1016"','const version = "1017"')
  s=replace_exact(s,'const exeVersion = "1.0.16"','const exeVersion = "1.0.17"')
  s=replace_exact(s,'"1013", "1014", "1015", version}', '"1013", "1014", "1015", "1016", version}')
  s=replace_exact(s,'const expectedOBFPatched10116 = "c3dcae2341f5fa96cb92b6a1cb1a59ec5f32cdf4579f77fe5ad30985764ee78c"',
    'const expectedOBFPatched10116 = "c3dcae2341f5fa96cb92b6a1cb1a59ec5f32cdf4579f77fe5ad30985764ee78c"\nconst expectedOBFPatched10117 = "31307f67a97dabb9687569c2f65a57c1b39c6aeec1eb1b8e8eb22099189ea93e"')
  s=replace_exact(s,'if hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10116',
      'if hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10117 && hash(obf) != expectedOBFPatched10116')
  s=replace_exact(s,'PL ASCII patch up to 1.0.16','PL ASCII patch up to 1.0.17')
  path.write_text(s,encoding='utf-8')
  path=worktree/'buildtools/NARZEDZIA_INSTALATOR/main.go';s=path.read_text('utf-8')
  s=replace_exact(s,'const edition = "1.0.16"','const edition = "1.0.17"')
  path.write_text(s,encoding='utf-8')
  path=worktree/'mod/mod_info.json';meta=json.loads(path.read_text('utf-8'))
  assert meta['version']=='1.0.16'
  meta['version']='1.0.17';meta['description']=meta['description'].replace('1.0.16','1.0.17')
  path.write_text(json.dumps(meta,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')
  path=worktree/'mod/CZYTAJ.txt';s=path.read_text('utf-8')
  s=replace_exact(s,'STARSECTOR PL ASCII 1.0.16','STARSECTOR PL ASCII 1.0.17')
  s+='\nPrzetlumaczono komunikaty samouczka dowodzenia flota oraz kolejne opisy i nazwy.\n'
  path.write_text(s,encoding='utf-8')
  print('Applied 1.0.17 overlay:',num_obf,'OBF rows;',num_api,'API rows, including',len(CORRECTIONS),'semantic correction')

if __name__=='__main__':
  import argparse
  ap=argparse.ArgumentParser();ap.add_argument('worktree',type=Path)
  main(ap.parse_args().worktree)