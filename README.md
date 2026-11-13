# Starsector PL ASCII — polonizacja Starsector 0.98a-RC8

**Stan (1.0.41):** rozwijana polonizacja, docelowe wydanie **1.1** NIE jest jeszcze ukończone.

Repozytorium ma umożliwić innemu agentowi odtworzenie i kontynuowanie pracy bez historii rozmowy.

**Aktualny stan roboczy: 1.0.41** (snapshot 1.0.12 + overlaye 1013–1041; OBF 3534 podmiany/539 klas bez zmian; API 5257 mapowanych wierszy/5255 trafien w 938 klasach, 77 korekt ilosciowych w 59 klasach; 870 danych identycznych z 1.0.40). Pelna 1.1 nadal OTWARTA.

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

## Wydanie 1.0.30 — poprawa skladanych dialogow i UI

Nowe literalne napisy OBF +2, API +4 i **jedna poprawka wczesniejszego skladanego zdania**. Naprawiono mieszanke `He is/She is` z polskim opisem lokalizacji poszukiwanej osoby; caly komunikat `On/Ona podobno ukrywa sie...` jest skladany gramatycznie. Poprawiono takze etykiety `Nazwa:`, `Cena: ` i licznik sekund impulsu zaklocajacego. [Dowody, testy i odtwarzanie](docs/RELEASE_1030.md). Nie oznaczac jako kompletnej 1.1: `Misc.STORY`, zaimki wspoldzielone i test Windows nadal otwarte.

## Wydanie robocze 1.0.31 — poprawka odmiany i kontrola statusow API

W `data/hullmods/SurveyingEquipment.java` usunieto bledna polska konstrukcje przy 1 jednostce i zachowano znaczniki `%s`, ASCII oraz CRLF. Mapy OBF/API i sumy spatchowanych JAR sa **niezmienione wzgledem 1.0.30**. Niezalezny audyt constant pool potwierdzil, ze status `DRAFT_ONLY_NOT_INSTALLED` jest mylacy: 1006/1008 takich wierszy zostalo zastosowanych do JAR. Ledger `docs/API_SEMANTIC_REVIEW_1031.json` dokumentuje **30** rzeczywiscie zrecenzowanych offline pozycji ze starszej puli 3658, pozostawiajac **3628** do recenzji semantycznej i nadal **3658** bez testu w grze Windows. [Pelny raport](docs/RELEASE_1031.md). Nie wydawac 1.1 bez zamkniecia [bramek](docs/RELEASE_GATES_11.json).

## Wydanie 1.0.32 — dynamiczne podpowiedzi paliwa i odmiana liczb

[Raport i testy](docs/RELEASE_1032.md). Naprawiono skladane podpowiedzi trzech zdolnosci, dotychczas laczace polski z angielskim `year's/years'`: `1 roku swietlnego` / `2 lat swietlnych`. API +6 nowych literalow, 25 poprawionych mapowanych tekstow, JAR 5223 realnych podmian/938 klas, kod metod bez zmian (potwierdzony bajt po bajcie). Rozszerzono recenzje offline z 30 do 55 pozycji; **3603** historycznych wpisow pozostaje do recenzji semantycznej, a 3664 w monitorowanych grupach do testu Windows. `Misc.STORY` i zaimki nadal blokują 1.1. Dane mod bez zmian od 1.0.31; paczka instalatora 1.0.32.

## Wydanie 1.0.33 — lokalizacja 81 kontekstow punktow fabularnych

Zastosowano nieodmienny skrot **PF** = punkty fabularne zamiast dynamicznego `Misc.STORY` (`story`). Kontrolowane tlumaczenie sasiednich tekstow wszystkich **81** oryginalnych uzyc w **24** klasach obejmuje **69** bezposrednich koncowek `point(s)`. Mapy: **OBF +24 nowych/40 skorygowanych**, **API +17 nowych/5 skorygowanych**; 10 testow kompletnych polskich konstrukcji, 14 testow negatywnych, bajtowa zgodnosc kodu metod obu zmodyfikowanych JAR. ZIP 870 identycznych danych i 3 programy Windows x64. [Dokumentacja i SHA](docs/RELEASE_1033.md), [publiczne liczniki](docs/STORY_1033_SUMMARY.json), [bramki wydania 1.1](docs/RELEASE_GATES_11.json).

**81 kontekstow poprawionych i sprawdzonych offline; wszystkie 81 nadal wymagaja testu UI w grze Windows.** Otwarta pozostaje odmiana 219 wywolan metod zaimkowych oraz 3600 historycznych recenzji API. Nie oznaczac jako kompletna 1.1.

## Wydanie 1.0.34 — dialogi bez angielskich dynamicznych zaimkow

[Raport techniczny](docs/RELEASE_1034.md) · [Rejestr 27 zmienionych wierszy](docs/RULES_PRONOUN_REVIEW_1034.json) · [bramki 1.1](docs/RELEASE_GATES_11.json). Zmodyfikowano tylko `data/campaign/rules.csv`: 27 wierszy, 62 zatwierdzone zamiany, 75 usunietych wystapien dynamicznych zaimkow w tekstach. Pozostale 869 danych oraz obie mapy OBF/API i patchery Java sa identyczne z 1.0.33. Obejmuje misje Akademii Galatia, informatora na Kapteyn, pielgrzymow Ludda i posrednika w ich misji. **Wywolania metod Java (219) pozostaja nienaruszone**, co jest odrebna metryka. Test w grze Windows nadal niezrealizowany; wydanie nie jest finalna 1.1.

## Wydanie 1.0.35 — dynamiczne zaimki w dialogach Tri-Tachyon i Ludda

Kolejne 64 widoczne wiersze `rules.csv` maja 93 poprawki tekstu, bez 108 angielskich zmiennych zaimkowych. Lacznie z 1.0.34 jest to **91 wierszy i 183 usuniete odniesienia**. Tlumaczenia nie zmieniaja skryptow, warunkow ani 219 istniejących wywolan getterow Java. Dane pozostalych 869 plikow oraz OBF/API JAR zachowane. Raport i instrukcja odtworzenia: [docs/RELEASE_1035.md](docs/RELEASE_1035.md); [rejestr 64 wierszy](docs/RULES_PRONOUN_REVIEW_1035.json). Wymagany test w dzialajacej grze Windows; to nadal NIE jest kompletna 1.1.

## Wydanie robocze 1.0.36 — poprawa jednego getHimOrHerself() bez zmian bajtkodu

[Weryfikowalny raport](docs/RELEASE_1036.md), [liczniki getterow](docs/PRONOUN_1036_SUMMARY.json), [bramki 1.1](docs/RELEASE_GATES_11.json). Dwa nowe literały API (himself/herself -> on/ona) i cztery poprawione fragmenty `PlanetaryShieldBarEvent`. Sprawdzono oba warianty polskiej konstrukcji w oryginalnej oraz spatchowanej puli stalych, jedno wywolanie Java getHimOrHerself() w optionSelected offset 663; **pozostale 218 z 219 wywolan wymagaja kontroli kontekstowej**, a wspolne `her` w getHimOrHer/getHisOrHer nadal koliduje. 20 nowych recenzji semantycznych API (78 zatwierdzonych offline lacznie, 3580 pozostale). API 5244 mapy/5242 trafienia w 938 klasach, wszystkie metody Java niezmienione bajtowo. 870 data identyczne z 1.0.35, testy Go/CI i Win x64 crossbuild. To nadal NIE jest ukonczona wersja 1.1 ani test gameplay Windows.

## Wersja 1.0.37 — szesc kolejnych kontekstow on/ona

W oryginalnym i spatchowanym API sprawdzono szesc miejsc `getHeOrShe` oraz 12 wariantow tekstow dla obu plci. Piec poprawionych wierszy `DRAFT/OPTIONAL` i jedna nowa brakujaca etykieta ` says. ` -> ` mowi. ` w `TriTachMajorLoanBarEvent`. Usunieto podwojne `bedzie` (`ContactIntel`), meska odmiane w negocjacjach i opisach naukowca/pozyczek. Bez modyfikacji logiki, OBF i plikow data. Rejestr: 83 historyczne API zatwierdzone offline, **3575** nadal do recenzji; Java gettery **7/219** kontekstow poprawionych offline, **212** oczekuje. Natywne Windows/gameplay nadal niewykonane. [Raport](docs/RELEASE_1037.md), [metryki](docs/PRONOUN_1037_SUMMARY.json).

## Wersja 1.0.38 — poprawiono caly kontekst spotkania z historykiem

W `HistorianData`, `HistorianBarEvent` i `DonationOffer` dodano **9 nowych** i poprawiono **12 istniejacych** tlumaczen API, bez zmiany metod JVM. Skladaja sie 18 wynikowych zdań dla obu plci, w tym prawidlowa odmiana `mezczyzna/kobieta`, `mu/jej` i `jego/jej`. Zweryfikowano **14** kontekstow wywolan getterow na oryginalnych bibliotekach. W `HistorianData` wspolny `her` = `jej` dziala w obu udokumentowanych funkcjach, ale konflikt `BaseBarEventWithPerson.her` #143 **nadal istnieje**. Gettery: 21/219 ocenionych offline, 198 pozostalo. Historia API: 104 zrecenzowane offline, 3554 do kontroli. Windows: 219 getterow + 81 PF + 91 dialogow nadal bez natywnego testu. [Raport 1.0.38](docs/RELEASE_1038.md), [dowody](docs/PRONOUN_1038_SUMMARY.json), [bramki 1.1](docs/RELEASE_GATES_11.json).

## Wersja 1.0.39 — kolejne 62 kontekstowe polskie dialogi

W `data/campaign/rules.csv` poprawiono 62 wiersze i 68 fragmentow, eliminujac **77** niepotrzebnych wstawek angielskich zaimkow bez zmiany skryptow, opcji, warunkow czy technicznych identyfikatorow. Razem z 1.0.34 i 1.0.35: **153** wiersze sprawdzone offline i **260** usunietych odnosnikow. Wszystkie 153 dialogi oczekuja na test wizualny w grze Windows. `tools/verify_1039.py` odwraca kazda podmiane i udowadnia bajtowa zgodnosc z 1.0.38, a `tools/verify_review_1039.py` chroni wczesniejsze 91 zatwierdzonych zmian. OBF/API JAR bez zmian. Nierozwiazane pozostaja **198** z 219 kontekstow wywolan getterow JVM, wspolne `her` #143 i 3554 starsze tlumaczenia API do recenzji. [Raport 1.0.39](docs/RELEASE_1039.md), [rejestr 62 zmian](docs/RULES_PRONOUN_REVIEW_1039.json).

## Wydanie 1.0.40 — forma mezczyzna/kobieta w wydarzeniach barowych

**3 nowe podmiany i 18 korekt API**. W osobnej bazowej klasie `BaseGetCommodityBarEvent` przetlumaczono `getManOrWoman()` i dopasowano sasiadujace frazy. Zweryfikowano 12 oryginalnych wywolan w siedmiu klasach i 24 polskie warianty fragmentow obu plci. Odrębny problem wspoldzielonych `her` pod indeksami #188 i #143 pozostaje otwarty; tych stalych nie modyfikowano, a inne zaimki moga nadal pozostawac angielskie w tych samych ekranach. API 5255 podmian, zero zmian wykonywalnego kodu JVM, realny upgrade z API 1.0.38 (jaka ma paczka 1.0.39), restore, idempotencja, uszkodzony JAR odrzucony, go test/vet i Windows x64 crossbuild PASS. 870 plikow danych bez zmian, 7371 poprawnych opcji. Historyczne API: 122/3658 recenzji offline, 3536 do recenzji; gettery: 33/219 ocenione offline, 186 pozostalo; Windows nieprzetestowany. [Raport](docs/RELEASE_1040.md), [bramki 1.1](docs/RELEASE_GATES_11.json).

## Wersja 1.0.41 — liczebniki i zabezpieczenie JAR przy ponownym uruchomieniu

**77 aktywnych poprawek API w 59 klasach**, wyłącznie w tłumaczonych tekstach z numerycznym `%s`: 40 × `jednostek` → `jedn.`, 25 × `punktow` → `pkt`, 12 × `lat swietlnych` → `l. sw.`. Znaczniki, identyfikatory i bajtkod Java są bez zmian. Te korekty gramatyczne NIE oznaczają pełnej recenzji semantycznej 77 zdań. Dodatkowo poprawiono patcher API: już zainstalowany JAR o zmodyfikowanych bajtach nagłówka ZIP nie jest uznawany za prawidłową kopię na podstawie identycznej rozpakowanej zawartości. Test integracyjny potwierdza odmowę bez nadpisania archiwum lub kopii zapasowej. [Raport](docs/RELEASE_1041.md), [metryki](docs/NUMERIC_1041_SUMMARY.json), [bramki 1.1](docs/RELEASE_GATES_11.json).

**Uwaga wydawnicza:** nieaktualny ZIP o SHA `81cee23f...` zawierał wcześniejszą kompilację instalatora. Poprawna, końcowa paczka 1.0.41 ma SHA **`ca780e8d6ca4e3ccbfba385c94d7508f25c58c4c3e740b5023d0fa902ef4e2d1`**, 16 256 610 bajtów, 873 wpisy; zaktualizowany EXE zweryfikowano bezpośrednio wewnątrz ZIP. Nadal brak native Windows gameplay test.
