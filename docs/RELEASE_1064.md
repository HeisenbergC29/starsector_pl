# Starsector PL ASCII 1.0.64 — inspekcje Hegemonii i bazy Ścieżki Ludda

**Gra:** Starsector 0.98a-RC8. **Wydanie:** Windows x64, ASCII. **Wersja docelowa 1.1 nadal NIEUKOŃCZONA.**

## Rzeczywiste zmiany

Sprawdzono w oryginalnej, niezmodyfikowanej grze **dwie klasy Java API**:

- `com.fs.starfarer.api.impl.campaign.intel.inspection.HegemonyInspectionIntel`: 28 istniejących pozycji mapy, 24 historyczne DRAFT/OPTIONAL, oryginalny JVM **56** odwołań `ldc` do **45** różnych tekstów.
- `com.fs.starfarer.api.impl.campaign.intel.bases.LuddicPathBaseIntel`: 28 pozycji, 24 historyczne DRAFT/OPTIONAL, oryginalny JVM **94** odwołania do **89** różnych tekstów.

Razem **48 nowych recenzji semantycznych** (oryginalne odwołania JVM, składnia i znaczenie), bez podwójnego zaliczania 482 starszych. Łączny audyt historyczny: **530/3658** (wciąż **3128** do recenzji). Nie oznacza to pełnej polonizacji żadnej z wymienionych funkcji ani przetestowania jej w interfejsie gry.

Zmieniono dokładnie **9 wcześniej istniejących fragmentów polskich** w klasowych mapowaniach API:

| Klasa | Tekst oryginalny / kontekst | Nowe polskie tłumaczenie / cel |
| --- | --- | --- |
| HegemonyInspectionIntel | `Colony threats` | `Colony threats` — **techniczny klucz Set.add**, nie zmieniać |
| HegemonyInspectionIntel | `The authorities at ` | `Decyzja wladz kolonii: ` — nazwa kolonii pozostaje bez odmiany |
| HegemonyInspectionIntel | ` will comply with the inspection. ` | ` - zgoda na inspekcje. ` |
| HegemonyInspectionIntel | `Operations at %s disrupted` | `Zaklocono dzialalnosc: %s` — zachowany parametr `%s` |
| HegemonyInspectionIntel | ` forces arrive in-system and encounter resistance` | `: oddzialy dotarly do ukladu i napotkaly opor` |
| LuddicPathBaseIntel | `Colony threats` | `Colony threats` — **techniczny klucz Set.add**, nie zmieniać |
| LuddicPathBaseIntel | `Fleet log` | `Fleet log` — **techniczny klucz Set.contains**, nie zmieniać |
| LuddicPathBaseIntel | `The base serves to provide material support ...` | `Baza zapewnia wsparcie materialne aktywnym komorkom Sciezki Ludda na pobliskich koloniach, umozliwiajac im ` |
| LuddicPathBaseIntel | `You do not know of any active pather cells ...` | `Nie wiadomo, czy baza wspiera jakiekolwiek aktywne komorki Sciezki Ludda.` |

Trzy oryginalne ciągi są wykorzystywane jako klucze porównania/dodawania kategorii. Miejsca w oryginalnym JVM: HegemonyInspectionIntel `getIntelTags`, `ldc` offset 17 → `Set.add` offset 20; LuddicPathBaseIntel `getIntelTags`, offset 79 → `Set.add` offset 82; `getSortString`, offset 4 → `Set.contains` offset 7. To nie są zwykłe etykiety interfejsu.

**Przykładowe poprawne kompozycje ASCII:** `Decyzja wladz kolonii: Jangala - zgoda na inspekcje. Na pewno wykryje wszystkie uzywane obecnie rdzenie SI.`; `Zaklocono dzialalnosc: Chicomoztoc`; `Hegemonia: oddzialy dotarly do ukladu i napotkaly opor`.

**Ograniczenie:** `FactionAPI.getDisplayNameHasOrHave()` i `getDisplayNameIsOrAre()` nadal zwracają dynamiczne angielskie czasowniki w innych składanych komunikatach. Nie wolno ich „naprawiać” samą zmianą sąsiednich polskich fragmentów. Wymagają osobnego audytu JVM.

## Integralność i wyniki testów

- API: mapa nadal **5314** unikatowych par `(source_class, english_literal)`, w dwóch klasach 56 pozycji, **48** historycznych statusów zatwierdzonych. Mapa OBF i wszystkie **870** plików `mod/data` bez zmian, w tym **11 107** rekordów `rules.csv` i **7371** poprawnych opcji dialogowych.
- Oryginalna gra: `starfarer.api.jar` SHA-256 `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`. W oryginalnym JVM potwierdzono **150** odwołań i wszystkie **56** mapowanych stałych; 3 chronione argumenty `Set.add`/`Set.contains`.
- Testy polskich kompozycji: **25/25** PASS, 12/12 celowo błędnych wariantów odrzucono. Testy kontraktu paczki: 6 błędnych wariantów odrzucono.
- Prywatny test instalacji na oryginalnych komercyjnych JAR: **fresh 1.0.64 = upgrade 1.0.63 → 1.0.64** bajt w bajt. Zmodyfikowane są **dokładnie 2 klasy Java**; instrukcje JVM oraz ich offsety pozostają identyczne; ponowna instalacja no-op, restore oryginałów bajtowo, uszkodzony JAR odrzucony. Raport: `docs/PRIVATE_UPGRADE_1064.json`.
- `GO111MODULE=off go test ./...` i `go vet ./...` dla OBF, API i instalatora: **PASS**. Cross-kompilacja trzech programów Windows x64: **PASS**.
- Paczka: 873 wpisy ZIP, 870 plików danych, poprawne CRC, dwa patchery osadzone dokładnie raz w instalatorze, bez oryginalnych komercyjnych JAR. Weryfikator odmawia wydania przy niezgodnym mapowaniu.

## Pliki dowodowe i odtworzenie

`tools/apply_1064.py`, `tools/verify_1064.py`, `tools/test_1064.py`, `tools/audit_original_jvm_1064.py`, `tools/build_review_1064.py`, `docs/INSPECTION_PATHBASE_REVIEW_1064.json`, `docs/JVM_AUDIT_1064.json`, `docs/API_SEMANTIC_REVIEW_1064.json`, `docs/PRIVATE_UPGRADE_1064.json`. Archiwum poprzednich bramek: `docs/RELEASE_GATES_1063.json`; aktualne 1.1: `docs/RELEASE_GATES_11.json`.

Po przywróceniu migawki źródeł 1.0.12 i zastosowaniu wszystkich nakładek `apply_1013.py`–`apply_1063.py`:

```sh
python3 tools/apply_1064.py worktree
python3 tools/verify_1064.py worktree
python3 tools/test_1064.py worktree
python3 tools/test_package_contract_1064.py worktree
python3 tools/build_review_1064.py worktree --record docs/INSPECTION_PATHBASE_REVIEW_1064.json --previous docs/API_SEMANTIC_REVIEW_1063.json --ledger docs/API_SEMANTIC_REVIEW_1064.json
python3 tools/check_release_gates_1064.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/RELEASE_GATES_1063.json --prior-semantic docs/API_SEMANTIC_REVIEW_1063.json --semantic docs/API_SEMANTIC_REVIEW_1064.json
python3 tools/test_release_gates_1064.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/RELEASE_GATES_1063.json --prior-semantic docs/API_SEMANTIC_REVIEW_1063.json --semantic docs/API_SEMANTIC_REVIEW_1064.json
(cd worktree && sh build_windows.sh)
python3 tools/package_1064.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.64_MINIMALNY.zip
```

Oryginalne komercyjne JAR są wyłącznie do prywatnej weryfikacji i nie są częścią repozytorium: `python3 tools/audit_original_jvm_1064.py --jar /PRIVATE/starfarer.api.jar --worktree worktree` oraz `python3 tools/private_upgrade_1064.py --jars /PRIVATE/starsector-core --worktree worktree`.

## Nadal otwarte dla 1.1

**3128** historycznych wpisów API, **186** kontekstów getterów Java, **1953** surowe dynamiczne znaczniki płci w **1006** dialogach (nie wszystkie są błędami), pełna kontrola pozostałych tekstów oraz **rzeczywiste uruchomienie i sprawdzenie GUI/rozgrywki na Windows**. Nie uznawać sukcesu CI za test graficzny. Brak wydania 1.1.
