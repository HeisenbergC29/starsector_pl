# Starsector PL 1.0.35 — poprawki dynamicznych dialogów

Wydanie pośrednie dla Starsector **0.98a-RC8**. Nie jest gotową wersją 1.1.

## Zakres zmian

W `data/campaign/rules.csv` poprawiono **64 wiersze**, wykonano **93 precyzyjne podmiany** i wyeliminowano **108 odwołań do dynamicznych zaimków**, które mogły wstawiać angielskie formy w polskie zdania. Przeredagowano całe fragmenty, a nie tylko pojedyncze angielskie słowa.

| Grupa dialogów | Wiersze |
|---|---:|
| Porty Tri-Tachyon, informacje o modyfikacjach okrętów | 16 |
| Kościół Ludda i patrole | 19 |
| Kustosz i sanktuarium | 21 |
| Powtórne powitania NPC | 8 |
| **Razem** | **64** |

Tam, gdzie trzeba było określić wykonawcę czynności, użyto polskich nazw ról — `rozmowca`, `oficer`, `kustosz`. Nie podmieniano globalnie getterów `HeOrShe`, `HisOrHer`, `HimOrHer`. W dwóch dialogach poprawiono podpis przycisku `lpp_hookCurateUpload`, zachowując dokładnie jego techniczny identyfikator.

## Integralność i testy

- Zmieniono wyłącznie kolumnę `text` i w dwóch wskazanych wierszach także `options`. Każdy pozostały identyfikator, warunek, skrypt oraz pole `notes` zostały zachowane.
- Z wydanego `rules.csv` 1.0.35 można odtworzyć **bajtowo identyczny** plik 1.0.34. Pozostałe 869 plików `data/` jest identycznych z oficjalną paczką 1.0.34.
- Zachowano ASCII, zakończenia linii CRLF, składnię CSV. Wszystkie **7371 opcji** mają poprawny format, bez błędów.
- **12 testów negatywnych danych** i **13 testów blokad wydania 1.1** zostało prawidłowo odrzuconych.
- Trzy komponenty Go: `go test` i `go vet` **PASS**; kompilacja trzech programów Windows PE32+ x64 **PASS**.
- Paczka: **870 plików danych, 873 wpisy ZIP**, test CRC **PASS**, brak oryginalnych komercyjnych bibliotek gry.
- Obie mapy tłumaczeń Java i patchery OBF/API pozostają identyczne z 1.0.34 (kod bibliotek jak w 1.0.33). Nowe wydanie dotyczy tylko danych dialogów i numeru instalatora.

## Postęp do 1.1 — rozdzielne metryki

- `docs/RULES_PRONOUN_REVIEW_1034.json`: 27 zatwierdzonych offline wierszy i 75 wyeliminowanych odwołań.
- `docs/RULES_PRONOUN_REVIEW_1035.json`: dodatkowe 64 wiersze i 108 odwołań.
- **Łącznie: 91 wierszy i 183 odwołania**. Wszystkie 91 wierszy nadal oczekują na kontrolę w działającej grze Windows.
- **219 wywołań metod zaimkowych Java** nadal nie zostało rozwiązanych. Liczba 183 oznacza usunięte odwołania w tekstach CSV, a nie zmiany instrukcji JVM.
- 81 kontekstów `Misc.STORY` jest poprawionych offline, ale nadal wymaga kontroli wizualnej w Windows.
- 3600 historycznych tłumaczeń API wymaga recenzji językowej; 3681 śledzonych fragmentów API nie przeszło testu runtime.
- Bramka wydania 1.1 pozostaje zamknięta w `docs/RELEASE_GATES_11.json`.

## Odtworzenie

```bash
python3 tools/restore_snapshot.py
for n in 1013 1014 1015 1016 1017 1018 1019 1020 1021 1022 1023 1024 1025 1026 1027 1028 1029 1030 1031 1032 1033 1034 1035; do
  python3 "tools/apply_${n}.py" worktree
done
python3 tools/verify_1035.py worktree
python3 tools/verify_review_1035.py worktree --prior-ledger docs/RULES_PRONOUN_REVIEW_1034.json --ledger docs/RULES_PRONOUN_REVIEW_1035.json
python3 tools/test_1035.py worktree
python3 tools/check_release_gates_1035.py worktree --gates docs/RELEASE_GATES_11.json
python3 tools/test_release_gates_1035.py worktree .
(cd worktree && sh build_windows.sh)
python3 tools/package_1035.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.35_MINIMALNY.zip
```

## Sumy SHA-256

| Plik | SHA-256 |
|---|---|
| `rules.csv` 1.0.34 | `ebcf0741e168dd7046259edeae506caceb6d93cd1f2f9c7ff315f9d52a13428d` |
| `rules.csv` 1.0.35 | `c09ff63ee5da19d93e17c66c4e8ed3f1beb0e805c885d6b32d67d878b5291e0d` |
| ZIP 1.0.35 | `08cb30cf426bf35f1e7e419d6f8bd1a07bf7d2b24b0eb731e37257dadb1e2d11` |

ZIP: **15 191 470 bajtów**, 873 wpisy. **Natywny test gry Windows nie został przeprowadzony.**
