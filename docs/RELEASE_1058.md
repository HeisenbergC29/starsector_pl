# Starsector PL ASCII 1.0.58 — poprawki wprowadzania wypowiedzi w 122 dialogach

**Gra:** Starsector 0.98a-RC8. **Wydanie:** 1.0.58, Windows x64. **Cel 1.1: NIEUKONCZONY**.

## Zakres faktycznych zmian

Przeanalizowano 122 kolejne, wczesniej niezatwierdzone rekordy `data/campaign/rules.csv`. W kazdym po czasowniku relacjonujacym wypowiedz znajdowal sie redundantny w polskim zdaniu zaimek `$heOrShe`/`$HeOrShe`. W **136** miejscach usunieto sam zaimek, np.:

- `mowi $heOrShe` -> `mowi`
- `dodaje $heOrShe` -> `dodaje`
- `odpowiada $heOrShe` -> `odpowiada`
- `pyta $heOrShe` -> `pyta`
- `krzyczy $heOrShe` -> `krzyczy`

Przeglad obejmuje tylko fragmenty wprowadzajace wypowiedz, poza cudzyslowami: nie jest to deklaracja pelnej recenzji kazdego zdania w danym rekordzie. Wzorow nie zastosowano do rekordow komentarzowych `#...`. Rekordy z **433** wczesniejszych recenzji sa wykluczone; zadnego ID nie policzono dwukrotnie.

W `docs/RULES_SPEECH_REVIEW_1058.json` znajduja sie: wszystkie 122 ID, oryginalne i poprawione **pelne pola tekstowe**, indeksy kazdej podmiany, niezmienne angielskie/polskie tokeny techniczne, hashe SHA-256 tekstow i liczniki. Mapa jest chroniona hashem SHA-256 `25b3eca81e41717fbfda5dafb36eb6f5c929eb920885ca2e55c1f340bac989c7`.

## Sprawdzona integralnosc

- Przed zmianami SHA-256 `rules.csv`: `693b874b6738d792bbf5b74a9e247e594c607c1834a2822823a228511a311f6c` (1.0.57).
- Po zmianach SHA-256 `rules.csv`: `4fcf72e3aad0a0c72bac3bea021a311b36f12c4d201d4dcf9b9c7edf2eeb0e04` (1.0.58).
- Odwrocenie dokladnie 122 pol `text` odtwarza **bajtowo identyczny** plik 1.0.57, lacznie z nieregularnosciami cytowania CSV i brakiem koncowego LF. Zachowano **11 107** rekordow.
- Nie zmodyfikowano zadnej kolumny `id`, `trigger`, `conditions`, `script`, `options`, `notes`. Wszystkie **869** pozostalych plikow danych sa bajtowo identyczne z 1.0.57.
- Weryfikator sprawdza rownosc pozostatych zmiennych, `%s/%d/%f`, znacznikow OR i cudzyslowow. Opcje dialogowe: **7371 zbadanych, 0 bledow**.
- Mapa OBF **3537** podmian w 539 klasach i mapa API **5298** wierszy, z czego **5296** skutecznych podmian w 938 klasach — **niezmienione**. Patcher API i instalator maja zaktualizowany numer wersji, bez nowych zmian wykonywalnego bajtkodu JVM.
- Dziesiec negatywnych mutacji `rules.csv`/planu i piec negatywnych mutacji kontraktu paczki zostaly prawidlowo odrzucone.

## Stan licznikow 1.1

| Miernik | 1.0.57 | 1.0.58 |
| --- | ---: | ---: |
| Unikatowe rekordy `rules.csv` zrecenzowane offline | 433 | **555** |
| Problematiczne znaczniki plci usuniete lacznie | 606 | **742** |
| Surowe dynamiczne zmienne plciowe pozostale do oceny | 2089 | **1953** |
| Rekordy nadal zawierajace takie znaczniki | 1028 | **1006** |
| Historyczne API zrecenzowane offline | 391/3658 | 391/3658 |
| Wywolania getterow Java do analizy | 186 | 186 |

Surowy placeholder w dialogu nie jest automatycznie bledem — do usuniecia potrzebna jest kontrola kontekstu.

## Testy i integracja

- Odtworzono z dziewieciu czesci snapshotu 1.0.12 i **45** nakladek 1013–1057; **872/872** pliki bazowego moda byly identyczne z finalna paczka GitHub Actions 1.0.57.
- `verify_1058.py` odtworzyl `rules.csv` 1.0.57 bajt w bajt. `test_1058.py`: 10/10 negatywnych mutacji odrzuconych; `test_package_contract_1058.py`: 5/5 nieprawidlowych stanow odrzuconych.
- `go test ./...`, `go vet ./...` — PASS dla OBF, API i instalatora. `build_windows.sh` — skompilowano 3 programy PE32+ x64.
- Na **oryginalnych** komercyjnych JAR z archiwum prywatnego: *fresh 1.0.58 = upgrade 1.0.57 -> 1.0.58*; ponowne zastosowanie no-op, odrzucenie uszkodzonego JAR i restore obu oryginalow o zadanych SHA — **PASS**. Raport `docs/PRIVATE_UPGRADE_1058.json`; powtorzenie: `tools/private_upgrade_1058.py` na prywatnym katalogu `starsector-core`.
- Lokalnie zbudowana paczka `Starsector_PL_ASCII_0.98a_RC8_1.0.58_LOCAL.zip`: 18 517 695 B, SHA-256 `8d245c4ab1516393b92f86b54e44108c65cf8eac4c7d18878123d2f04c63e6dc`, **873** wpisy, CRC PASS, **870** plikow `data/`, brak komercyjnych JAR.

Ostateczna paczka z GitHub Actions moze miec inna sume ZIP z uwagi na rozny toolchain, mimo identycznych danych i map podmian. Zweryfikowac ja oddzielnie.

## Reprodukcja w repozytorium

Po uruchomieniu `python3 tools/restore_snapshot.py` i zastosowaniu nakladek `apply_1013.py` do `apply_1057.py`:

```sh
python3 tools/apply_1058.py worktree
python3 tools/verify_1058.py worktree
python3 tools/test_1058.py worktree
python3 tools/test_package_contract_1058.py worktree
python3 tools/check_release_gates_1058.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/RELEASE_GATES_1057.json
python3 tools/test_release_gates_1058.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/RELEASE_GATES_1057.json
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
python3 tools/package_1058.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.58_MINIMALNY.zip
```

Prywatne oryginalne JAR pozostaja wylacznie lokalnie. Nie commitowac ich ani logow ujawniajacych sciezki komputera.

**1.1 NIE gotowa.** Pozostalo 1953 potencjalnych zmiennych plciowych w 1006 dialogach, 3267 historycznych wpisow API, 186 getterow JVM, pelny audyt tekstow i test gry uruchomionej natywnie na Windows. Cross-kompilacja to nie gameplay test.
