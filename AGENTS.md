# Starsector PL: instrukcje dla kolejnego agenta

**Aktualny stan roboczy: 1.0.21** (snapshot 1.0.12 + kolejne overlaye 1013–1021; OBF mapa 10121, API mapa 1021).

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
2. Uruchom `python3 tools/restore_snapshot.py` (wymagany zstd), nastepnie `python3 tools/apply_1013.py worktree` i `python3 tools/apply_1014.py worktree` oraz `python3 tools/apply_1015.py worktree` i `python3 tools/apply_1016.py worktree` oraz `python3 tools/apply_1017.py worktree` i `python3 tools/apply_1018.py worktree` oraz `python3 tools/apply_1019.py worktree` i `python3 tools/apply_1020.py worktree` oraz `python3 tools/apply_1021.py worktree`. Powstanie biezacy `worktree/` z mapami CSV (w tym API 1021, OBF 10121 i wszystkie historyczne), narzedziami Go, kodem patcherow i mod/data.
3. Waliduj `worktree/mod/data/campaign/rules.csv`.
4. Zdobywaj oryginalne JAR z prywatnej Biblioteki uzytkownika i weryfikuj ich SHA; nie zakladaj ze sa w GitHub.
5. Kontynuuj audyt wszystkich pozostalych pol do wersji 1.1.

6. Przy zmianach dynamicznych skladanych z kilku literałów wykonuj test *calego zdania*: stary problem `C` + `onsumes` dawal `Czuzywa`; poprawiono w 1.0.19. `Misc.STORY` 81 wywolan w 24 klasach, 219 wywolan metod zaimkowych w 42 klasach (zliczono takze `InterfaceMethod`). Szczegoly `docs/RELEASE_1019.md`; nie zmieniaj globalnie `her` ani `story`.

7. Audyt pojedynczych literałów wykonuj na **oryginalnej JVM constant pool** (`tools/audit_exact_literals_1020.py`), nie na escaped tekstowych wynikach `javap`. Dwa wiersze API nie znajduja klas w bibliotece API (jeden jest juz pokryty w OBF); nie przedstawiaj ich jako dwa brakujace teksty w grze. Reprodukcja: `docs/RELEASE_1020.md`.

8. Audyt oryginalne `data.rar` kontra 870 podmienianych plikow: `tools/verify_source_fields_1021.py`. W 833 ustrukturyzowanych plikach rozne sa tylko wartosci literalow, w 18 CSV tylko dozwolone tekstowe kolumny (5 skryptow `SetTextHighlights`), 19 TXT wymagaja osobnego recznego audytu. Raport w Bibliotece `Starsector_PL_1021_DATA_FIELD_AUDIT.json`, wyniki w `docs/RELEASE_1021.md`. Nie myl tego z semantycznym audytem kazdego napisu. OBF 3144 zamian / 533 klasy, API 5106 / 936 klas, bez zmian bajtkodu poza referencjami do podmienionych tekstow.
