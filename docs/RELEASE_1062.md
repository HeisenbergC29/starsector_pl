# Starsector PL ASCII 1.0.62 — pirackie bazy: porozumienia i techniczne kategorie

**Gra:** Starsector 0.98a-RC8. **Paczka:** Windows x64. **Cel 1.1 nadal NIEUKONCZONY.**

## Potwierdzony problem i realne poprawki

Oryginalna klasa `com.fs.starfarer.api.impl.campaign.intel.bases.PirateBaseIntel` zawiera **36** historycznie mapowanych angielskich napisów. Zweryfikowano ich rzeczywiste wykorzystanie w oryginalnym JAR, odnalaziono **2** dodatkowe widoczne napisy i zbadano w sumie **42 wywołania `ldc` / 38 unikatowych tekstów**. Nie są to wyłącznie poszukiwania ciągów tekstowych w pliku: każdemu przyporządkowano metodę, offset i numer stałej JVM (`docs/JVM_AUDIT_1062.json`).

Po przeglądzie 31 wcześniejszych mapowań DRAFT/OPTIONAL zastosowano **5** napraw:

| Stała oryginalnego JVM | Poprzednio w PL ASCII | 1.0.62 |
| --- | --- | --- |
| `Agreement broken` | `Porozumienie zerwane` | `Zerwano porozumienie` |
| `Agreement dissolved` | `Porozumienie rozwiazane` | `Rozwiazano porozumienie` |
| `Agreement made with base commander` | `Zawarto porozumienie z dowodca bazy` | `Porozumienie zawarte z dowodca bazy` |
| `Fleet log` | `Dziennik floty` | **`Fleet log`** (techniczny identyfikator kategorii) |
| `Colony threats` | `Zagrozenia dla kolonii` | **`Colony threats`** (techniczny identyfikator kategorii) |

Dwa **NOWE** mapowania w tej klasie: `Agreement` -> `Porozumienie` (kolorowane słowo informacji o zawarciu układu) oraz `agreement` -> `porozumienie` (dynamiczny parametr i jego wyróżnienie w podpowiedzi). `Porozumienie` występuje dokładnie raz w przetłumaczonym zdaniu i może zostać podświetlone; `Masz porozumienie z dowodca bazy...` otrzymuje poprawny dynamiczny argument.

### Dlaczego nie tłumaczymy kategorii w tym miejscu

Oryginalny JVM wywołuje `Set.contains("Fleet log")` w `getSortString()` (`ldc`, offset 4) oraz dwukrotnie `Set.add("Colony threats")` w `getIntelTags()` (offsety 59 i 81). To wartości kategorii używane przez kod, a nie zwykłe etykiety UI. Ich niezależne tłumaczenie zrywa kompatybilność z innymi producentami/odbiorcami kategorii. Dla pełnej polonizacji trzeba osobno sprawdzić centralne renderowanie widocznych nazw kategorii, pozostawiając klucze techniczne bez zmian. Nie twierdzimy, że przywrócenie angielskiego technicznego klucza jest tłumaczeniem widocznym dla gracza.

Zachowano wszystkie pozostałe mapowania, w tym wcześniejsze 4 rekordy `REVIEWED_VISIBLE_UI_1004` i 1 `VERIFIED_TOOLTIP_CALLSITE_1013` bez zmian. Dodane `Agreement` nie jest tożsame z technicznym `DEAL_MADE_PARAM`.

## Recenzje historyczne

Wśród 36 dotychczasowych mapowań klasy było dokładnie **31** w stanie DRAFT/OPTIONAL. Każdy z tych wpisów został przejrzany na podstawie konkretnych użyć oryginalnego JVM oraz zapisany w `docs/PIRATE_BASE_REVIEW_1062.json` (oryginalna/nowa wartość i status, SHA-256 wierszy i angielskich stałych). Przed aktualizacją rejestr zawierał **416** unikatowych przeglądów, po dodaniu **447 z 3658** — pozostaje **3211**. Dwa nowo odkryte literały nie są pozycjami historycznymi, zatem nie są doliczane do 447. Rejestr zbiorczy `docs/API_SEMANTIC_REVIEW_1062.json` chroni niezmienność wszystkich 416 starych odcisków.

### Obszary wymagające dalszej analizy

Nie rozwiązano w tym wydaniu fragmentu kodu `PirateBaseIntel.createSmallDescription()`, który łączy dynamiczną wartość `FactionAPI.getDisplayNameHasOrHave()` z przetłumaczonym zwrotem `zalozyli baze w`. Może to skutkować mieszaniem angielskiego `has/have` z polskim zdaniem — wymaga audytu źródła dynamicznej wartości i kontekstu dalszych wywołań. Ponadto złożone tytuły baz (`[prefix] Baza - ...`) wymagają osobnej recenzji odmiany i spójności wszystkich 8 wariantów. Nie dokonano niezatwierdzonych zamian globalnych ani zmian identyfikatorów klas/skryptów.

## Dowody integralności

- Oryginalny `starfarer.api.jar`: SHA-256 `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`. Nieudostępniany i niecommitowany.
- Mapa API przed: **5312** wierszy, SHA-256 `9efa72c67950a3f92ad776ad4c92172fa050f54d88556c8f159c3b1bec91f11b`.
- Mapa API po: **5314** wierszy, SHA-256 `1f85680ff856b858f2f4db342aa98754c085a35bec6e9d0538113a55f9471f01`.
- OBF: niezmieniona. Wszystkie **870** plików `mod/data`: byte-for-byte niezmienione; `rules.csv` SHA-256 `4fcf72e3aad0a0c72bac3bea021a311b36f12c4d201d4dcf9b9c7edf2eeb0e04`; 11107 reguł, 7371 opcji dialogowych, 0 błędów parsera.
- Java original-JAR upgrade: **świeża 1.0.62 = aktualizacja 1.0.61 → 1.0.62**, wynik API SHA-256 `f8906cb9079dd6e4e56620550d5ed4021716a226bc6a0aa0ab1a198d23ddf7e3`; wyłącznie `PirateBaseIntel.class` zmieniona. Opcody i offsety JVM identyczne. OBF SHA niezmienione `85b4b2afb4f6175cabedf1ef5cb9976e0097e39403dff0fc18c728c9d48894e1`. Reinstall no-op, restore bajtowo identyczne, uszkodzony JAR odrzucony.
- 18 kombinacji podpowiedzi o porozumieniu (wysokie/niskie `Agreement`, 3 wartości kredytów i 3 procenty); 12 celowo wadliwych mapowań odrzuconych; 6 wadliwych kontraktów paczki odrzuconych.
- `go test ./...` i `go vet ./...` w API, OBF i instalatorze: PASS; Windows amd64 cross-build trzech PE32+ EXE PASS.
- Archiwum lokalne `Starsector_PL_ASCII_0.98a_RC8_1.0.62_LOCAL.zip`: 19 374 060 B, SHA-256 `69250dcc7c600bf89dc473cc2dfae6fb3a295872fc424714231864b81391496c`, 873 wpisy, CRC poprawne, oryginalne komercyjne JAR niezałączone. Końcowy artefakt GitHub Actions wymaga osobnego sprawdzenia.

## Reprodukcja

Po `restore_snapshot.py` (snapshot 1.0.12) i nałożeniu `tools/apply_1013.py` do `tools/apply_1061.py`:

```sh
python3 tools/apply_1062.py worktree
python3 tools/verify_1062.py worktree
python3 tools/test_1062.py worktree
python3 tools/test_package_contract_1062.py worktree
python3 tools/build_review_1062.py worktree --record docs/PIRATE_BASE_REVIEW_1062.json --previous docs/API_SEMANTIC_REVIEW_1061.json --ledger docs/API_SEMANTIC_REVIEW_1062.json
python3 tools/check_release_gates_1062.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/RELEASE_GATES_1061.json --prior-semantic docs/API_SEMANTIC_REVIEW_1061.json --semantic docs/API_SEMANTIC_REVIEW_1062.json
python3 tools/test_release_gates_1062.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/RELEASE_GATES_1061.json --prior-semantic docs/API_SEMANTIC_REVIEW_1061.json --semantic docs/API_SEMANTIC_REVIEW_1062.json
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
python3 tools/package_1062.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.62_MINIMALNY.zip
```

Test z oryginalnym `starfarer.api.jar` prywatnie: `python3 tools/audit_original_jvm_1062.py --jar /PRIVATE/starfarer.api.jar --worktree worktree`, `python3 tools/private_upgrade_1062.py --jars /PRIVATE/original_jars --worktree worktree`. Nie commitować komercyjnych plików ani ich zawartości.

**Do celu 1.1 pozostają:** **3211** historycznych wpisów API, **186** wywołań getterów Java do sprawdzenia, **1953** surowe zmienne płciowe w **1006** rekordach dialogów, dalszy audyt kompletności oraz **NATYWNY TEST gry Windows**. Offline i CI nie oznaczają, że polska wersja jest pełna. 1.1 NIE GOTOWA.
