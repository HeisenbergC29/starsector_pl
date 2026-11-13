# Starsector PL ASCII 1.0.52 — kontekstowe zaimki w wydarzeniach barowych

**Gra:** Starsector 0.98a-RC8  
**Data:** 2026-11-13  
**Baza:** zweryfikowane wydanie 1.0.51, API mapa SHA256 `099abe6d62264e6b1d4ff66b9aba196ecb7d11845b7d2b2207aab4a8b8f66aa4`.  
**Nowa mapa:** `TLUMACZENIA_JAR_1052.csv`, **5283 wpisy**, SHA256 `ddcec94935d80bcee715514352f79ffbea113ec299953c422746a94241ee179c`.

**Status:** robocza wersja 1.0.52. Wydanie docelowe **1.1 pozostaje otwarte**; brak potwierdzenia przez rozgrywke na Windows.

## Kluczowy wynik: konflikt wspoldzielonego `her` nie wymaga zmian JVM

Oryginalna klasa `BaseBarEventWithPerson` posiada wspolna stala `#143 // String her` uzywana zarowno przez `getHimOrHer()`, jak i `getHisOrHer()`. W wersji 1.0.51 nie byla tlumaczona ze wzgledu na podejrzenie konfliktu przypadkow gramatycznych.

Przeanalizowano wszystkie **11 wywolan obu getterow** w dwoch oryginalnych klasach korzystajacych z dziedziczonych metod: 1+3 w `LuddicPathBaseBarEvent` oraz 1+6 w `PlanetaryShieldBarEvent`. Obydwa wywolania `getHimOrHer()` wystepuja w sytuacji **celownika** (propozycja dolaczenia do floty oraz postawienie drinka). W obydwu sprawdzonych uzyciach odpowiadaja im odpowiednio **mu / jej**. Dziewiec wywolan `getHisOrHer()` daje polskie **jego / jej**. Wspolna forma zenska **jej** jest wiec zgodna z tymi kontekstami i nie wymaga rozdzielenia stalych w bytecode.

Dodano **5** tlumaczen do `BaseBarEventWithPerson`: `man`→`mezczyzna`, `woman`→`kobieta`, `him`→`mu`, `his`→`jego`, `her`→`jej`.

Niezbedne byly rowniez **9 nowych** i **10 poprawionych** fragmentow klasowych w wydarzeniach. Przestawiono konstrukcje zdań, aby odmiana byla poprawna dla obu plci bez zmiany semantyki gry:

- `Widzisz, jak mezczyzna/kobieta ... z ... w jego/jej oczach.`
- `Przystan na jego/jej warunki.`
- `Akceptujesz warunki, ktore stawia mezczyzna/kobieta, i dokonujesz niezbednych ustalen.`
- `Zamiast tego zaproponuj mu/jej dolaczenie do swojej floty.`
- `Przepros za nieporozumienie, stawiajac mu/jej drinka.`
- `Nie zaklocaj jego/jej odpoczynku.`
- `On/ona kreci glowa. Z jego/jej ust pada ...` (kontekst polskiego zdania wymaga dalszej kontroli kapitalizacji po poprzedzajacym tekscie).

Dwa poczatkowo zaplanowane klucze pomijaly koncowe spacje w **oryginalnej puli stalych** (`A ` i ` temple. `). Wykryto to niezaleznym audytem JVM i skorygowano przed wydaniem; wszystkie **24 zamierzone mapowania** sa teraz zakotwiczone w oryginalnym `CONSTANT_String` dokladnie jeden raz. Testowane kompozycje 10 kontekstow × 2 plcie zachowuja kolejnosc, spacje i skladnie; nie stanowia jednak testu wszystkich realnych przebiegow dialogow.

## Mapa tlumaczen i niezmiennosc logiki

W stosunku do 1.0.51 dokonano **14 nowych, dokladnie klasowych tlumaczen** oraz **10 poprawek** zapisanych wpisow DRAFT/OPTIONAL, bez zmiany angielskich identyfikatorow, statusow dawnych wpisow, placeholderow czy innych 5259 pozycji mapy. Mapę zapisano CSV UTF-8 z CRLF; widoczne teksty gry zawieraja tylko polski ASCII.

**Weryfikacja na oryginalnej komercyjnej bibliotece API**:

- Oryginalny `starfarer.api.jar`: SHA256 `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`.
- Zmodyfikowany API po 1.0.52: SHA256 `5d53fa936ada275642a93b523f4a3e5ef45c10d3f16ed82465ed5476d27414c7`.
- **5281 faktycznych podmian** w **938 klasach**.
- Porownanie patchowanego API 1.0.51 i 1.0.52: roznia sie **dokladnie trzy klasy**, wszystkie inne pliki JAR identyczne.
- Zmiana dotyczy wylacznie wpisow puli stalych i dodanych napisow UTF8. **Zero nowych zmian wykonywalnych instrukcji JVM**; wczesniejszy, osobno zatwierdzony wyjatek dwoch operandow osobowosci z 1.0.51 zachowano bez zmian.
- Wszystkie **870** plikow `mod/data/` i OBF bez zmian.
- Test rzeczywistej aktualizacji **1.0.51 → 1.0.52**, instalacji od zera, ponownego zastosowania bez zmian, odmowy zmiany uszkodzonego ZIP i pelnego przywracania oryginalow: **PASS**; fresh = upgrade bajtowo. Raport: `docs/UPGRADE_1052.json`.
- Audyt trzech klas JVM i 13 wywolan getterow osobowosci/plci: `docs/JVM_AUDIT_1052.json`; 20 symulowanych skladowych komunikatow i 8 testow negatywnych: `docs/COMPOSITE_UI_1052.json`.

## Rejestr semantyczny i pozostale warunki 1.1

10 poprawionych wierszy DRAFT/OPTIONAL po raz pierwszy zrecenzowano na oryginalnych stalych; poprzednich **314** recenzji nie przeliczono ponownie. Lacznie **324 z 3658** historycznych wpisow API zweryfikowanych offline; **3334 pozostaja**. Nowych 14 literalow nie doliczono do historycznego mianownika 3658.

W bramkach wydania `docs/RELEASE_GATES_11.json` konflikt samej stalej `her` w klasie bazowej oznaczono **rozwiazany offline**, nadal **oczekuje na walidacje w grze Windows**. Zachowano konserwatywnie **186** nierozpatrzonych kontekstow getterow w szerszym korpusie, bez nieuprawnionego odejmowania wywolan z poprzedniego audytu. Do oceny pozostaje takze 2275 surowych zmiennych zaimkowych w 1139 rekordach `rules.csv`, weryfikacja wszystkich pozostalych tekstow i rzeczywista rozgrywka.

**Nie deklarowac pelnej wersji 1.1 na podstawie audytu offline.** Oryginalne komercyjne JAR nie sa publikowane.

## Odtworzenie wydania

Po odtworzeniu snapshotu 1.0.12 i wszystkich overlayow do 1.0.51:

```bash
python3 tools/apply_1052.py worktree
python3 tools/verify_1052.py worktree
python3 tools/test_1052.py worktree
python3 tools/verify_review_1052.py worktree --previous docs/API_SEMANTIC_REVIEW_1051.json --ledger docs/API_SEMANTIC_REVIEW_1052.json
python3 tools/check_release_gates_1052.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/API_SEMANTIC_REVIEW_1051.json --ledger docs/API_SEMANTIC_REVIEW_1052.json
python3 tools/test_release_gates_1052.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/API_SEMANTIC_REVIEW_1051.json --ledger docs/API_SEMANTIC_REVIEW_1052.json
(cd worktree && sh build_windows.sh)
python3 tools/package_1052.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.52_MINIMALNY.zip
```

Prywatny audyt oryginalnych JAR jest uruchamiany poza CI — `tools/private_jvm_1052.py` oraz `tools/private_upgrade_1052.py` — z biblioteki posiadanej przez wlasciciela gry. CI nie dostaje komercyjnych bibliotek.
