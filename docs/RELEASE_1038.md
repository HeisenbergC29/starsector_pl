# Starsector PL 1.0.38 — pełny kontekst spotkania z historykiem

Gra: **Starsector 0.98a-RC8**. Wydanie **1.0.38 jest etapem prac nad 1.1**, a nie ukończoną polonizacją. Tekst gry zapisujemy wyłącznie jako polski ASCII, zgodnie z istniejącymi ograniczeniami fontów.

## Poprawki rzeczywiście wykonane

- W klasie `HistorianData` przetłumaczono pięć dotąd nietłumaczonych stałych używanych przez gettery: `man`/`woman` -> `mezczyzna`/`kobieta`, `him` -> `mu`, `his` -> `jego`, `her` -> `jej`.
- To **przypadek kontekstowy**: współdzielone `her` w `HistorianData` może poprawnie oznaczać jednocześnie celownik ("Dziekujesz jej") i zaimek dzierżawczy ("za jej informacje"). NIE rozszerzać tej translacji automatycznie na `BaseBarEventWithPerson`: tam wspólne `her` (#143) ma nadal nierozwiązany konflikt przypadków.
- W `HistorianBarEvent` dodano trzy brakujące fragmenty tekstowe i poprawiono **11** dotychczasowych. Składanie uwzględnia rodzaj gramatyczny: `Porozmawiaj z mezczyzna/kobieta ...`, `Dziekujesz mu/jej za jego/jej informacje`, wygląd/historyk w podeszłym wieku i pożegnanie. Zlikwidowano błędne podwójne zaprzeczenie "nie nie wiem" oraz podwójny cudzysłów w powitaniu.
- W `DonationOffer` dodano jeden brakujący fragment `pursue` -> `zbadac` oraz poprawiono sąsiedni opis darowizny. Pełny opis zachowuje oryginalny tryb przypuszczający "pozwolilaby" i oba warianty rodzaju.
- Razem: **9 nowych wpisów API i 12 korekt istniejących**; API ma **5254 wiersze mapy, 5252 rzeczywiste podmiany w 938 klasach**. OBF bez zmian od wersji 1.0.33 (**3534 podmiany w 539 klasach**). Wszystkie **870 plików `data/`** identyczne z 1.0.37.

## Kontrola oryginalnego bajtkodu i kontekstów

- Oryginalne archiwum `starfarer.api.jar` gry potwierdzone SHA256 `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`.
- Po spatchowaniu 1.0.38 SHA256 `a55118c7ad5a75c90c6f6c2aed8e61ac19151dc4468744acf823a577c69a4dc3`.
- Niezależna kontrola `tools/verify_1038.py` porównuje wszystkie klasy JVM: **938 zmodyfikowanych klas, 5252 podmiany CONSTANT_String, zero zmian bajtkodu wykonywalnego**.
- Zbadano dokładne położenia **13** wywołań getterów w `HistorianBarEvent` i **1** w `DonationOffer`. Zrekonstruowano **18 wariantów pełnych zdań** (9 konstrukcji × dwie płcie). Rejestr wywołań Java: pierwotnie 219, poprzednio 7 zatwierdzonych offline, obecnie **21**, pozostaje **198** do recenzji. Wszystkie 219 nadal czekają na test UI Windows.
- Kompilator został uruchomiony na źródłach 1.0.38. Faktyczna instalacja na oryginalnym JAR i aktualizacja z faktycznie spatchowanego API 1.0.37 prowadzą do **identycznego wynikowego JAR bajt w bajt**. Ponowna instalacja nie modyfikuje pliku. Przywracanie odtwarza oryginalne SHA. Celowo uszkodzony JAR jest odrzucany bez nadpisania.
- **13 negatywnych testów mapy i 13 negatywnych testów bramek wydania**, wszystkie `go test`/`go vet` dla trzech komponentów, Windows x64 PE32+ dla trzech EXE oraz **7371 poprawnych opcji `rules.csv`**: zaliczone lokalnie. Wynik CI GitHub jest osobnym potwierdzeniem; podawać PASS dopiero po zakończeniu workflow.

## Recenzja semantyczna i ograniczenia

`docs/API_SEMANTIC_REVIEW_1038.json` zachowuje 83 wcześniejsze zatwierdzenia wraz z niezmienionymi hashami i dodaje **21** historycznych pozycji DRAFT/OPTIONAL z `HistorianBarEvent` i `DonationOffer`. Razem zatwierdzono offline **104**, pozostało **3554** ze śledzonej historycznej puli 3658. Nowych wpisów z tej wersji nie zaliczono do historycznej puli; w grupie oczekującej na niezależną kontrolę rozgrywki jest **3693** fragmentów.

Zmiana `HistorianData.her` nie usuwa konfliktu `BaseBarEventWithPerson.her` #143. Pozostałe wymagania do 1.1: 198 kontekstów getterów do kontroli offline, 81 przetłumaczonych kontekstów `Misc.STORY` do testu wizualnego, 91 dialogów `rules.csv` do testu wizualnego, pełna kontrola kompletności oraz działająca gra Windows. **Nie uznawać kompilacji EXE za test uruchomienia gry.**

## Odtworzenie źródeł i testów

```sh
python3 tools/restore_snapshot.py
for n in 1013 1014 1015 1016 1017 1018 1019 1020 1021 1022 1023 1024 1025 1026 1027 1028 1029 1030 1031 1032 1033 1034 1035 1036 1037 1038; do
    python3 "tools/apply_${n}.py" worktree
done
python3 tools/verify_1038.py worktree
python3 tools/verify_review_1038.py worktree --prior-ledger docs/API_SEMANTIC_REVIEW_1037.json --ledger docs/API_SEMANTIC_REVIEW_1038.json
python3 tools/check_release_gates_1038.py worktree --gates docs/RELEASE_GATES_11.json --prior-ledger docs/API_SEMANTIC_REVIEW_1037.json --ledger docs/API_SEMANTIC_REVIEW_1038.json
python3 tools/test_1038.py worktree
python3 tools/test_release_gates_1038.py worktree --gates docs/RELEASE_GATES_11.json --prior-ledger docs/API_SEMANTIC_REVIEW_1037.json --ledger docs/API_SEMANTIC_REVIEW_1038.json
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
python3 tools/package_1038.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.38_MINIMALNY.zip
```

Jeżeli dostępne są prywatne, legalnie pozyskane oryginalne JAR, przeprowadzić dodatkową kontrolę bajtową:

```sh
python3 tools/verify_1038.py worktree --original-api /PRIVATE/starfarer.api.jar --patched-api /PRIVATE/installed/starfarer.api.jar
python3 tools/verify_review_1038.py worktree --prior-ledger docs/API_SEMANTIC_REVIEW_1037.json --ledger docs/API_SEMANTIC_REVIEW_1038.json --patched-api /PRIVATE/installed/starfarer.api.jar
```

Nie publikować oryginalnych komercyjnych JAR, ani pełnych wypisów oryginalnych napisów w publicznym repozytorium.

## Gotowa paczka 1.0.38

`Starsector_PL_ASCII_0.98a_RC8_1.0.38_MINIMALNY.zip`: **15 830 546 B**, **873 wpisy** (870 `data/` + `mod_info.json`, `CZYTAJ.txt`, instalator Windows x64), SHA256 `75192d9d8e79e1e75b00e48a0ddee70a2d9dd6488056b7b41637a18c3c1fce0e`. ZIP CRC PASS. Paczka nie zawiera oryginalnych JAR.

**Brak natywnego testu gry Windows. 1.1 pozostaje w opracowaniu.**
