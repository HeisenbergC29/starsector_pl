# Starsector PL 1.0.34 — poprawione dialogi ze zmiennymi zaimkowymi

Wersja gry: **0.98a-RC8**. Wydanie pośrednie **1.0.34**; pełna wersja **1.1 nadal nieukończona**.

## Zmiany przetłumaczonych danych

Wykonano **62 precyzyjne zmiany w 27 wierszach** polonizowanego `data/campaign/rules.csv` (26 pól `text`, jedna etykieta `options`). W ich wyniku usunięto **75 odwołań do dynamicznych zmiennych zaimkowych**, które mogły wstawiać angielskie formy do polskich wypowiedzi. Zamiast zamieniać globalnie `him`, `her`, `his` lub `man/woman`, przeredagowano całe zdania, zachowując znaczenie i poprawność w zależności od płci postaci.

| Grupa misji i dialogów | Wiersze | Zmiany |
|---|---:|---:|
| Akademia Galatia: Skok Poprzeczny (`gaTJ*`) | 7 | 15 |
| Akademia Galatia: informator na Kapteyn (`gaFC*`) | 6 | 12 |
| Pielgrzymi Ludda (`lpt*`, `LPT*`) | 5 | 18 |
| Powrót załogi placówki / rozmowy luddystów (`locrlf*`) | 9 | 17 |
| **Razem** | **27** | **62** |

Przykładowo wymieniono sklejone z angielskim zaimkiem zdanie „badacz ... [he/she] zdołał ...” na konstrukcję z „kontakt został nawiązany”, a mieszane „za plecami [him/her]” na „za plecami naukowca”. W zdaniach o pielgrzymach określenia dzierżawcze zastąpiono poprawnymi polskimi odniesieniami do grupy i dłoni. Zmienne dotyczące nazw postaci, planet, kwot, celów misji oraz obiektów gry pozostały na swoich miejscach.

## Integralność i zasady bezpieczeństwa

- **869 pozostałych plików** `data/` jest identycznych bajtowo z wydaniem 1.0.33; liczba plików nie zmieniła się: **870**.
- W zmienionym `rules.csv` nietknięte są wszystkie identyfikatory, warunki, wyzwalacze, skrypty i notatki. Jedyna zmiana w `options` dotyczy treści przycisku; techniczne `locrlf_startBar` pozostało bez zmian.
- Format pliku, komórki CSV, kodowanie ASCII i wszystkie zakończenia CRLF zachowano. Wszystkie **7371** opcji dialogowych przeszły test poprawności: **0 błędów**.
- Mapy tłumaczeń Java OBF 10133 / API 1033, oba patchery oraz docelowe sumy SHA-256 spatchowanych JAR **nie zmieniły się** względem 1.0.33. Zwiększony został wyłącznie numer wydania moda i połączonego instalatora.
- Potwierdzono odwrotne odtworzenie pliku 1.0.33 z pełnego zestawu zmian (identyczna suma SHA-256), odrzucanie uszkodzonego wejścia i niedozwolonych modyfikacji skryptów/opcji.
- Łącznie **11 negatywnych prób** zmian danych oraz **9 negatywnych testów** bramek wydania 1.1 zostało odrzuconych. `go test` i `go vet` dla obu patcherów i instalatora: **PASS**. Trzy pliki Windows PE32+ x86-64 zostały skompilowane: **PASS**.

## SHA-256 i paczka

| Plik | SHA-256 |
|---|---|
| `rules.csv` 1.0.33 | `c24d09cb29da3cccd01b40e2b8d318988000ebb132ad0de105fdf916e7b00e38` |
| `rules.csv` 1.0.34 | `ebcf0741e168dd7046259edeae506caceb6d93cd1f2f9c7ff315f9d52a13428d` |
| OBF po patchowaniu (bez zmian od 1.0.33) | `03729bc8e6ad0100ce4d0f7bf2f71bc198f917ff9e1b2fa5f9dacf4f35960a7a` |
| API po patchowaniu (bez zmian od 1.0.33) | `148f70c8bb45ef5d1e59c7ada1157766eb032e582bc12522b2e613e95a84839a` |
| ZIP `Starsector_PL_ASCII_0.98a_RC8_1.0.34_MINIMALNY.zip` | `559c5651367907396c078757925aceb4b5296bc6786e426462f8f5ac34da0487` |

ZIP: **15 191 440 bajtów, 873 wpisy, 870 plików danych, sprawdzona integralność CRC**. W paczce jest jeden instalator Windows x64; nie zawiera oryginalnych komercyjnych bibliotek JAR. Połączony instalator 1.0.34 wbudowuje te same sprawdzone patchery OBF/API co 1.0.33 i nie nadpisuje JAR, jeśli są już aktualne.

## Reprodukcja z GitHuba

```bash
python3 tools/restore_snapshot.py
for n in 1013 1014 1015 1016 1017 1018 1019 1020 1021 1022 1023 1024 1025 1026 1027 1028 1029 1030 1031 1032 1033 1034; do
    python3 "tools/apply_${n}.py" worktree
done
python3 tools/verify_1034.py worktree
python3 tools/verify_review_1034.py worktree --ledger docs/RULES_PRONOUN_REVIEW_1034.json
python3 tools/test_1034.py worktree
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
python3 tools/check_release_gates_1034.py worktree --gates docs/RELEASE_GATES_11.json --prior-ledger docs/API_SEMANTIC_REVIEW_1032.json --ledger docs/API_SEMANTIC_REVIEW_1033.json --rules-ledger docs/RULES_PRONOUN_REVIEW_1034.json
python3 tools/test_release_gates_1034.py worktree .
(cd worktree && sh build_windows.sh)
python3 tools/package_1034.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.34_MINIMALNY.zip
```

## Pozostaje do Starsector PL 1.1

**Nie wolno odejmować 75 zmian wyświetlanego tekstu od liczby 219 wywołań metod Java**: wywołania getterów nadal istnieją w skompilowanym kodzie, choć tekst w 27 poprawionych miejscach już nie wykorzystuje ich wyników. Szczególnie trudny pozostaje wspólny indeks `her` dla `getHisOrHer()` oraz `getHimOrHer()`.

Nadal otwarte: **219 wywołań getterów** wymagających kontekstowej kontroli, **81 tekstów `Misc.STORY`** oczekujących na oględziny w grze, **3600** starszych tłumaczeń API do kontroli językowej, kompletność całego interfejsu oraz rzeczywisty **test w działającym Starsector na Windows**. **27** nowych wierszy wymaga również potwierdzenia w grze.

Wszystkie oceny tej wersji są testami **offline**, nie potwierdzają bezbłędnej rozgrywki. Rejestr kontrolny `docs/RULES_PRONOUN_REVIEW_1034.json` przechowuje wyłącznie identyfikatory i sumy tekstów, bez rozpowszechniania oryginalnych zasobów komercyjnych.
