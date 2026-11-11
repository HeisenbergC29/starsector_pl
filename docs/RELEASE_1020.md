# Starsector PL 1.0.20 — wydanie robocze 2026-11-11

**Gra:** Starsector 0.98a-RC8. **Cel 1.1 nadal NIE jest zakonczony.**

## Rzeczywiste zmiany
- **7 poprawek** wcześniej przetłumaczonych fragmentów w `PlanetaryShieldBarEvent`. Błędy wynikały ze składania polskich zdań z dynamicznym `getHeOrShe()` (niedopasowane czasy, rodzaj, odstępy). Przyklady po poprawce: `Zapytaj doswiadczonego kosmonaute, co ona obserwuje`, `Kosmonauta wyjasnia, ze tylko on i pilot zdolali uciec w kapsule ratunkowej`.
- **1 nowa podmiana** w `CorruptPLClerkSuppliesBarEvent`: ` says.` → ` mowi.`.
- Test sprawdza **10 pełnych zdań** osobno dla `on` i `ona`; zachowano składnię i brak podwójnych spacji.
- Pola techniczne i identyfikatory niezmienione. **870/870 plików `data/` bajtowo identycznych z 1.0.19.**
- Mapa API **5107 wierszy, 5105 rzeczywistych podmian w 936 klasach**. OBF **bez zmian** względem 1.0.18: 3142 podmiany w 533 klasach.

## Testy na oryginalnych JAR (Linux)
| Test | Wynik |
| --- | --- |
| Oryginalne sumy SHA-256 obu JAR zgodne z wersją 0.98a-RC8 | PASS |
| Tylko zatwierdzone podmiany `CONSTANT_String` w API (audyt klasy po klasie) | PASS |
| Niezmieniony bajtkod metod i pozostałe elementy API JAR | PASS |
| Świeża instalacja OBF i API | PASS |
| Upgrade API 1.0.19 → 1.0.20, wynik identyczny ze świeżą instalacją | PASS |
| Ponowna instalacja bez zmian | PASS |
| Przywrócenie bajtowo oryginalnych bibliotek OBF i API | PASS |
| 10 kompletnych wariantów zdań z dwoma rodzajami | PASS |
| Go test i vet, trzy EXE PE32+ Windows x64 | PASS |
| `rules.csv` 7371/7371 opcji poprawnych | PASS |
| ZIP CRC, 873 pliki, 870 danych, oryginalnych JAR nie dołączono | PASS |
| Natywny test Windows oraz uruchomienie gry | NIE WYKONANO |
| Ukończenie wszystkich tłumaczeń w wersji 1.1 | NIEPOTWIERDZONE |

**API patched SHA-256:** `300e5b339f1ed512743ba93876ffb53a7a7b6c551fc34a4211954e89c24fb770`.
**OBF patched SHA-256 (bez zmian):** `c95b45715e4d7c1b982d154acdc6776a3cf60756e83eefb00ea526a96c5a6c92`.

## Nowy dokładny audyt JVM, eliminujący fałszywe alarmy `javap`
`tools/audit_exact_literals_1020.py` czyta oryginalną pulę stałych klas, nie tekstowy wynik `javap`. W starszych raportach apostrofy/cudzysłowy ucieczkowe powodowały fałszywe wskazania — np. wcześniejsze podejrzenie 14 angielskich literałów w `CorruptPLClerkSuppliesBarEvent` było nieprawdziwe. Faktyczny brak dla tej klasy: ` says.` (plus nierozwiązane dynamiczne zaimki).

Wynik dla oryginalnych bibliotek i map:
- **API:** 3450 klas, 23254 unikalne w klasach `CONSTANT_String`, 5105 dopasowanych podmian, 246 podejrzanych niezamapowanych tekstów według heurystyki; 2 mapowania wskazują klasy nieobecne w tym JAR.
- **OBF:** 2818 klas, 14889 unikalnych literałów w klasach, 3142 dopasowania, 427 heurystycznych kandydatów; brak niedopasowanych wierszy mapy.
- Dwóch niedopasowanych wierszy API **nie należy automatycznie usuwać**: `Select ships to recover` jest już obecne i tłumaczone w OBF; `data/hullmods/SurveyingEquipment.java` nie jest klasą w API JAR, wymaga sprawdzenia źródła skryptu.
- **Kandydat heurystyczny NIE oznacza tekstu wyświetlanego w grze**, a suma unikalnych literałów nie jest procentem ukończenia polonizacji. Wiele wartości to diagnostyka, identyfikatory lub kod pomocniczy.

Kompletny audyt z kandydatami pozostaje prywatnie w Bibliotece projektu jako `AUDIT_EXACT_API_1020.json` i `AUDIT_EXACT_OBF_1020.json`. Nie publikować komercyjnych literałów z oryginalnych JAR.

## Pakiet i odtworzenie

`Starsector_PL_ASCII_0.98a_RC8_1.0.20_MINIMALNY.zip`
- **12 029 872 bajtów**, SHA-256 **`8dbd429a220ccd180891e4f5fd83d6846ab0322f29e9bdb4abd4ec0bbb311961`**.
- ZIP i `Starsector_PL_1.0.20_TESTY.json` zapisano w prywatnej Bibliotece projektu.

```sh
python3 tools/restore_snapshot.py
for n in 1013 1014 1015 1016 1017 1018 1019 1020; do
  python3 "tools/apply_$n.py" worktree
done
python3 tools/verify_1020_dialogs.py worktree
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
python3 tools/package_1020.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.20_MINIMALNY.zip
```

## Do 1.1
Zaimki poza formami podmiotowymi w 219 wywołaniach, 81 użyć `Misc.STORY`, kontrole dynamicznych dialogów i znaczników formatowania, niezweryfikowane semantycznie grupy `DRAFT/OPTIONAL`, oraz rzeczywisty test w Windows/grze. Nie twierdzić, że test CI jest testem uruchomionej gry.
