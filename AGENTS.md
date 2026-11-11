# Starsector PL: instrukcje dla kolejnego agenta

**Aktualny stan roboczy: 1.0.26** (snapshot 1.0.12 + overlaye 1013–1026; OBF mapa 10126: 3380 podmian; API mapa 1026: 5150 wierszy, 5148 podmian identycznych z 1025).

**Cel 1.1:** pelna polonizacja wszystkich wyswietlanych pol gry Starsector 0.98a-RC8. Wersje 1.0.x NIE oznaczaja ukonczonego tlumaczenia.

- Tlumacz wszystkie widoczne teksty z data/, OBF i API, w tym dialogi, menu, opisy, raporty, nazwy generowane i dynamiczne wiadomosci.
- Tlumacz nazwy z powszechnym polskim odpowiednikiem, pseudonimy/nicki i skroty z przetlumaczonym rozwinieciem (combat readiness CR -> gotowosc bojowa GB). **Nie tlumacz imion i nazwisk osob.**
- W zasobach gry polski ASCII bez diakrytykow (ograniczenia fontow); tekst dokumentacji moze byc z polskimi znakami.
- Nigdy nie zmieniaj ID, warunkow, skryptow, parametrow, technicznych odniesien ani bajtkodu metod. Waliduj wylacznie zmieniane pola. Wyjatki wymagaja dowodu i opisu.
- Krytyczne: w `data/campaign/rules.csv` option musi miec forme `ID:tekst` lub `number:ID:tekst`. Dodatkowy dwukropek wewnatrz tekstu powoduje NumberFormatException przy starcie. Uruchamiaj maintenance/check_rules_options.py przed wydaniem.
- Zachowuj wszystkie znaczniki $..., %..., kroki parsera, format CSV, kodowanie i zakonczenia linii CRLF.
- Po zmianach porownuj cala strukture z oryginalami i kazdy zmieniony .class (dopuszczalne tylko literały i manifest JAR), testuj na oryginalnych JAR: instalacje, aktualizacje, idempotencje, przywracanie i odmowe na uszkodzonych plikach.
- Natywne testy Windows i gry sa oddzielne; format PE i testy Go na Linuxie nie zastepuja uruchomienia gry.
- Paczka dla gracza minimalna: 870 plikow data, mod_info.json, krotka instrukcja i jeden EXE ze zintegrowanymi patcherami. Zrodla i raporty poza paczka.
- Oryginalne JAR sa materialami komercyjnymi gry i nie sa w tym repo. **Nie dodawaj do publicznego GitHub oryginalnych bibliotek ani pelnych logow ze sciezkami uzytkownika.**
- Nie udawaj PASS ani 100% ukonczenia. Pracuj konkretnie, raportuj krotko. Nie tworz kolejnych wersji bez zmian i testow.
- Audyt 1018 wykryl **aktywnie widoczne angielskie zaimki** w dynamicznych dialogach API (`BaseBarEventWithPerson` i `PlanetaryShieldBarEvent`) oraz `Misc.STORY` w dwoch tooltipach OBF. Zob. `docs/DYNAMIC_FRAGMENT_AUDIT_1018.md`, issue #4; nie naprawiaj globalna podmiana `her` bez analizy przypadkow gramatycznych. W 1.0.18 przetlumaczono tylko podmiotowe `he/she`; pozostale zaimki wymagaja odmiany. Ostatnia zbudowana wersja to 1.0.21, nie jest to 1.1.

## Start pracy w nowym czacie
1. Czytaj README, docs/STATUS.md i docs/TEST_109_CRASH.md.
2. Uruchom `python3 tools/restore_snapshot.py` (wymagany zstd), nastepnie `python3 tools/apply_1013.py worktree` i `python3 tools/apply_1014.py worktree` oraz `python3 tools/apply_1015.py worktree` i `python3 tools/apply_1016.py worktree` oraz `python3 tools/apply_1017.py worktree` i `python3 tools/apply_1018.py worktree` oraz `python3 tools/apply_1019.py worktree` i `python3 tools/apply_1020.py worktree` oraz `python3 tools/apply_1021.py worktree` i `python3 tools/apply_1022.py worktree` oraz `python3 tools/apply_1023.py worktree` i `python3 tools/apply_1024.py worktree`. Powstanie biezacy `worktree/` z mapami CSV (w tym API 1021, OBF 10121 i wszystkie historyczne), narzedziami Go, kodem patcherow i mod/data.
3. Waliduj `worktree/mod/data/campaign/rules.csv`.
4. Zdobywaj oryginalne JAR z prywatnej Biblioteki uzytkownika i weryfikuj ich SHA; nie zakladaj ze sa w GitHub.
5. Kontynuuj audyt wszystkich pozostalych pol do wersji 1.1.

6. Przy zmianach dynamicznych skladanych z kilku literałów wykonuj test *calego zdania*: stary problem `C` + `onsumes` dawal `Czuzywa`; poprawiono w 1.0.19. `Misc.STORY` 81 wywolan w 24 klasach, 219 wywolan metod zaimkowych w 42 klasach (zliczono takze `InterfaceMethod`). Szczegoly `docs/RELEASE_1019.md`; nie zmieniaj globalnie `her` ani `story`.

7. Audyt pojedynczych literałów wykonuj na **oryginalnej JVM constant pool** (`tools/audit_exact_literals_1020.py`), nie na escaped tekstowych wynikach `javap`. Dwa wiersze API nie znajduja klas w bibliotece API (jeden jest juz pokryty w OBF); nie przedstawiaj ich jako dwa brakujace teksty w grze. Reprodukcja: `docs/RELEASE_1020.md`.

8. Audyt oryginalne `data.rar` kontra 870 podmienianych plikow: `tools/verify_source_fields_1021.py`. W 833 ustrukturyzowanych plikach rozne sa tylko wartosci literalow, w 18 CSV tylko dozwolone tekstowe kolumny (5 skryptow `SetTextHighlights`), 19 TXT wymagaja osobnego recznego audytu. Raport w Bibliotece `Starsector_PL_1021_DATA_FIELD_AUDIT.json`, wyniki w `docs/RELEASE_1021.md`. Nie myl tego z semantycznym audytem kazdego napisu. OBF 3144 zamian / 533 klasy, API 5106 / 936 klas, bez zmian bajtkodu poza referencjami do podmienionych tekstow.

9. W 1.0.22 skorygowano 65 wystapien nazwy frakcji do `Liga Perseanska` / `Ligi Perseanskiej` / `Lige Perseanska`, w 3 user-facing plikach data. `tools/verify_1022_names.py` kontroluje hash 867 nietknietych plikow i 3 docelowych; `tools/test_1022_names.py` chroni przed zastapieniem fragmentu `Ligi Persea` wewnatrz poprawnej juz `Ligi Perseanskiej`. Nie zmieniono map JAR, technicznych ID ani skryptow. Testy pelnej 1.1 i Windows wciaz otwarte; `docs/RELEASE_1022.md`.

10. W 1.0.23 dodano 67 UI literals (41 OBF, 26 API) w tooltipach uzbrojenia, tabelach rynku, kodeksie, symulatorze i gotowosci bojowej. Nie patchuj enum ID `HIGH/LOW/EXTREME` itp. W `ToggleAbilityWithCost` oryginalne `educes the combat readiness ` z trailing space jest ODREBNYM literalem od wersji bez spacji; polski wynik musi poprawnie skladac zdanie. Test `tools/verify_1023_ui.py`, dowody `docs/RELEASE_1023.md`. Patch OBF SHA `f391bc4f0a0c6078845f02415b80378a9d45375ab37eb6c287fcac4058b46abb`, API SHA `562877340d26fecabb5c34f38b9fbe11ed8d2c781faa78b307c7150bc018cb10`. Natywnej gry Windows i pelnej 1.1 NIE zweryfikowano.

11. **Krytyczne odkrycie 1.0.24:** w 1.0.23 wiele głownych przyciskow menu bylo po angielsku, mimo przetlumaczonych `New Game`/`Load Game`. W klasie OBF `com.fs.starfarer.title.C` potwierdzono 8 pozostalych stringow budujacych przyciski. W 1.0.24 sa po polsku, wraz z filtrami wyboru broni i eskadr, launcherem i zadaniami flot: **44 nowe etykiety** (OBF 28/API 16). Zachowano enum ID (`FOLLOW`, `HOLD`, etc.) i potencjalnie techniczny wybor `Off` launchera. Gotowe testy: `tools/verify_1024_ui.py`, `tools/test_1024_delta.py` i prywatny audyt `tools/verify_1024_callsites.py`; raport `docs/RELEASE_1024.md`. Oryginalne JAR bez zmian po restore, Windows/gameplay nieuruchomione. Audyt pelnego 1.1 nadal otwarty.

12. **1.0.25:** OBF +81 krotkich UI etykiet w 12 klasach, m.in. przegladarki schematow, koszty produkcji, wybor oficerow, dziennik misji. `ShipLoss` składa w 3 wariantach `utrata 17% GB`, `skrzydlo Osa - utrata 17% GB`, `okret Jastrzab - utrata 17% GB` bez błędów odmiany. API ma mapę 1025 identyczna z 1024; nowy patcher akceptuje hash OBF `dc1fecf61d12d8819bab11b3d1bf20c4aecc294ac27ebce747e08b0dd35ae033`. Weryfikacja 81 JVM literałów w 100 miejscach ldc, 12 klas, 1018 zrodel odtwarzalnych, realny upgrade 1.0.24->1.0.25 PASS. Audyt 3659 DRAFT/OPTIONAL: zadnych strat spacji/znacznikow, dwa prawidlowe przecinki Oxford przed `i`. To nie jest pełna recenzja znaczenia; issue #3 dalej otwarte. Szczegoly `docs/RELEASE_1025.md`.

13. **1.0.26:** 86 nowych etykiet OBF w 20 klasach, m.in. przyciski refitu, badanie planet, wybieranie celow najazdow, budynki i rynek, oficerowie, odzyskiwanie i zakladki. Potwierdzono 106 uzyc JVM `ldc`; 11 etykiet ma posrednie przekazanie do UI przez zmienne (nie oceniaj ich wylacznie oknem 10 instrukcji). API 1026 to kopia mapy 1025; nowy patcher akceptuje OBF SHA `a475ef535590b79da74d425f9e3f7566c85bed163e4a3795e88a593b7f69f42a`. Fresh, real upgrade z 1.0.25, restore, invalid JAR odmowa, Go i 1021 plikow zrodel odtwarzalnych: PASS. `docs/RELEASE_1026.md`. Nie deklarowac pelnego 1.1 ani native Windows runtime testow.
