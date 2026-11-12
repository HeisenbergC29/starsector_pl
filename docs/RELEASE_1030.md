# Starsector PL 1.0.30 — wydanie robocze (0.98a-RC8)

**Cel 1.1 nadal otwarty.** Nie odnotowano natywnego testu Windows ani gry. Nie dodawac komercyjnych JAR do repozytorium.

## Zmiany zweryfikowane na oryginalnych klasach JVM

W stosunku do 1.0.29: **2 nowe etykiety OBF, 4 nowe fragmenty API i 1 poprawiona wczesniejsza translacja API**.

| Klasa | Oryginalny literal | Nowy tekst ASCII | Kontekst |
|---|---|---|---|
| `com.fs.starfarer.coreui.O` | `Name:` | `Nazwa:` | etykieta okna nadawania nazwy |
| `com.fs.starfarer.ui.impl.StandardTooltipV2$15` | `Price: ` | `Cena: ` | opis ceny towaru (zachowana spacja na koncu) |
| `com.fs.starfarer.api.impl.campaign.intel.PersonBountyIntel` | `He is` | `On` | poczatek zdania o polozeniu poszukiwanej osoby |
| `...PersonBountyIntel` | `She is` | `Ona` | alternatywny rodzaj gramatyczny |
| `...PersonBountyIntel` | ` rumored to be ` | ` podobno ` | korekta poprzedniego tekstu ` wedlug poglosek przebywa `, zapobiegajaca skladaniu `przebywa ukrywa sie` |
| `com.fs.starfarer.api.impl.campaign.abilities.InterdictionPulseAbility` | `Interdict! (` | `Zaklocenie! (` | komunikat impulsu zaklocajacego |
| `...InterdictionPulseAbility` | `s)` | ` s)` | poprawny odstep przed symbolem sekundy w `Zaklocenie! (4 s)` |

Dla opisu nagrody zweryfikowano wszystkie 6 kombinacji (On/Ona × `hiding out near` / `hiding out in` / `located in`), m.in. `On podobno ukrywa sie w poblizu Eos.` oraz `Ona podobno znajduje sie w Eos.`. Znaczniki i nazwy dynamiczne pozostaja niezmienione.

Nowe mapy: OBF `TLUMACZENIA_OBF_10130.csv` (**3510 wpisow / 3510 trafien / 538 klas**); API `TLUMACZENIA_JAR_1030.csv` (**5219 wpisow, 5217 trafien / 938 klas**, w tym jeden stary wiersz bez dopasowanej klasy API i drugi historycznie nieaplikowany). W poprawionym API jeden wczesniejszy wpis otrzymal status `VERIFIED_VISIBLE_SENTENCE_1030`, dlatego nadal **3658** wpisow DRAFT/OPTIONAL wymaga semantycznej recenzji; to nie jest certyfikacja pozostalych wpisow.

## Weryfikacja techniczna

- Oryginalne SHA-256: OBF `5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8`, API `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`.
- Nowe SHA-256 po instalacji: OBF `291a0098153b058b5725a97a331d4e41763bef9ea33dbac42eea0d0a989f8722`; API `f1927b0fbea90e41c049e95b954f97acfcf9e59496c89371b774ad0e12cea4e6`.
- Oryginalna pula stalych JVM i instrukcje `ldc`: **6/6 nowych par** aktywnie uzywanych w kodzie, **1/1 poprawiony starszy literal**. Parser czyta oryginalny `CONSTANT_String`, bo tekstowy `javap` ucina spacje na koncu.
- Audyt wszystkich **538 OBF + 938 API** zmienionych klas: zero nieautoryzowanych modyfikacji wykonywalnego bajtkodu; jedynie dozwolone literały, odniesienia do nich i manifest OBF.
- Swieza instalacja obu oryginalnych JAR: PASS. **Rzeczywisty upgrade spatchowane 1.0.29 → 1.0.30**: wynik obu JAR bajtowo identyczny ze swieza instalacja, PASS.
- Idempotencja: PASS; restore obu oryginalnych JAR bajtowo: PASS; celowo uszkodzone JAR odmowa: PASS.
- 870/870 plikow `mod/data/` identyczne z paczka 1.0.29; `rules.csv` 7371/7371 prawidlowych opcji.
- Go `test` i `vet`: PASS we wszystkich 3 komponentach; kompilacja 3 EXE Windows x64: PASS na Linuxie.
- Odtwarzalnosc: 1032 niegenerowane pliki zrodel porownane bajtowo po ponownym uruchomieniu overlay 1030: PASS.
- Paczka `Starsector_PL_ASCII_0.98a_RC8_1.0.30_MINIMALNY.zip`: **14 637 790 bajtow**, SHA-256 `b59d2dda6881907a62348de9fd3c53928e668e71a13de17804c56d34534589c7`, **873 wpisy**; CRC PASS, brak komercyjnych JAR.
- **Windows natywny i gameplay wizualny: NIE WYKONANO**. Powyzsze testy nie potwierdzaja renderingu wszystkich komunikatow w uruchomionej grze.

## Reprodukcja na GitHub (bez komercyjnych JAR)

```bash
python3 tools/restore_snapshot.py
for n in 1013 1014 1015 1016 1017 1018 1019 1020 1021 1022 1023 1024 1025 1026 1027 1028 1029 1030; do
  python3 "tools/apply_$n.py" worktree
done
python3 tools/verify_1030_sentences.py worktree
python3 tools/test_dynamic_1030.py
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
python3 tools/check_release_gates_1030.py worktree --gates docs/RELEASE_GATES_11.json
(cd worktree && sh build_windows.sh)
python3 tools/package_1030.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.30_MINIMALNY.zip
```

Opcjonalnie na **prywatnych** oryginalnych bibliotekach uzytkownika: `tools/verify_1030_callsites.py` i `tools/verify_1029_jars.py` (do testow wszystkich klas potrzebny oryginalny i docelowy JAR; ostatni skrypt z nazwy 1029 ma ogolny parser i nadal moze sluzyc do analizy 1.0.30 po aktualizacji licznikow).

## Pozostale bramki do 1.1

`Misc.STORY`: **81 uzyc**, niezmienione; wspoldzielone zaimki: **219 wywolan**, niezamkniete; pozostale aktywne starsze wpisy DRAFT/OPTIONAL: **3658**; przeglad kompletnej polonizacji i natywny test Windows: NIEZAKONCZONE. Zob. `docs/RELEASE_GATES_11.json`, issue #3 i #4. Nie nadawac numeru 1.1 bez dowodow dla kazdej bramki.
