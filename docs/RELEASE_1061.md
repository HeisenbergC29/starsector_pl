# Starsector PL ASCII 1.0.61 — Holownik Bram: skladnia, czasy przelotu i audyt API

**Gra:** Starsector 0.98a-RC8. **Instalator:** Windows x64. **Wersja 1.1 wciaz nieukonczona.**

## Zakres oryginalnych tekstow Java

Pelny audyt oryginalnego `starfarer.api.jar` klasy `com.fs.starfarer.api.impl.campaign.intel.misc.GateHaulerIntel` potwierdzil **49 instrukcji `ldc`/`ldc_w` wykorzystujacych 33 angielskie literaly** (30 istniejacych oraz 3 brakujace w poprzedniej mapie). Sprawdzono metody `addBulletPoints`, `createSmallDescription`, `getName`, `getSortString` oraz `getIntelTags`. Zrodlo testu: `tools/audit_original_jvm_1061.py`; wyniki: `docs/JVM_AUDIT_1061.json`. Oryginalne komercyjne JAR nie sa czescia wydania.

- **25 historycznych rekordow** o poprzednich statusach `DRAFT_ONLY_NOT_INSTALLED` / `OPTIONAL_PATCHER_NOT_GAME_TESTED` recenzowano pod katem rzeczywistego miejsca uzycia, kontekstu i jezyka. To recenzje offline — nie test natywnego UI Windows. Wazne: stary patcher Go nie uzywa kolumny `status` do odfiltrowania mapowan; status opisuje poziom weryfikacji, a nie warunek ich instalowania.
- **15 istniejacych tlumaczen** poprawiono, w tym laczniki dynamicznych opisow czasu i celu, odmiane statusow przy rzeczowniku `Holownik` oraz opisy przybycia i odlotu.
- **3 nowe mapowania**, ograniczone do tej jednej klasy: `day` -> `dzien`, `days` -> `dni` oraz stale pojedyncze ` ` -> `. `. Ten ostatni przypadek zostal zweryfikowany poprzez indeks konstanty w oryginalnej klasie i **jedno** jej uzycie, w `createSmallDescription` pod offsetem 551. Inne puste ciagi z tej klasy pozostaja nietkniete.

## Poprawne dynamiczne zdania

Przyklady wypowiedzi gry w zapisie ASCII:

| Przed | Po |
| --- | --- |
| `Estimated %s ` + `days` + ` to complete transit` | `Szacowany czas przelotu: 5 dni` |
| `Estimated %s ` + `day` + ` for transit` | `Szacowany czas przelotu: 1 dzien` |
| `The gate hauler has arrived to the ` + nazwa + ` ` + `and is decelerating...` | `Holownik Bram dotarl do celu: uklad Askonia. Wyhamowuje, aby wejsc na orbite postojowa.` |
| `Status: dormant` | `Stan: uspiony` |
| `Status: operational` | `Stan: gotowy` |

Dwa opisy pelnego przelotu skladaja teraz ilosc dni i nazwe miejsca przez strukture `Szacowany czas ...: %s dzien/dni. Cel: [nazwa]. Po przybyciu ...`, nie wymagajac odmiany dynamicznej nazwy. Testy obejmuja **93 warianty** roznych ilosci (`1`, `2`, `5`, `11`, `21`, `22`) i nazw obiektow. Nie zmieniono kodu, progow czasowych ani warunkow rozgrywki.

## Nowy stan recenzji historycznego API

| Miernik | 1.0.60 | 1.0.61 |
| --- | ---: | ---: |
| Historyczne wiersze API poddane recenzji offline | 391 | **416** |
| Historyczne wiersze API do dalszej recenzji | 3267 | **3242** |
| Liczba wierszy mapy API | 5309 | **5312** |
| Skuteczne podmiany API wg dotychczasowej metodologii | 5307 | **5310** |
| Gettery JVM pozostale do oceny | 186 | 186 |
| Surowe dynamiczne zmienne plciowe w `rules.csv` | 1953 | 1953 |
| Dialogi z tymi zmiennymi | 1006 | 1006 |

Nowa recenzja 25 rekordow jest dopisana do niezmiennego rejestru 391 w `docs/API_SEMANTIC_REVIEW_1061.json`; ich znaczniki sa przeliczane z biezacej mapy, a kazdy poprzedni `row_sha256` musi nadal wystepowac bez zmian. Nowych trzech literalow **nie** wliczono do 3658 historycznych. Szczegolowy rejestr 25 par oryginalnego i sprawdzonego tekstu, statusu oraz odcisku SHA-256: `docs/GATE_HAULER_REVIEW_1061.json`.

## Testy offline i rzeczywiste oryginalne JAR

- Mapy starej i nowej wersji sprawdzono kryptograficznie: stara `963634daecdbd86e007091f90788367d826ade750d4b16bf335dd88ce439b724`, nowa `9efa72c67950a3f92ad776ad4c92172fa050f54d88556c8f159c3b1bec91f11b`.
- Oryginalny `starfarer.api.jar`: SHA-256 `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`. **49 uzyc** polskich fragmentow powiazano z oryginalnymi instrukcjami, w tym **5 singular i 5 plural** dla czasu.
- Swieza instalacja 1.0.61 oraz aktualizacja **1.0.60 -> 1.0.61** na dwoch oryginalnych komercyjnych JAR: wyniki **bajtowo identyczne**. Zmieniona dokladnie **jedna** klasa `.class` (`GateHaulerIntel`), a offsety i rodzaje wykonywalnych instrukcji JVM pozostaly identyczne. Wynikowy API SHA-256 `338c2a172e291df8adeeb8d3fd68de153d4bfb30de241b4cfa44166d76d69d04`. OBF pozostaje `85b4b2afb4f6175cabedf1ef5cb9976e0097e39403dff0fc18c728c9d48894e1`.
- Ponowna instalacja jest no-op; opcje przywracania odtwarzaja oryginalne JAR bajtowo; uszkodzony JAR jest odrzucany bez nadpisywania. Raport `docs/PRIVATE_UPGRADE_1061.json`, wykonywalny test `tools/private_upgrade_1061.py`.
- `go test ./...`, `go vet ./...` w patcherach OBF, API i instalatorze: PASS. Cross-build **3 PE32+ Windows x64**: PASS.
- Walidacja CSV: `rules.csv` **11 107 rekordow i 7371 prawidlowych opcji**. **Wszystkie 870 plikow danych** maja niezmienne sumy; brak zmian NPC, questow, skryptow i warunkow. 12 niepoprawnych mapowan/gramatyk zostalo odrzuconych; 6 sfalszowanych kontraktow pakietu takze.
- ZIP: **873 wpisy**, 870 plikow `data`, poprawne CRC, oba patchery osadzone dokladnie raz w instalatorze, brak komercyjnych JAR.

## Reprodukcja

Po wykonaniu `python3 tools/restore_snapshot.py` i `tools/apply_1013.py`...`tools/apply_1060.py` w podanej kolejnosci:

```sh
python3 tools/apply_1061.py worktree
python3 tools/verify_1061.py worktree
python3 tools/test_1061.py worktree
python3 tools/test_package_contract_1061.py worktree
python3 tools/build_review_1061.py worktree --record docs/GATE_HAULER_REVIEW_1061.json --previous docs/API_SEMANTIC_REVIEW_1055.json --ledger docs/API_SEMANTIC_REVIEW_1061.json
python3 tools/check_release_gates_1061.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/RELEASE_GATES_1060.json --prior-semantic docs/API_SEMANTIC_REVIEW_1055.json --semantic docs/API_SEMANTIC_REVIEW_1061.json
python3 tools/test_release_gates_1061.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/RELEASE_GATES_1060.json --prior-semantic docs/API_SEMANTIC_REVIEW_1055.json --semantic docs/API_SEMANTIC_REVIEW_1061.json
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
python3 tools/package_1061.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.61_MINIMALNY.zip
```

Tylko lokalnie, z oryginalnymi JAR u wlasciciela:

```sh
python3 tools/audit_original_jvm_1061.py --jar /PRIVATE/starfarer.api.jar --worktree worktree
python3 tools/private_upgrade_1061.py --jars /PRIVATE/starsector-core --worktree worktree
```

**Nie wysylaj oryginalnych komercyjnych JAR do publicznego repozytorium.** Dalsze prace: pozostale 3242 historyczne wiersze API, 186 getterow, 1953 dynamiczne zmienne w 1006 dialogach, kompletne sprawdzenie wszystkich tekstow oraz test interfejsu w uruchomionej grze Windows. **Wydanie 1.1 pozostaje niewydane.**
