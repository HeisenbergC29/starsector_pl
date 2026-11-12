# Starsector PL 1.0.39 — kolejna poprawka dynamicznych zaimkow w dialogach

**Wersja gry:** Starsector 0.98a-RC8. **Stan:** wydanie robocze 1.0.39, niekompletna docelowa 1.1.

## Zakres rzeczywistych zmian

W `data/campaign/rules.csv` przeredagowano **62 niezaleznie wybrane rekordy dialogowe**, wykonujac **68 dokladnych podmian** w wylacznie widocznej kolumnie `text` i usuwajac **77 wystapien angielskich zmiennych zaimkowych**. Obejmuje m.in. komunikaty Tri-Tachyon, przeglady celne, dialogi zwiazane z Luddystami, terminale i sprzedaz danych oraz zdarzenia misji Akademii Galatia. Obok usuniecia zmiennych skorygowano kilka sformulowan naruszajacych polska gramatyke, np. odmieniane przymiotniki zalezne od plci osoby. Nie ingerowano w skrypty, warunki, identyfikatory, notatki ani podpisy `options`.

Na tle wersji 1.0.38 **869 pozostalych plikow `data/` ma identyczna zawartosc bajt po bajcie**. Mapy tlumaczen API i OBF oraz programy patchujace biblioteki Java nie zostaly zmienione. Zmienila sie tylko wersja we wspolnym instalatorze (`1.0.39`) oraz pliki informacyjne moda. Paczka nie zawiera komercyjnych oryginalnych bibliotek JAR.

Nie mylic tej poprawki z rozwiazaniem getterow w Java. **219 oryginalnych instrukcji wywolan metod zaimkowych** pozostaje ta sama liczba: 21 kontekstow reviewed offline z 1.0.38, **198** bez recenzji, wszystkie 219 bez wizualnego testu natywnego Windows. Konflikt wspolnej stalej `her` #143 w `BaseBarEventWithPerson` jest nadal otwarty.

## Potwierdzona odwracalnosc i integralnosc

- `rules.csv` przed 1.0.39, SHA256: `c09ff63ee5da19d93e17c66c4e8ed3f1beb0e805c885d6b32d67d878b5291e0d`.
- `rules.csv` po 1.0.39, SHA256: `fd7697b869bc4951204a7e90583ab8526ae1d046ba715454048b7cbaedcd3751`.
- `tools/verify_1039.py` odwraca **kazda** z 68 podmian w 62 rekordach i odtwarza dokladnie poprzedni SHA. Porownuje wszystkie siedem kolumn `rules.csv` rekord po rekordzie; dopuszcza tylko zmiany w `text` wybranych 62 identyfikatorow.
- 11107 rekordow danych reguly gry i **7371 poprawnych opcji dialogowych**, zero bledow parsera.
- `tools/verify_review_1039.py` potwierdza sumy SHA zmienionych pol oraz wszystkie poprzednie 27+64=91 recenzji (bez nadpisywania). Razem **153 zrecenzowane wiersze offline**, **260 usunietych wystapien zaimkow** w tekstach wzgledem wydania 1.0.33. Wszystkie 153 wymagaja wizualnego potwierdzenia Windows.
- `tools/verify_1039.py` weryfikuje niezmienione sumy SHA dwoch map tlumaczen i patcherow Go dla Java, 870 plikow ASCII i integralnosc `mod_info.json`.
- `tools/test_1039.py`: **12 testow negatywnych** z nieautoryzowanymi zmianami danych, checksum i ponownym zastosowaniem poprawki; wszystkie odrzucone. `tools/test_release_gates_1039.py`: **14 testow negatywnych** przeciwko pozornemu zakonczeniu 1.1; wszystkie odrzucone.
- `go test ./...` i `go vet ./...`: 3 komponenty Go zaliczone. Kompilacja 3 programow Windows x64, weryfikacja PE32+ x86-64: zaliczone.
- ZIP: **873 wpisy, w tym 870 plikow `data/`**, CRC zaliczone, **15 830 723 bajty**; SHA256 `ba2f3c8c1048b1941adecb632891493bd64b697a070aee72f649a2a128dc250e`.

## Odtworzenie ze zrodel repozytorium

```sh
python3 tools/restore_snapshot.py
for n in 1013 1014 1015 1016 1017 1018 1019 1020 1021 1022 1023 1024 1025 1026 1027 1028 1029 1030 1031 1032 1033 1034 1035 1036 1037 1038 1039; do
    python3 "tools/apply_${n}.py" worktree
done
python3 tools/verify_1039.py worktree
python3 tools/verify_review_1039.py worktree --ledger34 docs/RULES_PRONOUN_REVIEW_1034.json --ledger35 docs/RULES_PRONOUN_REVIEW_1035.json --ledger docs/RULES_PRONOUN_REVIEW_1039.json
python3 tools/check_release_gates_1039.py worktree --gates docs/RELEASE_GATES_11.json --ledger34 docs/RULES_PRONOUN_REVIEW_1034.json --ledger35 docs/RULES_PRONOUN_REVIEW_1035.json --ledger docs/RULES_PRONOUN_REVIEW_1039.json --api-ledger docs/API_SEMANTIC_REVIEW_1038.json
python3 tools/test_1039.py worktree
python3 tools/test_release_gates_1039.py worktree --gates docs/RELEASE_GATES_11.json --ledger34 docs/RULES_PRONOUN_REVIEW_1034.json --ledger35 docs/RULES_PRONOUN_REVIEW_1035.json --ledger docs/RULES_PRONOUN_REVIEW_1039.json --api-ledger docs/API_SEMANTIC_REVIEW_1038.json
(cd worktree && sh build_windows.sh)
python3 tools/package_1039.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.39_MINIMALNY.zip
```

Lokalnie mozna dodatkowo podac `--previous /PRIVATE/Starsector_PL_ASCII_0.98a_RC8_1.0.38_MINIMALNY.zip` do `verify_1039.py` i `package_1039.py` dla pelnego porownania wydan. Zrodla komercyjnej gry i JAR-y nalezy przechowywac prywatnie.

## Otwarte warunki wydania 1.1

`Misc.STORY` ma 81/81 kontekstow poprawionych offline, ale 81 nadal potrzebuje wizualnej kontroli. 153 poprawione wiersze `rules.csv` wymagaja kontroli w dzialajacej grze. Getter calls: 198 kontekstow do recenzji, 219 do Windows. Ze starszej puli API 3658 wpisow zostalo **3554** do recenzji jezykowej; 3693 w monitorowanej grupie nie bylo testowane w grze Windows. Brakuje niezaleznego pelnego przegladu kompletnego UI oraz rozgrywki Windows.

**Nie przedstawiaj tego wydania jako finalnej 1.1. Build Windows x64 nie jest natywnym testem gry.**
