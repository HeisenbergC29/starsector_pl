# Starsector PL 1.0.29 — wydanie robocze (0.98a-RC8)

Wersja docelowa: **1.1**, nieukonczona. Oryginalne JAR sa prywatnymi materialami gry i nie sa publikowane w repo.

## Dokonane zmiany
- **OBF +23** nowych klasowo ograniczonych etykiet UI w 21 klasach, m.in. ludnosc, zarzadzanie, kredyty/miesiac, lata swietlne, ceny, zasieg, refit, stany oslony, grupy uzbrojenia.
- **API +7** w 6 klasach: `Go back` w czterech miejscach, niedobor zywnosci i ostrzezenie o niedoborze, `Fight!`.
- Zmiany wylacznie w literałach tekstowych; bez dotykania `Misc.STORY`, metod zaimkowych, ID, enum, technicznych kluczy, logiki.
- Pliki `mod/data/`: **870/870 identyczne** z 1.0.28; zmienione `mod_info.json`, `CZYTAJ.txt`, Go patchery i mapy.
- Aktywne mapy: OBF `TLUMACZENIA_OBF_10129.csv`, API `TLUMACZENIA_JAR_1029.csv`.
- **OBF 3508 dopasowan, 538 klas; API 5213 dopasowan, 938 klas** (mapa API ma 5215 wierszy, dwa historyczne odwolania nie trafiaja do klas API).

## Testy lokalne na oryginalnych komercyjnych bibliotekach
- OBF 3508 i API 5213 zatwierdzonych zmian tekstowych; **43 instrukcje `ldc`** dla nowych etykiet.
- Po patchowaniu struktura wykonywalna kazdej zmienionej klasy jest identyczna, zmieniaja sie tylko literały JVM i dozwolone sumy manifestu OBF.
- Swieza instalacja OBF + API **PASS**.
- Aktualizacja z **rzeczywiscie spatchowanej 1.0.28** do 1.0.29 daje identyczne bajtowo JAR co swieza instalacja: **PASS**.
- Ponowna instalacja bez nowych zmian oraz odzyskanie oryginalnych JAR bit-po-bicie: **PASS**.
- Celowo uszkodzone JAR sa odrzucane: **PASS**.
- 12 negatywnych testow naruszenia map, 7371/7371 opcji `rules.csv`, testy Go i `go vet`, kompilacja trzech EXE PE32+ Windows x64: **PASS**.
- Audyt wszystkich 870 danych wobec wydania 1.0.28: **brak zmian**.

Oryginalne SHA-256: OBF `5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8`; API `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`.
Spatchowane 1.0.29: OBF `fe13bdd519414be15e290ab1fcf84724524ea5e2f133b1bae6ce4e12ad90e71a`; API `030e3f3e1f4649de423a8dce5e64b0acd7849a9cd26063b38a87974eb954e0f2`.

## Odtworzenie i kontrola
```bash
python3 tools/restore_snapshot.py
for n in 1013 1014 1015 1016 1017 1018 1019 1020 1021 1022 1023 1024 1025 1026 1027 1028 1029; do
  python3 "tools/apply_$n.py" worktree
done
python3 tools/verify_1029_ui.py worktree
python3 tools/test_1029_delta.py worktree
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
python3 tools/package_1029.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.29_MINIMALNY.zip
```
Weryfikacja z prywatnymi oryginalnymi JAR: `python3 tools/verify_1029_callsites.py --obf /private/starfarer_obf.jar --api /private/starfarer.api.jar --out /tmp/ST_1029_CALLSITES.json`. Audit patched-vs-original: `tools/verify_1029_jars.py`.

**ZIP gracza:** `Starsector_PL_ASCII_0.98a_RC8_1.0.29_MINIMALNY.zip`, 14 294 963 bajtow, SHA `a5deb389b017adfd9011cc69438bc0f34fc3d06830fea71d40415ea70133a2e7`, 873 wpisy (870 data, mod_info.json, CZYTAJ.txt, instalator Windows x64). Bez oryginalnych JAR.

## Pozostale otwarte zadania
- Kontekstowa naprawa 81 wystapien `Misc.STORY` w 24 klasach (69 doklejonych `point/points`); globalna podmiana jest niebezpieczna.
- Poprawna odmiana dynamicznych zaimkow w skladanych zdaniach (219 odnotowanych wywolan).
- Semantyczny audyt 3659 aktywnie stosowanych wpisow API `DRAFT/OPTIONAL`, dalsze pominięte etykiety.
- Test instalatora i rozgrywki na **natywnym Windows**: **NIE WYKONANY**. Testy Linux i cross-build nie potwierdzaja poprawnego renderowania calej polonizacji.
