# Starsector PL ASCII 1.0.53 — brakujace liczebniki w oknie odzyskiwania okretow

**Gra:** Starsector 0.98a-RC8. **Data:** 2026-11-13. **Stan:** wydanie robocze 1.0.53, pelna wersja 1.1 nadal OTWARTA.

## Wykryty i naprawiony blad

Audyt wszystkich 5283 wierszy mapy API na oryginalnym `starfarer.api.jar` wykazal **dwa wiersze skierowane do nieistniejacych tam klas**. Oba sa od dawna objete polonizacja w prawidlowej warstwie: 

* `data/hullmods/SurveyingEquipment.java`: polski opis i skroty `jedn.` znajduja sie juz w pliku Java wysylanym w `mod/data/`;
* `com.fs.starfarer.ui.newui.FleetMemberRecoveryDialog`: naglowek `Select ships to recover` zostal juz spolonizowany przez OBF; angielskie bajty pozostaja w puli stalych nieuzywane po przekierowaniu `CONSTANT_String`.

Bledna hipoteze, ze naglowek pozostaje angielski, odrzucono po sprawdzeniu **aktywnej referencji** w JVM (`ldc_w #816`). Nastepnie oryginalny `FleetMemberRecoveryDialog` wskazal **trzy inne rzeczywiste braki** `ship`, `ships` i ` ships` w tekstach z dynamicznie podstawiana liczba okretow:

| Klucz OBF, JVM | Polski ASCII | Widoczny przyklad |
| --- | --- | --- |
| `ship` (#823) | `okr.` | `Wybrano 1 okr. do odzyskania` |
| `ships` (#821) | `okr.` | `Wybrano 5 okr. do odzyskania` |
| ` ships` (#1248) | ` okr.` | `Podjeto nadzwyczajne wysilki, aby odzyskac 5 okr.` |

**Dlaczego skrot `okr.`:** oryginalny kod rozroznia `ship` i `ships`, ale angielska liczba mnoga obejmuje zarowno 2, jak i 5. Jedna polska forma rzeczownika nie pasuje do obu wartosci, a niezalezny od liczby skrot usuwa blad bez modyfikacji logiki.

## Zmiany techniczne

- **OBF:** dodano trzy precyzyjnie klasowe mapowania do 3534 wierszy: **3537 rzeczywistych podmian w 539 klasach**. Oryginalna mapa `TLUMACZENIA_OBF_10133.csv` SHA-256 `f2ffdb534d870a49fce81dea47b4ebbac8fdccc218b79d5bed0f3752485cd484`; nowa `TLUMACZENIA_OBF_10153.csv` SHA-256 `435da69852718501146f08b4fada80ae2714c9142b435f90e600c86c594120be`.
- **API:** mapa `TLUMACZENIA_JAR_1053.csv` jest bajtowo identyczna z 1.0.52 (`ddcec94935d80bcee715514352f79ffbea113ec299953c422746a94241ee179c`). Obie maja 5283 wiersze, w tym **dwa niefunkcjonalne wpisy historyczne**, pozostawione dla zgodnosci historii; rzeczywiste API podmienia 5281 literałów w 938 klasach. Go patcher API otrzymal nowy numer wydania oraz dopuszcza nowy zweryfikowany SHA OBF.
- **Metody Java:** zmienily sie tylko trzy klasywe wskazania `CONSTANT_String` w jednej klasie OBF oraz odpowiadajace im sumy kryptograficzne w manifeście JAR. **Zero zmian wykonywalnych instrukcji JVM** w 1.0.53; wczesniejszy kontrolowany wyjatek z 1.0.51 pozostaje nietkniety.
- **Pliki data:** wszystkie 870 plikow niezmienione, w tym `rules.csv`; mod version i instrukcja instalacji zaktualizowane do 1.0.53.

## Testy na oryginalnych komercyjnych bibliotekach (prywatnie)

- SHA oryginalnego OBF `5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8`.
- OBF 1.0.52 `03729bc8e6ad0100ce4d0f7bf2f71bc198f917ff9e1b2fa5f9dacf4f35960a7a`.
- **OBF 1.0.53:** `85b4b2afb4f6175cabedf1ef5cb9976e0097e39403dff0fc18c728c9d48894e1`.
- **API 1.0.53 (bez zmian JAR od 1.0.52):** `5d53fa936ada275642a93b523f4a3e5ef45c10d3f16ed82465ed5476d27414c7`.
- Oryginalne `ldc_w` dla 3 fragmentow oraz naglowka zweryfikowane co do indeksu i liczby instrukcji (po jednym wywolaniu).
- Swieza instalacja obydwu patcherow i aktualizacja z 1.0.52: **bajtowo identyczne dwa JAR-y**. Ponowne uruchomienie (no-op), odmowa nadpisania uszkodzonego OBF i pelne przywrocenie obu oryginalow: **PASS**.
- Testy Go `go test ./...`, `go vet ./...` dla obu patcherow: **PASS**. Symulacje dynamicznych liczebnikow 1,2,5,12,21 w dwoch rodzajach napisow: **10 PASS**. Piec testow negatywnych struktury mapy i dziewiec falszywych statusow 1.1 odrzuconych.

Wyniki: `docs/JVM_OBF_RECOVERY_1053.json`, `docs/API_OBF_ROUTING_1053.json`. Kod testow: `tools/private_integration_1053.py`, `tools/verify_1053.py`, `tools/test_1053.py`.

## Reprodukcja CI

Po odtworzeniu snapshotu 1.0.12 i nalozeniu wersji 1.0.13 ... 1.0.52:

```bash
python3 tools/apply_1053.py worktree
python3 tools/verify_1053.py worktree
python3 tools/test_1053.py worktree
python3 tools/check_release_gates_1053.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/API_SEMANTIC_REVIEW_1051.json --ledger docs/API_SEMANTIC_REVIEW_1052.json
python3 tools/test_release_gates_1053.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/API_SEMANTIC_REVIEW_1051.json --ledger docs/API_SEMANTIC_REVIEW_1052.json
(cd worktree && sh build_windows.sh)
python3 tools/package_1053.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.53_MINIMALNY.zip
```

Komercyjne JAR nie sa przesylane na GitHub ani w finalnej paczce. Brak rzeczywistego gameplay Windows.

## Warunki docelowej 1.1 wciaz otwarte

**324/3658** historycznych API zrecenzowane offline, **3334** bez przegladu semantycznego; **186** szerszych getter-callsite Java do audytu; 2275 surowych zaimkow w 1139 rekordach rules.csv do przegladu; brak pelnej kontroli wizualnej i natywnej rozgrywki Windows. 1.0.53 nie nalezy nazywac 1.1.
