# Starsector PL ASCII — polonizacja Starsector 0.98a-RC8

**Stan (1.0.29):** rozwijana polonizacja, docelowe wydanie **1.1** NIE jest jeszcze ukończone.

Repozytorium ma umożliwić innemu agentowi odtworzenie i kontynuowanie pracy bez historii rozmowy.

**Aktualny stan roboczy: 1.0.29** (snapshot bazowy 1.0.12 + overlaye 1013–1029; 23 nowe etykiety OBF w 21 klasach i 7 API w 6 klasach; 870 danych bez zmian). Cel 1.1 jeszcze nieukonczony.

## Zacznij tutaj
1. [AGENTS.md](AGENTS.md) — niezmienne zasady pracy i lokalizacji.
2. [docs/STATUS.md](docs/STATUS.md) — prawdziwy stan, znane błędy i następne kroki.
3. [docs/SOURCES.md](docs/SOURCES.md) — oryginalne pliki, sumy SHA-256 i odtwarzanie środowiska.
4. [docs/BUILD.md](docs/BUILD.md) — kompilacja i testy patcherów.
5. [docs/TEST_109_CRASH.md](docs/TEST_109_CRASH.md) — błąd zgłoszony podczas testu 1.0.9.

## Zakres
- Polonizujemy **wszystkie pola wyświetlające tekst graczowi**: dane, dialogi, kod OBF/API i teksty dynamiczne.
- Tłumaczymy nazwy mające ustalone polskie odpowiedniki, pseudonimy i skróty z przetłumaczonym rozwinięciem.
- Nie tłumaczymy imion/nazwisk osób ani technicznych ID, warunków, skryptów, parametrów i odwołań.
- Polski ASCII (bez znaków diakrytycznych) w zasobach gry, dopóki nie zostanie potwierdzona obsługa znaków.
- Każdą zmianę weryfikujemy względem źródeł. Samo przejście testu instalatora NIE dowodzi ukończenia lokalizacji.

## Prawo i bezpieczeństwo
**Nie dodawać oryginalnych JAR, pełnych zasobów komercyjnej gry ani logów z prywatnymi ścieżkami użytkownika do publicznego GitHuba.** Użytkownik ma oryginały w archiwach przekazanych prywatnie. Do repo należą źródła narzędzi, mapy przekładu, praca własna, instrukcje i testy.

## Test gry
Zgłoszony crash na 1.0.9 został odtworzony poprzez analizę `rules.csv` i bajtkodu parsera. Ścieżka naprawy opisana jest w `docs/TEST_109_CRASH.md`.

Wersja 1.1 dopiero po pełnym audycie, a nie po samym wzroście liczby podmian.

## Rozwój 1.0.13
Po odtworzeniu `worktree` z archiwum 1.0.12 wykonaj `python3 tools/apply_1013.py worktree` przed kompilacja. Nowy plik `TLUMACZENIA_JAR_1013.csv` jest generowany na podstawie niezmienionej mapy `1010` (wymaganej do aktualizacji). Mapy OBF nie zmieniono. Wynik testow i SHA-256 paczki: `docs/RELEASE_1013.md`.

## Rozwój 1.0.14
Po odtworzeniu migawki wywołaj kolejno `python3 tools/apply_1013.py worktree` i `python3 tools/apply_1014.py worktree`. Historia obu map 1013/1014 jest zachowana dla aktualizacji starszych instalacji. Go test zawiera regresję dla nie-ASCII w literałach z oryginalnego JAR. Szczegóły: [docs/RELEASE_1014.md](docs/RELEASE_1014.md).

## Rozwój 1.0.15
Po odtworzeniu bazy wykonaj po kolei `python3 tools/apply_1013.py worktree`, `python3 tools/apply_1014.py worktree`, `python3 tools/apply_1015.py worktree`. Zapisano wszystkie historyczne mapy do aktualizacji. Zobacz [docs/RELEASE_1015.md](docs/RELEASE_1015.md).

## Rozwój 1.0.16
Po `python3 tools/restore_snapshot.py` wykonaj po kolei `tools/apply_1013.py`, `tools/apply_1014.py`, `tools/apply_1015.py`, `tools/apply_1016.py` z argumentem `worktree`. Obie historyczne mapy OBF/API sa zachowane dla upgrade. Zobacz [docs/RELEASE_1016.md](docs/RELEASE_1016.md).

## Rozwój 1.0.17
Po odtworzeniu bazy wykonaj w kolejnosci `tools/apply_1013.py` do `tools/apply_1017.py` z argumentem `worktree`. Zweryfikowano odtwarzalnosc 1000 plikow zrodlowych. Zobacz [docs/RELEASE_1017.md](docs/RELEASE_1017.md).

## Rozwój 1.0.18
Po odtworzeniu bazy wykonaj `tools/apply_1013.py` do `tools/apply_1018.py` kolejno z argumentem `worktree`, a nastepnie `python3 tools/verify_subject_pronouns_1018.py worktree`. Inne zaimki i `Misc.STORY` wymagaja audytu. Wyniki: [docs/RELEASE_1018.md](docs/RELEASE_1018.md).

## Rozwój 1.0.19
Wykonaj kolejno `tools/apply_1013.py`–`tools/apply_1019.py` na przywroconym `worktree`, nastepnie `tools/verify_1019_tooltip.py`. Nowy niezalezny audyt 81 odwolan `Misc.STORY` i 219 wywolan metod zaimkowych: `tools/audit_dynamic_calls_1019.py`. [Raport](docs/RELEASE_1019.md).

## Rozwój 1.0.20
Po odtworzeniu snapshotu wykonaj nakladki 1013–1020 w kolejnosci i `python3 tools/verify_1020_dialogs.py worktree`. Nowy `tools/audit_exact_literals_1020.py` porownuje faktyczne `CONSTANT_String` oryginalnych JAR z mapami bez blednych escape'ow z `javap`. Wyniki: [docs/RELEASE_1020.md](docs/RELEASE_1020.md).

## Rozwój 1.0.21
Po odtworzeniu bazy uruchom kolejno overlaye 1013–1021, potem `python3 tools/verify_1021_delta.py worktree`. Audyt wzgledem prywatnego oryginalnego `data.rar` obejmuje **870 plikow**: 833 struktur, 18 CSV i 19 TXT do recenzji semantycznej. Kod: `tools/verify_source_fields_1021.py`; testy zabezpieczen: `tools/test_source_fields_1021.py`. [Szczegoly](docs/RELEASE_1021.md).

## Rozwój 1.0.22
Po przywroceniu snapshotu wykonaj overlaye 1013–1022 w tej kolejnosci, potem `python3 tools/verify_1022_names.py worktree` i `python3 tools/test_1022_names.py`. W 1.0.22 wyeliminowano 53 formy `Liga/Ligi/Lige Perseusza` i 12 `Liga/Ligi Persea` w widocznych polach tekstowych. 867 pozostalych plikow danych ma taki sam hash-drzewa jak w 1.0.21. [Dokumentacja 1.0.22](docs/RELEASE_1022.md).

## Rozwój 1.0.23
Po przywroceniu snapshotu stosuj nakladki 1013–1023 kolejno. OBF aktywna mapa `TLUMACZENIA_OBF_10123.csv`, API `TLUMACZENIA_JAR_1023.csv`. Test `python3 tools/verify_1023_ui.py worktree` potwierdza dokladnie +67 widocznych etykiet, zachowanie poprzednich map i skladanie fragmentow podpowiedzi. Zachowano aktualizacje z 1.0.22. [Dokumentacja](docs/RELEASE_1023.md).

## Rozwój 1.0.24
Po odtworzeniu snapshotu zastosuj nakladki 1013–1024 kolejno. OBF aktywna mapa `TLUMACZENIA_OBF_10124.csv`; API aktywna mapa `TLUMACZENIA_JAR_1024.csv`. `python3 tools/verify_1024_ui.py worktree` testuje dokladnie +44 nowe etykiety, nienaruszone stare tlumaczenia i brak zmiany danych; `python3 tools/test_1024_delta.py worktree` celowo narusza mapy i testuje odmowe. Z prywatnymi oryginalnymi JAR: `tools/verify_1024_callsites.py` (44 potwierdzone miejsca uzycia). [Dokumentacja](docs/RELEASE_1024.md).

## Rozwój 1.0.25
Po odtworzeniu bazy wykonaj overlaye `tools/apply_1013.py`–`tools/apply_1025.py` kolejno na `worktree`. Aktywne mapy: OBF `TLUMACZENIA_OBF_10125.csv`, API `TLUMACZENIA_JAR_1025.csv` (ta sama zawartosc co 1024). Testy: `tools/verify_1025_ui.py`, `tools/test_1025_delta.py`, odrebnie `tools/verify_1025_callsites.py` z prywatnym JAR. Audyt 3659 aktywnych DRAFT/OPTIONAL: `tools/audit_draft_boundaries_1025.py`. Zob. [docs/RELEASE_1025.md](docs/RELEASE_1025.md).

## Rozwój 1.0.26
Po odtworzeniu bazy wykonaj overlaye 1013–1026 kolejno. Aktywne mapy: OBF `TLUMACZENIA_OBF_10126.csv` (3380 podmian), API `TLUMACZENIA_JAR_1026.csv` (identyczna z 1025, 5148 podmian). Test `tools/verify_1026_ui.py` kontroluje dokladnie 86 nowych etykiet w 20 klasach i brak zmian danych; `tools/test_1026_delta.py` wymusza wykrycie pieciu niedozwolonych zmian. Z prywatnym oryginalnym JAR mozna uruchomic `tools/verify_1026_callsites.py` (106 odwolania `ldc`). Zob. [docs/RELEASE_1026.md](docs/RELEASE_1026.md).

## Rozwój 1.0.27
Po odtworzeniu bazy wykonaj overlaye 1013–1027 kolejno. Aktywne mapy: `TLUMACZENIA_OBF_10127.csv` (3421 trafien) i `TLUMACZENIA_JAR_1027.csv` (5180 wierszy, 5178 trafien). Test `tools/verify_1027_ui.py` chroni stare i nowe mapy, `tools/test_1027_delta.py` sprawdza 14 nieautoryzowanych modyfikacji, a `tools/verify_1027_callsites.py` potwierdza 140 wywolan `ldc` z oryginalnych JAR. [Dokumentacja 1.0.27](docs/RELEASE_1027.md).

## Rozwoj 1.0.28
Zastosuj kolejno overlaye `tools/apply_1013.py` do `tools/apply_1028.py` na odtworzonym `worktree`, potem `tools/verify_1028_ui.py` i `tools/test_1028_delta.py`. Aktywne mapy OBF `TLUMACZENIA_OBF_10128.csv` i API `TLUMACZENIA_JAR_1028.csv`. Oryginalne JAR mozna niezaleznie sprawdzic narzedziami `tools/verify_1028_callsites.py` oraz `tools/audit_story_1028.py`. Pozostale **81** uzyc `Misc.STORY` w **24** klasach nie zostalo globalnie zmienione (69 bezposrednio zestawia sie z `point/points`). [Dokumentacja](docs/RELEASE_1028.md).

## Rozwoj 1.0.29

30 nowych klasowo ograniczonych podmian Java UI (OBF 23, API 7); 43 uzycia `ldc` zweryfikowane na oryginalnych bibliotekach. Pełen raport: [docs/RELEASE_1029.md](docs/RELEASE_1029.md). Odtworzenie: po overlay 1028 uruchom `python3 tools/apply_1029.py worktree`, nastepnie `python3 tools/verify_1029_ui.py worktree`, `python3 tools/test_1029_delta.py worktree`, walidator opcji rules i `sh worktree/build_windows.sh`. 1.1 nadal nieukonczona, test gry na Windows niewykonany.

## Postep do 1.1: audyt dynamicznych tekstow 1030 (bez nowego wydania)

Na oryginalnych i spolonizowanych bibliotekach 1.0.29 ponownie zweryfikowano 81 uzyc `Misc.STORY`, 24 klasy oraz techniczna kolizje stalej `her` miedzy dwoma metodami. Stworzono narzedzia i testy tylko do odczytu, a takze kolejke 3659 starszych tlumaczen API do recenzji semantycznej. Nowe bramki akceptacji opisano w [docs/RELEASE_GATES_11.json](docs/RELEASE_GATES_11.json). Wyniki: [docs/DYNAMIC_AUDIT_1030.md](docs/DYNAMIC_AUDIT_1030.md) oraz [docs/SEMANTIC_AUDIT_1030.md](docs/SEMANTIC_AUDIT_1030.md). **Najnowsza paczka 1.0.29 pozostaje bez zmian. To nie jest ukonczona 1.1.**

### Audyt pominiętych zasobow (bez nowej paczki, etap 1030)

Z oryginalnego `data.rar` sklasyfikowano **529** plikow niepodmienianych przez 870 plikow lokalizacji. 23 nazwy kadlubow są identyczne ze spolonizowana tabela, 4 nazwy wariantow wymagaja indywidualnej decyzji, a 50 skryptow Java przebadano leksykalnie: 238 aktywnych literalow kodu, jeden wielowyrazowy komunikat diagnostyczny. Wynik i ograniczenia w [docs/OMITTED_DATA_1030.md](docs/OMITTED_DATA_1030.md). To nie zastępuje natywnego testu gry ani nie oznacza pelnej 1.1.
