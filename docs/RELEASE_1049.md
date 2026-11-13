# Starsector PL ASCII 1.0.49 — dynamiczne etykiety odzysku i recenzja UI

**Data:** 2026-11-13  
**Gra:** Starsector 0.98a-RC8  
**Poprzednia mapa:** `TLUMACZENIA_JAR_1048.csv` — SHA-256 `2f85b133be0d3087321d16dd71080f5214cf9e2932cc60381ecbab521b273289`.  
**Nowa mapa:** `TLUMACZENIA_JAR_1049.csv` — SHA-256 `3ae9e6c3e8675139a9aa3bc91ca88f32fc2b65301f5b7657e8936c85d81c5420`.  
**Status:** wydanie rozwojowe **1.0.49**. Pełna polonizacja **1.1 nie jest ukończona**. Pliki gry stosują polski ASCII bez diakrytyków.

## 1. Naprawa faktycznego błędu składanego tekstu Java

`com.fs.starfarer.api.impl.campaign.intel.misc.SalvorsTallyIntel` konstruuje pięć pozycji zestawienia odzysku przez sklejenie tekstu bazowego z angielskim `s` (liczba mnoga). Poprzednia mapa polonizowała same bazy, ale pozostawiała kodowi dopisanie `s`. Prowadziło to do błędów typu `5 porzucony okrets`, a dla `unexplored planetside ruin` stała `s` jest nawet przypisywana niezależnie od liczby przedmiotów.

Wersja 1.0.49 w **tej jednej klasie** zamienia oryginalną stałą `s` na pusty napis. To nie jest globalna zamiana ani zmiana instrukcji JVM. Pięć baz zostało równocześnie przeredagowanych na etykiety niezależne od liczby:

| Oryginalny literal JVM | Polska baza bez zmiennej liczby mnogiej |
|---|---|
| `%s derelict ship` | `Wraki okretow: %s` |
| `%s orbital installation` | `Instalacje orbitalne: %s` |
| `%s other source` | `Inne miejsca odzysku: %s` |
| `%s unexplored debris field` | `Niezbadane pola szczatkow: %s` |
| `%s unexplored planetside ruin` | `Niezbadane ruiny na planetach: %s` |

`javap -c -p` na oryginalnym JAR potwierdził sześć instrukcji `ldc #128 // String s`, wszystkie w tym mechanizmie tworzenia liczby mnogiej. Ścieżka modyfikacji to wyłącznie `CONSTANT_String` i nowa `CONSTANT_Utf8` pusta; położenie i bajty kodu metod pozostają niezmienione.

## 2. Pozostałe dokładnie ograniczone korekty API

Wykonano 13 korekt istniejących mapowań oraz dodano dokładnie jedno nowe mapowanie `s -> ""` (`5260 -> 5261` wierszy mapy). Nowe poprawki w siedmiu klasach objęły:

- `CommodityProductionMission` (2): okresy umowy zapisane jako `Liczba cykli: %s`, bez błędu `1 cykli`;
- `HypershuntIntel` (1): dodatkowe zakłady przemysłowe opisane jako zwiększenie ich liczby o `%s`, niezależnie od tego, czy wartość to 1, 2, czy 5;
- `SalvorsTallyIntel` (5 + 1): pięć liczebnikowo neutralnych etykiet i wyłączenie angielskiego sufiksu;
- `BaseHubMission`, `RaidSecretOutpostMission`, `MarketCMD$2` (4): neutralna odmiana liczby żołnierzy piechoty morskiej jako `%s zoln.`;
- `HyperspaceTopographyEventIntel` (1): `ls` ujednolicono do `l. sw.`, a limit macierzy pokazano jako `Maksymalna liczba wykorzystywanych macierzy czujnikow: %s`.

Nie modyfikowano identyfikatorów, angielskich kluczy, statusów istniejących wierszy ani kodu Java. Wszystkie 870 plików `mod/data/` są identyczne z wydaniem 1.0.48.

## 3. Weryfikacja map i rzeczywistych bibliotek

| Kontrola | Potwierdzony wynik |
|---|---|
| Oryginalne literały `CONSTANT_String` | **58/58** — 14 pozycji nowej poprawki, 44 dodatkowe krótkie teksty UI |
| Oryginalne wywołania `ldc` używające `s` | **6/6**, tylko mechanizm liczby mnogiej `SalvorsTallyIntel` |
| Zmienione klasy API w porównaniu 1.0.48 → 1.0.49 | **7** |
| Zmienione klasy API w porównaniu do oryginału | **938** |
| Faktyczne podmiany w oryginalnym API JAR | **5259** |
| Modyfikacje wykonywalnego bajtkodu metod Java | **0** |
| Podstawienia dla 1, 2 i 5 | **54/54 PASS** |
| Testy negatywne mapy i znaczników | **8/8 prawidłowo odrzuconych** |
| Mutacje zamknięcia bramek 1.1 | **8/8 prawidłowo odrzuconych** |
| `GO111MODULE=off go test ./...` i `go vet ./...` API | **PASS lokalnie** |
| Fresh install vs upgrade API **1.0.48 → 1.0.49** | Bajtowo identyczne (**PASS**) |
| Reapply / uszkodzona metadana ZIP / restore | **PASS / odrzucona / PASS** |
| Natywny gameplay Windows | **NIE przeprowadzono** |

**SHA-256 API po 1.0.49**: `423fbd7c1afc5b1e0322c6c7c8aa64e0c4cfc84645cec37a92772a387bbdb9f6`.  
**SHA-256 oryginalnego API**: `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`.  
**SHA-256 oryginalnego OBF**: `5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8`.

**Dowody:** `docs/API_TEXT_CORRECTIONS_1049.json`, `docs/JVM_AUDIT_1049.json`, `docs/PRIVATE_UPGRADE_1049.json`; testy `tools/verify_1049.py`, `tools/test_1049.py`, `tools/private_jvm_audit_1049.py`, `tools/private_upgrade_1049.py`. Oryginalne komercyjne biblioteki nie są dołączane ani publikowane.

## 4. Dalsza semantyczna recenzja historycznych wpisów API

Do rejestru dopisano **44 krótkie, konkretne teksty UI** sprawdzone w oryginalnym JVM, m.in. awans oficera, ukończenie kontraktu, schematy wyposażenia, uszkodzenia w bitwie i wybór jednostek do odzyskania. Dodano również **5 poprawionych wpisów DRAFT/OPTIONAL** z punktu 2.

Wynik: **203 + 49 = 252** z historycznych **3658** wierszy sprawdzonych offline; **3406** pozostaje bez pełnej recenzji semantycznej. Poprzednie 203 wpisy w `docs/API_SEMANTIC_REVIEW_1048.json` są zachowane bez modyfikacji. Rejestr `docs/API_SEMANTIC_REVIEW_1049.json` jest wyliczany i walidowany z rzeczywistej mapy. **Status DRAFT/OPTIONAL nie znaczy, że wiersz nie jest instalowany.** Recenzja jest offline i nie zastępuje testu renderowania w Windows.

## 5. Odrębny problem zaimków, którego NIE naprawiano automatycznie

W `BaseBarEventWithPerson` metody `getHimOrHer()` i `getHisOrHer()` współdzielą literał `her` (`#143`), lecz wymagają po polsku innych przypadków gramatycznych. Nie wolno zastąpić `her` jedną polską formą w całej klasie. W `FactionPersonalityPickerPluginImpl` podobny konflikt dotyczy krótkich tekstów UI zawierających nazwy cech oficera — częściowo używane także jako identyfikatory logiki. W obu miejscach do dalszych działań potrzebna jest szersza analiza kontekstu i osobne testy.

Bramka `shared_her_conflict_open=true` i licznik **186** getterów Java bez zakończonej recenzji pozostają bez zmian. Wszystkie testy w działającej grze Windows oraz pełny audyt widocznych tekstów nadal pozostają otwarte. **Nie wydawać jako 1.1.**

## Reprodukcja

Po standardowym odtworzeniu snapshotu 1.0.12 i nakładek `tools/apply_1013.py`–`tools/apply_1048.py`:

```bash
python3 tools/apply_1049.py worktree
python3 tools/verify_1049.py worktree
python3 tools/test_1049.py worktree
python3 tools/verify_review_1049.py worktree --previous docs/API_SEMANTIC_REVIEW_1048.json --ledger docs/API_SEMANTIC_REVIEW_1049.json
python3 tools/check_release_gates_1049.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/API_SEMANTIC_REVIEW_1048.json --ledger docs/API_SEMANTIC_REVIEW_1049.json
python3 tools/test_release_gates_1049.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/API_SEMANTIC_REVIEW_1048.json --ledger docs/API_SEMANTIC_REVIEW_1049.json
(cd worktree && sh build_windows.sh)
python3 tools/package_1049.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.49_MINIMALNY.zip
```

Prywatne testy oryginalnych bibliotek:

```bash
python3 tools/private_upgrade_1049.py --original-api /private/starfarer.api.jar --original-obf /private/starfarer_obf.jar --previous-exe /private/api_linux_1048 --current-exe /private/api_linux_1049
```
