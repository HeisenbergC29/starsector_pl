# Starsector PL ASCII 1.0.57 — polska skladnia gestow w 70 dialogach

**Gra:** Starsector 0.98a-RC8. **Wersja:** 1.0.57, robocze wydanie Windows x64. **Cel 1.1: nadal OTWARTY.**

## Zmiany tlumaczen

Na podstawie rzeczywistego `rules.csv` 1.0.56 poprawiono **70 nowych, wczesniej nierecenzowanych dialogow**. Dotycza **74** idiomatycznych zwrotow opisujacych ruch glowy, dloni, ramion, oczu, brwi, warg i gestow postaci. Usunieto **76** zbednych odniesien do `$hisOrHer`, w tym po dwa w dwoch opisach chowania glowy w dloniach. Przyklady: `przewraca $hisOrHer oczami` -> `przewraca oczami`, `krzyzuje $hisOrHer ramiona` -> `krzyzuje ramiona`, `kreci glowa $hisOrHer` -> `kreci glowa`, `sklada $hisOrHer dlonie` -> `sklada dlonie`.

15 scisle wyliczonych wzorcow nie stosuje sie do komentarzowych regulek o ID zaczynajacym sie od `#`. Brak wczesniej poprawionych ID: **363** unikatowe rekordy 1.0.34–1.0.56 sa chronione. W publicznym `docs/RULES_REFLEXIVE_REVIEW_1057.json` zapisano wszystkie pelne teksty oryginalne i poprawione, ID, 74 wzorcowe podmiany, liczniki oraz SHA-256 obu wersji kazdego pola. Kazda poprawka przechodzi przez scisly test ID, calego oryginalnego tekstu i odpowiedniego wzorca.

Zmieniono **wylacznie** kolumne `text` dokladnie 70 rekordow `data/campaign/rules.csv`. Po odwróceniu 70 zmian odzyskano oryginalny 1.0.56 `rules.csv` **bajt po bajcie**, bez ponownej serializacji pliku CSV. Nie zostaly zmienione identyfikatory, skrypty, `conditions`, `trigger`, `options`, `notes`, kod JVM ani pozostale **869** plikow danych. Poprzednie 7371 opcji dialogowych zachowalo poprawna skladnie parsera.

**Hash rules.csv 1.0.56:** `a08330e67de037fc0df66447c039ec7ac6792340405d2983c04e31f2bfef4810`.

**Hash rules.csv 1.0.57:** `693b874b6738d792bbf5b74a9e247e594c607c1834a2822823a228511a311f6c`.

## Stan audytu

| Miernik | 1.0.56 | 1.0.57 |
| --- | ---: | ---: |
| Zrecenzowane offline unikatowe reguly `rules.csv` | 363 | **433** |
| Usuniete problematyczne zmienne plciowe od wczesniejszych wydan | 530 | **606** |
| Pozostale wystapienia dynamicznych zmiennych plciowych | 2165 | **2089** |
| Rekordy z co najmniej jednym surowym znacznikiem plciowym | 1029 | **1028** |
| Historyczne API sprawdzone offline | 391/3658 | **391/3658** |
| Wywolania getterow Java wymagajace analizy | 186 | **186** |

Nie kazdy z 2089 pozostalych znacznikow jest bledem. Zadna zmienna nie zostala usunieta globalnie ani z technicznych pol CSV.

## Testy

- Odtworzenie 1.0.56 z dziewieciu czesci snapshotu 1.0.12 i 44 overlayow: PASS; porownanie **872/872** plikow z oficjalna paczka 1.0.56: bajtowo identyczne.
- Precyzyjny test 70 ID i 74 podmian oraz odwrocenie zmian do oryginalnego rules.csv: PASS; 10 celowo uszkodzonych planow lub plikow **prawidlowo odrzuconych**.
- 869 pozostalych danych: niezmienne sumy SHA-256. Zmienna CSV tylko w kolumnie `text`; zachowane 11 107 rekordow i 7371 opcji.
- Mapa API 5298 wierszy (5296 podmian), mapa OBF 3537 podmian: **niezmienione**. Patcher API i instalator maja nowy numer 1.0.57. Wszystkie wykonywalne instrukcje JVM bez nowych modyfikacji.
- `GO111MODULE=off go test ./...` i `go vet ./...` w OBF oraz API: PASS. Windows x64 cross-build patcherow i instalatora: PASS.
- Oryginalne komercyjne JAR: **fresh 1.0.57 = upgrade 1.0.56 -> 1.0.57**, ponowne zastosowanie no-op, odmowa uszkodzonego API, restore do oryginalnych SHA. Raport `docs/PRIVATE_UPGRADE_1057.json` oraz powtarzalny prywatny test `tools/private_upgrade_1057.py`.
- Testy bramek wydania 1.1: 10 sfalszowanych stanow ukonczenia odrzuconych; testy kontraktu paczki: 5 falszywych metadanych odrzuconych.
- Paczka Windows ZIP: **873 wpisy**, 870 plikow danych, poprawne CRC, trzy wlasne pliki dystrybucyjne. Brak oryginalnych komercyjnych JAR.

**Paczka zbudowana lokalnie:** `Starsector_PL_ASCII_0.98a_RC8_1.0.57_MINIMALNY.zip` (18 517 823 B), SHA-256 `fd977ded522cecb01e63cfac7eac222b2cd0d22388e4ba18289f6f7033e54ea8`. Jesli artefakt GitHub Actions zostanie ponownie zbudowany, porownac jego wlasne SHA-256; kompresja i toolchain moga wytworzyc inny plik ZIP przy takiej samej zawartosci.

## Odtworzenie i wydanie

Po `python3 tools/restore_snapshot.py` i zastosowaniu `tools/apply_1013.py` do `tools/apply_1056.py` kolejno:

```sh
python3 tools/apply_1057.py worktree
python3 tools/verify_1057.py worktree
python3 tools/test_1057.py worktree
python3 tools/test_package_contract_1057.py worktree
python3 tools/check_release_gates_1057.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/RELEASE_GATES_1056.json
python3 tools/test_release_gates_1057.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/RELEASE_GATES_1056.json
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
python3 tools/package_1057.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.57_MINIMALNY.zip
```

**Oryginalne JAR testuj wylacznie prywatnie** z `python3 tools/private_upgrade_1057.py --jars /PRIVATE/starsector-core --repo . --out /PRIVATE/1057_upgrade.json`. Nie commituj JAR, binariow ani logow ze sciezkami systemowymi.

## Nadal otwarte dla 1.1

Pozostalo **2089** surowych wystapien zmiennych plciowych w **1028** rekordach (wymagaja sprawdzenia kontekstu), **3267** historycznych wpisow API do pelnej recenzji, **186** niedokonczonych wywolan getterow JVM oraz pelny audyt widocznych tekstow. **Natywny gameplay na Windows NIE zostal przeprowadzony.** Kompilacja Windows x64 i testy offline nie stanowia potwierdzenia, ze wszystkie teksty sa poprawne w uruchomionej grze. Wersja 1.1 pozostaje NIEWYDANA.
