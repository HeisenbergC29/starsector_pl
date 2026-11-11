# Starsector PL: instrukcje dla kolejnego agenta

**Aktualny stan roboczy: 1.0.15** (snapshot bazowy 1.0.12 + kolejno `tools/apply_1013.py`, `tools/apply_1014.py`, `tools/apply_1015.py`).

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

## Start pracy w nowym czacie
1. Czytaj README, docs/STATUS.md i docs/TEST_109_CRASH.md.
2. Uruchom `python3 tools/restore_snapshot.py` (wymagany zstd), nastepnie `python3 tools/apply_1013.py worktree` i `python3 tools/apply_1014.py worktree` oraz `python3 tools/apply_1015.py worktree`. Powstanie biezacy `worktree/` z mapami CSV (w tym 1013, 1014 i 1015), narzedziami Go, kodem patcherow i mod/data.
3. Waliduj `worktree/mod/data/campaign/rules.csv`.
4. Zdobywaj oryginalne JAR z prywatnej Biblioteki uzytkownika i weryfikuj ich SHA; nie zakladaj ze sa w GitHub.
5. Kontynuuj audyt wszystkich pozostalych pol do wersji 1.1.
