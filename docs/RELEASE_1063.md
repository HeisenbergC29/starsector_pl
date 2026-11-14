# Starsector PL ASCII 1.0.63 — komorki Sciezki Ludda: techniczne kategorie i raporty incydentow

**Gra:** Starsector 0.98a-RC8. **Instalator:** Windows x64. **Docelowa 1.1:** nadal NIEUKONCZONA.

## Rzeczywisty zakres zmian

W oryginalnej klasie Java `com.fs.starfarer.api.impl.campaign.intel.bases.LuddicPathCellsIntel` sprawdzono wszystkie **47** wczesniej mapowanych tekstow. Zidentyfikowano **35** mapowan nadal oznaczonych DRAFT/OPTIONAL, nieujetych w zadnym z 447 wczesniejszych, historycznych zatwierdzen API. Na podstawie oryginalnego JAR `starfarer.api.jar` (Starsector 0.98a-RC8) wykonano recenzje wszystkich 35, z czego **14** wymagalo zmian jezykowych lub technicznych. Nie dodano nowych literali i nie zmieniono liczby wierszy mapy API (**5314**).

Główne poprawki (zapis ASCII gry):

| Angielska stala JVM | Wczesniejsza wartosc PL | Nowa wartosc PL / uzasadnienie |
| --- | --- | --- |
| `Colony threats` | `Zagrozenia dla kolonii` | **`Colony threats`** — techniczny klucz kategorii `Set.add()` w `getIntelTags` (nie etykieta do bezposredniego tlumaczenia) |
| `The Pather base at the ` | `Baza Sciezki Ludda w ` | `Baza Sciezki Ludda (lokalizacja: ` — bez wymuszania odmiany nazwy ukladu |
| ` is providing support to these cells.` | ` zapewnia wsparcie tym komorkom.` | `) wspiera te komorki.` |
| `The Pather cells have conducted a successful act of sabotage, disrupting ` | `Komorki Sciezki Ludda przeprowadzily udany sabotaz, zaklocajac dzialanie ` | `Komorki Sciezki Ludda przeprowadzily udany sabotaz. Cel: ` |
| ` operations for %s ` | ` dzialalnosc przez %s ` | `. Zaklocenie potrwa %s ` — zachowany parametr wyróżnienia liczby |
| `An attempted act of sabotage against ` | `Proba sabotazu wymierzona w ` | `Lokalne sluzby bezpieczenstwa udaremnily probe sabotazu. Cel: ` |
| ` operations was averted by the local security forces.` | ` udaremniono dzieki miejscowym sluzbom bezpieczenstwa.` | `.` |
| `The Pather cells have smuggled a planetbuster onto ` | `Komorki Sciezki Ludda przemycily na ` | `Wyznawcy Sciezki Ludda przemycili bron planetobojcza. Cel: ` |
| `If they succeed, the colony will effectively be destroyed.` | `Jesli im sie uda, kolonia zostanie praktycznie zniszczona.` | ` Jesli plan sie powiedzie, kolonia zostanie praktycznie zniszczona.` — dodano brakujaca spacje po zdaniu poprzedzajacym |

Ponadto poprawiono przypadki skutecznego i udaremnionego zamachu z bronia planetobojcza, opis czasu zaklocenia dzialalnosci oraz komunikat o zniszczeniu kolonii. **Wszystkie 14 zmian sa kluczowane pelna nazwa klasy i doslownym tekstem oryginalnej stalej.** Zadne identyfikatory klas, reguly, opcje dialogowe, skrypty ani instruckje gry nie zostaly zmienione.

Przykladowe zlozone polskie komunikaty:

- `Baza Sciezki Ludda (lokalizacja: uklad Corvus) wspiera te komorki.`
- `Komorki Sciezki Ludda przeprowadzily udany sabotaz. Cel: Rafineria. Zaklocenie potrwa 5 dni.`
- `Lokalne sluzby bezpieczenstwa udaremnily probe sabotazu. Cel: Produkcja paliwa.`
- `Wyznawcy Sciezki Ludda przemycili bron planetobojcza. Cel: Jangala. Lokalne sluzby bezpieczenstwa odnalazly i rozbroily ladunek, ratujac kolonie.`
- `Istnieja przeslanki, ze wyznawcy Sciezki Ludda planuja przemycic bron planetobojcza. Cel: Jangala. Jesli plan sie powiedzie, kolonia zostanie praktycznie zniszczona.`

Zachowano zastepowanie `%s` podswietlana liczba z oryginalnego wywolania `TooltipMakerAPI.addPara`. Metoda `BaseIntelPlugin.getDaysString(float)` dostarcza odpowiedni napis `day/days`, przetlumaczony we wczesniejszych wersjach na `dzien/dni`.

## Oryginalne JVM i audyt

- Oryginalny komercyjny `starfarer.api.jar`: SHA-256 `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`.
- Oryginalna pojedyncza klasa `LuddicPathCellsIntel.class`: SHA-256 `d2bdbbdb250692bd93694ec31624a4dfd3672d07c679a05d399f0bc17f262dbf`.
- Odczytano stałe `CONSTANT_String` **bajtowo z JVM**, w tym spacje na koncach napisow, ktorych komentarze `javap` nie zachowuja jednoznacznie. Nastepnie skojarzono je z instrukcjami `ldc/ldc_w` i metodami.
- **83** wykonane odczyty `ldc`, **71** unikatowych stalych tekstowych, wszystkie **47/47** istniejacych mapowan klasy znalezionych w oryginalnym JVM. Dla kazdej mapy zapisano metody, offsety, indeksy puli stalych, oryginalny SHA-256 oraz status.
- Krytyczny przypadek: `Colony threats` w `getIntelTags()`, `ldc_w` offset **36**, `Set.add()` offset **39**. Jest to techniczny tag i musi zachowac angielska wartosc. Przetlumaczenie go w izolacji mogloby rozlaczyc producentow i odbiorcow kategorii.
- Rejestry: `docs/JVM_AUDIT_1063.json`, `docs/LUDDIC_CELLS_REVIEW_1063.json` i append-only `docs/API_SEMANTIC_REVIEW_1063.json`.

## Integralnosc, testy i aktualizacja

- Mapa API przed: 5314 rekordow, SHA-256 `1f85680ff856b858f2f4db342aa98754c085a35bec6e9d0538113a55f9471f01`.
- Mapa API po: 5314 rekordow, SHA-256 `5443294fa1cdf96b21fb7bba3e5a92b96f8f1b6cec6807203dd7e3e74e1d58fc`.
- Odwzorowanie OBF niezmienione; wszystkie **870** plikow `mod/data` bajtowo identyczne z 1.0.62. `rules.csv` SHA-256 `4fcf72e3aad0a0c72bac3bea021a311b36f12c4d201d4dcf9b9c7edf2eeb0e04`.
- **60** symulacji kompozycji polskich komunikatow: 4 nazwy ukladow, 4 nazwy kolonii, 4 kategorie przemyslu, 5 wariantow liczbowych i 7 kontekstow narracyjnych. **12** uszkodzonych mapowan prawidlowo odrzuconych; **6** falszywych kontraktow paczki odrzuconych.
- `go test ./...` i `go vet ./...` dla OBF, API, instalatora: PASS. `maintenance/check_rules_options.py` — **7371** opcji, zero bledow. Windows x64 cross-build trzech plikow PE32+: PASS.
- Prywatny oryginalny JAR: *fresh 1.0.63 = upgrade 1.0.62 → 1.0.63*; patched API SHA-256 `64c62c940264e4bd386503c68b2784f775fc1275bab8a812b2812431e31f45f4`. **Dokladnie 1 klasa Java zmieniona**: `LuddicPathCellsIntel.class`. Struktura instrukcji JVM — identyczna z oryginalem. Powtorna instalacja jest no-op, przywracanie oryginalnych JAR-ow bitowo poprawne, uszkodzony JAR odrzucony. `docs/PRIVATE_UPGRADE_1063.json`.
- Lokalny ZIP `Starsector_PL_ASCII_0.98a_RC8_1.0.63_LOCAL.zip` — **19 588 411 B**, SHA-256 `e0e083e524c1fd1e95c9ef61f52ffdf0d6b4234b590ed9ff2dfbb68cdef11e73`, 873 wpisy, CRC PASS, 870 danych i brak komercyjnych JAR. Końcowy artefakt GitHub Actions weryfikowac osobno.

## Nierozwiazane kwestie — bez pozornego sukcesu

`MarketAPI.getOnOrAt()` w klasie `LuddicPathCellsIntel` wstawia dynamiczne angielskie `on/at` do opisu komorek na kolonii. Wpisy `There are active Luddic Path cells ` i `There are indications that sleeper ...` wymagaja korekty logiki skladania, nie tylko mapowania jednego angielskiego literalu. Analogicznie otwarty pozostaje przypadek `FactionAPI.getDisplayNameHasOrHave()` w klasie baz piratow. Nie wprowadzono niezweryfikowanych zmian kodu JVM.

Wieloetapowy audyt **API: 482/3658** zrecenzowanych historycznie, **3176** nadal niezweryfikowanych. Ponadto **186** getterow, **1953** potencjalnych znacznikow plciowych w **1006** rekordach dialogow, dalszy audyt wszystkich tekstow i rzeczywisty gameplay Windows — nadal OTWARTE. **Wersja 1.1 NIE GOTOWA**.

## Powtórzenie odtworzenia

Po `python3 tools/restore_snapshot.py` i stosowaniu `tools/apply_1013.py` do `tools/apply_1062.py`:

```sh
python3 tools/apply_1063.py worktree
python3 tools/verify_1063.py worktree
python3 tools/test_1063.py worktree
python3 tools/test_package_contract_1063.py worktree
python3 tools/build_review_1063.py worktree --record docs/LUDDIC_CELLS_REVIEW_1063.json --previous docs/API_SEMANTIC_REVIEW_1062.json --ledger docs/API_SEMANTIC_REVIEW_1063.json
python3 tools/check_release_gates_1063.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/RELEASE_GATES_1062.json --prior-semantic docs/API_SEMANTIC_REVIEW_1062.json --semantic docs/API_SEMANTIC_REVIEW_1063.json
python3 tools/test_release_gates_1063.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/RELEASE_GATES_1062.json --prior-semantic docs/API_SEMANTIC_REVIEW_1062.json --semantic docs/API_SEMANTIC_REVIEW_1063.json
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
python3 tools/package_1063.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.63_MINIMALNY.zip
```

Oryginalne komercyjne JAR-y testowac **prywatnie** przez `tools/audit_original_jvm_1063.py` oraz `tools/private_upgrade_1063.py`. Nie publikowac komercyjnych bajtow.
