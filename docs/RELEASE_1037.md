# Starsector PL 1.0.37 — kontekstowe poprawki zaimkow on/ona

**Gra:** Starsector 0.98a-RC8. **Pelne wydanie 1.1 wciaz nie jest gotowe.** Ten etap poprawia kilka punktowych bledow juz przetlumaczonych komunikatow; nie zmienia kodu wykonywalnego Java ani technicznych identyfikatorow. Teksty gry pozostaja w ASCII bez polskich znakow diakrytycznych.

## Rzeczywiste zmiany

- **5 korekt aktywnych wierszy API** (z zachowaniem statusow historycznych):
  - `ContactIntel`: usunieto podwojne „bedzie” w opisie okresowych zadan kontaktu;
  - `DeliveryBarEvent`: usunieto meska odmiane `niezadowolonego` po zmiennej `on/ona`;
  - `ScientistAICoreBarEvent`: zastapiono zalezne od plci `nie mial` neutralnym `nie mysli trzezwo`;
  - `ScientistAICoreIntel`: `nie byl nikim waznym` -> `nie jest nikim waznym`;
  - `TriTachLoanBarEvent`: opis utraty opanowania zmieniono na neutralny `traci rezon ...`.
- **1 nowy mapowany literał API** w `TriTachMajorLoanBarEvent`: rzeczywiste ` says. ` -> ` mowi. `. W tej samej klasie istnieje tez inny, dluzszy tekst ` says. "I find that reassuring."`, ktory byl juz tlumaczony; poprawka dotyczy odrebnego miejsca skladania zdania, a nie zastepuje poprzedniego wpisu.
- Przeanalizowano **6 konkretnych instrukcji `getHeOrShe`** w oryginalnym JVM, zweryfikowano obie odmiany kazdego lokalnego fragmentu (**12 wariantow**). Nie twierdzimy, ze cala zawartosc kazdego powiazanego ekranu jest kompletna: w czesci ekranow wystepuja tez inne, nierozwiazane gettery.
- Mapy: **OBF bez zmian** od 1.0.36 (3534 podmiany / 539 klas), **API 5244 -> 5245 wierszy**, **5243 rzeczywiste podmiany w 938 klasach**. Wszystkie **870 plikow data** pozostaly identyczne z 1.0.36.

## Niezalezna weryfikacja na prywatnych oryginalnych JAR

- SHA256 oryginalnego API: `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`.
- SHA256 spatchowanego API 1.0.37: `5eb063221593fd4c9edecd5da37f024a01f87f3fd9e411a74b187fc09d7646e1`.
- Pelne porownanie 938 zmienionych klas metodami `proof_class_files`: **5243 podmiany `CONSTANT_String`, zero zmian w kodzie wykonywalnym**; wspolny wpis `her` #143 w `BaseBarEventWithPerson` zachowany dokladnie.
- Instalacja na oryginale i **aktualizacja z rzeczywiscie spatchowanego 1.0.36** daja identyczny plik bajt w bajt. Ponowna instalacja nic nie zmienia. Restore odtwarza oryginalne SHA256. Uszkodzony JAR bez zweryfikowanego backupu jest odrzucany, bez nadpisania.
- **9 testow negatywnych mapy**, **10 testow negatywnych bramek 1.1**, wszystkie testy Go/vet trzech komponentow, build Windows x64 PE32+ i 7371/7371 opcji rules.csv — zaliczone lokalnie. Wynik niezaleznego GitHub Actions nalezy sprawdzic po commicie.

## Rejestry 1.1

- Oryginalne **219** wywolan getterow Java. Poprzednio 1 sprawdzone offline; teraz **6 dodatkowych** (razem **7**), pozostaje **212** do przegladu kontekstowego offline. **Wszystkie 219** pozostaje do sprawdzenia wizualnie w dzialajacej grze Windows.
- Wspoldzielony literal `her` #143 — nadal otwarty, bez ryzykownej globalnej podmiany.
- Historyczna grupa API: **83** zatwierdzone offline (78 poprzednich +5), **3575** jeszcze do recenzji semantycznej. **3684** teksty w monitorowanej grupie nadal bez kontroli Windows.
- **81 kontekstow `Misc.STORY`** poprawionych offline, lecz 81 nadal wymaga testu w grze. **91** poprawionych wierszy `rules.csv` wymaga kontroli UI. To inne metryki niz wywolania Java.

## Odtworzenie na repozytorium

```bash
python3 tools/restore_snapshot.py
for n in 1013 1014 1015 1016 1017 1018 1019 1020 1021 1022 1023 1024 1025 1026 1027 1028 1029 1030 1031 1032 1033 1034 1035 1036 1037; do
  python3 "tools/apply_$n.py" worktree
done
python3 tools/verify_1037.py worktree
python3 tools/verify_review_1037.py worktree --prior-ledger docs/API_SEMANTIC_REVIEW_1036.json --ledger docs/API_SEMANTIC_REVIEW_1037.json
python3 tools/check_release_gates_1037.py worktree --gates docs/RELEASE_GATES_11.json --prior-ledger docs/API_SEMANTIC_REVIEW_1036.json --ledger docs/API_SEMANTIC_REVIEW_1037.json
python3 tools/test_1037.py worktree
python3 tools/test_release_gates_1037.py worktree --gates docs/RELEASE_GATES_11.json --prior-ledger docs/API_SEMANTIC_REVIEW_1036.json --ledger docs/API_SEMANTIC_REVIEW_1037.json
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
python3 tools/package_1037.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.37_MINIMALNY.zip
```

Z prywatnymi oryginalnymi JAR (ktorych **nie** wolno commitowac do repo):

```bash
python3 tools/verify_1037.py worktree \
 --original-api /PRIVATE/starfarer.api.jar \
 --patched-api /PRIVATE/installed/starfarer.api.jar
```

## Paczka dla gracza

`Starsector_PL_ASCII_0.98a_RC8_1.0.37_MINIMALNY.zip` — **15 615 848 bajtow**, **873 wpisy**, 870 `data/` + metadane/instrukcja + instalator Windows x64. SHA256: `19f824d47f1053e08ad91e54c3fc17bb140812109fa693e57b89818f4086a46c`. ZIP CRC PASS. Oryginalnych bibliotek gry nie zawiera.

**Brak natywnego testu Windows. Nie oznaczac jako wersji 1.1.**
