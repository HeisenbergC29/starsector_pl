# Starsector PL ASCII 1.0.54 — poprawki składanych komunikatów symulatora i kodeksu

**Gra:** Starsector 0.98a-RC8. **Data:** 2026-11-13. Wersja 1.1 **NIE** jest ukończona.

## Wprowadzone zmiany

W 1.0.53 interfejs `SimUpdateIntel` i `CodexUpdateIntel` łączył polskie prefiksy z angielskimi rzeczownikami (np. `faction/factions`, `variant/variants`, `entry/entries`), bo wcześniej nie przetłumaczono tych niewielkich stałych JVM. Dla 1, 2 i 5 składnia zmienia się także pomiędzy przypadkami, co uniemożliwia proste użycie jednego polskiego rzeczownika po `%s`.

W 1.0.54 zmieniono sześć starych wpisów mapy API i dodano **siedem** nowych ścisłych mapowań klasowych. Powiadomienia mają teraz neutralną konstrukcję: `Nowe frakcje w symulatorze: %s`, `Nowe warianty okretow w symulatorze: %s` oraz `Nowe wpisy w kodeksie: %s`. Angielskie fragmenty używane wyłącznie do tworzenia końcówek tych trzech powiadomień otrzymują pusty odpowiednik; nie dotyczy to identyfikatorów ani innych klas.

Oprócz tego poprawiono cztery opisy po zmiennej liczbie: `PhaseField` (liczba okrętów w zestawieniu sensorów), `PlanetSearchData$5` (wymagana liczba stabilnych lokalizacji), `BlockadeFGI` (liczba kolonii objętych blokadą) i `StandardPerseanLeagueActivityCause$1` (warunek liczby kolonii). Uniknięto konstrukcji typu `1 najwazniejszych okretow` i `1 stabilnymi lokalizacjami`. Wszystkie nowe teksty są ASCII, bez ingerencji w oryginalne znaczenie wartości.

| Element | Przed | Po |
|---|---|---|
| Symulator, 1 frakcja | `%s new faction` i częściowo polski prefiks | `Nowe frakcje w symulatorze: 1` |
| Symulator, 5 wariantów | `%s nowych kadlubow ` + `variants` | `Nowe warianty okretow w symulatorze: 5` |
| Kodeks, 2 wpisy | `%s nowych wpisow w Kodeksie ` + `entries` | `Nowe wpisy w kodeksie: 2` |
| Filtr planet | `co najmniej 1 stabilnymi lokalizacjami` | `liczba stabilnych lokalizacji wynosi co najmniej 1` |
| Sygnatura czujników | `1 najwazniejszych okretow` | `1 okr. o najwiekszej sygnaturze` |
| Blokada | `dla wszystkich 1 kolonii` | `dla wszystkich kolonii (liczba: 1)` |

**Zachowano istniejące znaczenie danych technicznych.** Zmodyfikowano wyłącznie `CONSTANT_String` w sześciu klasach API, bez zmian wykonywalnych instrukcji Java. OBF w wersji 1.0.53 oraz wszystkie 870 plików danych modu pozostały bajtowo bez zmian. Mapa API: 5283 → **5290 pozycji**, w tym **5288 skutecznych podmian w 938 klasach**. Pozostałe dwa historyczne mapowania API są obsługiwane przez inne warstwy, zgodnie z audytem 1.0.53.

## Dowody na oryginalnej grze i regresje

- Źródło: legalnie posiadany `starfarer.api.jar`, SHA-256 `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`.
- Każdy z **13** oryginalnych literałów odnaleziono w dokładnej klasie Java i potwierdzono instrukcją `ldc`/`ldc_w` wyświetlającą tekst.
- **Sześć** klas API zmienionych względem poprzedniego wydania, **zero nowych zmian bajtkodu wykonywalnego**.
- **35** wariantów z dynamicznymi liczbami, **8** celowych uszkodzeń mapy, **9** prób sztucznego zamknięcia bramek 1.1 — wszystkie PASS.
- Rzeczywisty patcher Go na oryginalnych JAR-ach: świeża instalacja = aktualizacja 1.0.53 → 1.0.54, identyczne SHA-256; ponowne zastosowanie bez zmian, odmowa nadpisania uszkodzonego JAR oraz restore obu oryginałów — PASS.
- API 1.0.54 SHA-256 `b5c256c78f92fb174456cb297660945d81690c33d21d513627b0547ed783eb14`; OBF pozostaje `85b4b2afb4f6175cabedf1ef5cb9976e0097e39403dff0fc18c728c9d48894e1`.
- Dokumenty audytowe: `docs/JVM_AUDIT_1054.json`, `docs/API_SEMANTIC_REVIEW_EVIDENCE_1054.json`, `docs/UPGRADE_1054.json`.

## Semantyczny rejestr 1.1

Na podstawie oryginalnego JVM przejrzano **19 historycznych** wpisów DRAFT/OPTIONAL z powyższych klas (w tym sześć poprawionych). Dotychczasowe 324 recenzje pozostają bez zmian, czyli razem jest **343/3658**, a **3315** pozostaje do przeglądu. Siedem nowo dodanych stałych nie zostało wliczonych do historycznego mianownika.

## Reprodukcja w GitHub Actions

Po odtworzeniu snapshotu i wcześniejszych nakładek do 1.0.53:

```sh
python3 tools/apply_1054.py worktree
python3 tools/verify_1054.py worktree
python3 tools/test_1054.py worktree
python3 tools/verify_review_1054.py worktree --previous docs/API_SEMANTIC_REVIEW_1052.json --ledger docs/API_SEMANTIC_REVIEW_1054.json
python3 tools/check_release_gates_1054.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/API_SEMANTIC_REVIEW_1052.json --ledger docs/API_SEMANTIC_REVIEW_1054.json
python3 tools/test_release_gates_1054.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/API_SEMANTIC_REVIEW_1052.json --ledger docs/API_SEMANTIC_REVIEW_1054.json
(cd worktree && sh build_windows.sh)
python3 tools/package_1054.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.54_MINIMALNY.zip
```

Prawdziwe komercyjne biblioteki JAR **nie są** publikowane. Sprawdzenie stałych JVM i test aktualizacji na kopiach JAR-ów wykonano wyłącznie lokalnie. Testy w rzeczywiście uruchomionej grze Windows **nie były** wykonane.

## Co nadal blokuje 1.1

3315 historycznych tłumaczeń API nie ma jeszcze pełnego przeglądu, 186 kontekstów getterów zaimkowych jest otwartych, a liczne dynamiczne teksty `rules.csv` wymagają audytu oraz wizualnej weryfikacji. Dodatkowo znaleziony w `BlockadeFGI` angielski fragment `more day(s)` jest składany w sposób wymagający ostrożniejszej zmiany — **nie zmieniono go bez pewności co do semantyki**, pozostaje zadaniem przyszłego etapu. Brak testu gry Windows i pełnej zgodności wszystkich napisów; wersja 1.0.54 nie spełnia jeszcze kryteriów 1.1.
