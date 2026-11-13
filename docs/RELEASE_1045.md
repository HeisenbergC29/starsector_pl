# Starsector PL ASCII 1.0.45 — korekta 44 dialogow dynamicznych

**Data:** 2026-11-13  
**Gra:** Starsector 0.98a-RC8  
**Baza:** 1.0.44, `rules.csv` SHA-256 `cf1e35899c5cebd42430cf45242662a6c59389e3330c493c6b667bf2eafb918b`  
**Wynik:** `rules.csv` SHA-256 `e9a6ad60da0caca6fa89af21370eddfa461de39324486368458aca2575e3b64a`  
**Status:** nowe tlumaczenia przetestowane offline; **NIE** jest to ukonczona polonizacja 1.1.

## Zakres rzeczywistych poprawek

W 44 nazwanych rekordach `data/campaign/rules.csv` wykonano 80 lokalnych podmian fraz i usunieto 93 problematiczne odwolania do zmiennych `$heOrShe`, `$HeOrShe`, `$hisOrHer`, `$HisOrHer` i `$himOrHer`. Przetlumaczono wybrane wyrazenia w kontekstach patroli Tri-Tachyon, kontaktow Sciezki Ludda, dziesieciny i misji akademickich. Nie wykonano automatycznej masowej zamiany zmiennych.

Przyklady nowych calych fragmentow polskich (ASCII w grze):

| Kontekst | Poprzedni tekst w grze | Nowy tekst w grze |
|---|---|---|
| Spotkanie ze Sciezka Ludda | `$HeOrShe rozpaczliwie splata $hisOrHer dlonie` | `Rozmowca rozpaczliwie splata dlonie` |
| Patrol Tri-Tachyon | `$HeOrShe spoglada na $hisOrHer drugi ekran` | `Rozmowca spoglada na drugi ekran` |
| Negocjacja dziesieciny | `do $hisOrHer zalogi` | `do swojej zalogi` |
| Kontakt akademicki | `zaskakuje to $himOrHer` | `zaskakuje to pirackiego kapitana` |

Każda poprawka jest przypisana do konkretnego ID dialogu i sprawdzona na pelnym tekscie tego rekordu. Uczciwe ograniczenie: review dotyczy wyszczegolnionych fraz, nie jest jeszcze kompletna recenzja kazdego pozostalego zdania w tych 44 rekordach. Nie zmieniono imion, nazwisk ani mechaniki gry.

## Testy offline — niezalezne od Windows runtime

- Dokladnie 44 rekordy, 80 podmian tekstowych i 93 usuniete odwolania. Kazdy zmieniony rekord nie zawiera juz zadnej z wymienionych *ogolnych* zmiennych zaimkowych.
- Zmieniono wylacznie kolumne `text` rekordow CSV; `id`, `trigger`, `conditions`, `script`, `options`, `notes` sa identyczne. Struktura, ASCII i CRLF zachowane.
- Odwracalnosc 1.0.45 -> 1.0.44: identyczny SHA-256 poprzedniego `rules.csv`.
- Pozostale 869 plikow `data/`: bez zmian; niezalezny hash drzewa SHA-256: `5bfda6c69b2f83e3913fa4e1475c6288e1f3a0d82914fd007abba381e8da0fc1`.
- Mapy OBF i API oraz pliki wykonywalne patcherow Java: bez zmian. Nie zmieniono zadnego getter-callsite Java ani zadnej klasy JAR w tym etapie.
- `tools/test_1045.py`: 7 celowych naruszen nie przechodzi walidacji (bledne SHA, zmiana naglowka, CRLF, nie-ASCII, usuniety kontekst, uszkodzone odwracanie, dowolna modyfikacja innego pliku).
- Raport `docs/RULES_GENDER_REVIEW_1045.json` zawiera identyfikatory oraz sumy SHA-256 fragmentow tekstu przed/po i jest sprawdzany wzgledem danych; wczesniejsze review nie moga byc policzone po raz drugi.
- `tools/audit_rules_pronouns_1045.py` weryfikuje ze wskazanym hashem caly `rules.csv`, wykazujac 2275 pozostalych wystapien kandydatow w 1139 wierszach (w 1.0.44: 2368 w 1183 wierszach). To **liczba surowych placeholderow**, a nie liczba potwierdzonych bledow w grze. Szczegoly `docs/PRONOUN_AUDIT_1045.json`.

Wszystkie przedzialy i liczniki powyzej odnosza sie do materialu statycznego, bez natywnej kontroli UI. Weryfikacja 7371 opcji CSV, testy Go i pakowanie Windows x64 sa wykonywane przez pipeline GitHub Actions; ich wynik należy odczytac z konkretnego przebiegu CI, nie z samego tego dokumentu.

## Reprodukcja z GitHuba

Po `python3 tools/restore_snapshot.py` i kolejnych overlayach `tools/apply_1013.py`–`tools/apply_1044.py`, wykonywanych z argumentem `worktree`:

```bash
python3 tools/apply_1045.py worktree --ledger-out /tmp/RULES_GENDER_REVIEW_1045_generated.json
python3 tools/verify_1045.py worktree \
  --prior-ledger docs/RULES_PRONOUN_REVIEW_1034.json \
  --prior-ledger docs/RULES_PRONOUN_REVIEW_1035.json \
  --prior-ledger docs/RULES_PRONOUN_REVIEW_1039.json \
  --prior-ledger docs/RULES_POSSESSIVE_REVIEW_1043.json \
  --prior-ledger docs/RULES_GENDER_REVIEW_1044.json
python3 tools/test_1045.py worktree
python3 tools/audit_rules_pronouns_1045.py worktree/mod/data/campaign/rules.csv --output /tmp/PRONOUN_AUDIT_1045_generated.json
python3 tools/check_release_gates_1045.py worktree --gates docs/RELEASE_GATES_11.json --ledger docs/RULES_GENDER_REVIEW_1045.json
python3 tools/test_release_gates_1045.py worktree --gates docs/RELEASE_GATES_11.json --ledger docs/RULES_GENDER_REVIEW_1045.json
(cd worktree && sh build_windows.sh)
python3 tools/package_1045.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.45_MINIMALNY.zip
```

## Co blokuje wydanie 1.1

- 186 z 219 oryginalnych getter-callsite Java wciaz nie ma przegladu kontekstowego (kolizja `her` #143 nadal otwarta).
- 3536 historycznych wierszy API pozostaje bez pelnej recenzji znaczenia; statusy DRAFT/OPTIONAL sa z punktu widzenia patchera instalowane, nie mozna ich automatycznie uznac za niewidoczne.
- Wszystkie 253 zmodyfikowane od 1.0.34 dialogi (44 nowe plus 209 poprzednich), 81 kontekstow PF, 77 poprawek liczebnikow i 15 poprawek interpunkcji wymagaja testow w UI Windows.
- Cala gra i komplet jej wyswietlanych tekstow nadal nie zostaly zweryfikowane; nie wykonano natywnego testu rozgrywki Windows.

**Wersje robocze 1.0.x nie rownaja sie pelnej polonizacji 1.1.**
