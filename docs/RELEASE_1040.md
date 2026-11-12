# Starsector PL ASCII 1.0.40 — kontekstowe `man/woman` w wydarzeniach barowych

**Wydanie robocze 12.11.2026. Nie jest to pelna 1.1.** Wersja gry 0.98a-RC8.

## Zakres zmian

Przy weryfikacji oryginalnej biblioteki API ustalono, ze `BaseGetCommodityBarEvent` i `BaseBarEventWithPerson` sa dwiema roznymi klasami bazowymi. Obie moga zwracac angielskie formy rodzaju, lecz maja niezalezne pule stalych i wspoldzielone `her` odpowiednio pod indeksami #188 i #143. W 1.0.40 **nie zmieniono zadnej z tych stalych `her`** ani metod wykonywalnych Java.

Bezpiecznie przetlumaczono `BaseGetCommodityBarEvent.getManOrWoman()` (`man` -> `mezczyzna`, `woman` -> `kobieta`) i dopasowano otaczajace teksty w siedmiu klasach. Audyt na oryginalnej i spatchowanej bibliotece potwierdza dokladnie **12 wywolan** i **24 warianty sprawdzonych fragmentow** (dwa rodzaje gramatyczne na kazde wywolanie).

| Klasa | Wywolania `getManOrWoman` | Przyklad poprawy |
| --- | ---: | --- |
| `CorruptPLClerkSuppliesBarEvent` | 1 | `Przy barze stoi mezczyzna/kobieta ...` |
| `DeliveryBarEvent` | 3 | `Przy stoliku w rogu siedzi mezczyzna/kobieta ...` |
| `LuddicCraftBarEvent` | 2 | `Przy stoliku siedzi mezczyzna/kobieta w stroju ...` |
| `LuddicFarmerBarEvent` | 2 | `Przy stole siedzi mezczyzna/kobieta w stroju ...` |
| `ScientistAICoreBarEvent` | 1 | `W poblizu stoi mezczyzna/kobieta w akademickim mundurze ...` |
| `TriTachLoanBarEvent` | 2 | `W odpowiedzi mezczyzna/kobieta milknie ...` |
| `TriTachMajorLoanBarEvent` | 1 | `Gdy negocjacje dobiegaja konca, mezczyzna/kobieta ...` |

**Uwaga o zakresie:** sa to sprawdzone fragmenty otaczajace `getManOrWoman`, nie wszystkie kompletne zdania tych wydarzen. Niektore z tych samych ekranow nadal wywoluja `getHisOrHer` i `getHimOrHer`, ktore moga wstawiac angielskie `his/her/him`. Tych nie uznano za naprawione. W szczegolnosci wspoldzielona stala `her` nie zostala globalnie przetlumaczona.

Nowa mapa API dodaje **3** literalne podmiany i koryguje **18** istniejacych mapowanych pol. Przypadki ujawnione podczas testu: oryginalny tekst `A ` ma koncowa spacje niewidoczna w `javap`; napis `Nod to the concerned ` juz istnial w mapie i wymagal korekty, a nie dodania. Oba problemy wykryto i poprawiono **przed** przygotowaniem wydania.

## Zmiany techniczne i testy

- API: `TLUMACZENIA_JAR_1038.csv` (5254 wiersze) -> `TLUMACZENIA_JAR_1040.csv` (**5257 wierszy**, **5255** rzeczywistych podmian w **938** klasach). OBF: 3534 podmiany/539 klas, bez zmian.
- SHA-256 oryginalnego API: `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`.
- SHA-256 spatchowanego API 1.0.40: `5e76f0ba08927564b35ded6ffa5dfba7c32134df152394c7cca19f5e96bf3ef5`.
- Wszystkie zmodyfikowane klasy sprawdzone strukturalnie: tylko aktualizacje puli `CONSTANT_String`/nowe `CONSTANT_Utf8`, **zero zmian wykonywalnych instrukcji i pozostalych bajtow metod**.
- Instalacja na oryginalnym API i aktualizacja z faktycznie spatchowanej wersji API 1.0.38 (uzywanej takze w 1.0.39) daja identyczny SHA; ponowna instalacja bez zmian; restore oryginalnego SHA; uszkodzony JAR odrzucony bez nadpisania.
- 13 negatywnych testow map i 12 negatywnych testow bramek, 3x Go test/vet, 3x Windows x64 PE crossbuild, 7371/7371 dialog option syntax PASS. Natywnego Windows gameplay **nie wykonywano**.
- 870 plikow `mod/data/` jest identyczne bajt po bajcie z 1.0.39; 873 wpisy ZIP, CRC PASS. W publicznym repo brak oryginalnych komercyjnych JAR.

Wydanie: `Starsector_PL_ASCII_0.98a_RC8_1.0.40_MINIMALNY.zip`, 16 043 243 B, SHA-256 `1b10c2bf2aaaaa2eb6d74a1b2e77d59bf12c631490cf8ba4a74dc98759a24d02`.

## Kontrola przed 1.1

| Bramka | Stan po 1.0.40 |
| --- | --- |
| `Misc.STORY` | 81/81 poprawionych offline; 81 czeka na Windows UI |
| Getter calls | 33/219 wywolan ocenionych kontekstowo offline (w tym 12 `getManOrWoman` w tej wersji); 186 do recenzji; wszystkie 219 bez Windows UI |
| Historyczne API | 122 z 3658 recenzji offline (104 poprzednie + 18 z tego etapu), 3536 otwarte |
| Dialogi `rules.csv` | 153 poprawione offline, wszystkie bez natywnego UI |
| Windows gameplay | NIEWYKONANY |

Odtwarzanie CI: snapshot 1.0.12 -> po kolei `tools/apply_1013.py` ... `tools/apply_1039.py` -> `tools/apply_1040.py`. Dowody: `tools/verify_1040.py`, `tools/verify_review_1040.py`, `tools/check_release_gates_1040.py`, `tools/test_1040.py`, `tools/test_release_gates_1040.py`, `tools/package_1040.py` oraz JSON-y w `docs/`.
