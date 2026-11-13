# Starsector PL ASCII 1.0.47 — liczebniki produkcji i audyt opcji walki

**Data:** 2026-11-13  
**Gra:** Starsector 0.98a-RC8  
**Poprzednia wersja:** 1.0.46  
**Status:** wydanie robocze, **1.1 nadal NIE jest kompletna**.

## Co rzeczywiscie poprawiono

W 14 precyzyjnie wskazanych wierszach mapy API, nalezacych do 11 klas Java, poprawiono niewlasciwa odmiane `jednostke` po dynamicznym `%s`. Wersje historyczne zakladaly liczbe pojedyncza; w czasie gry wartosc moze byc inna. Zastosowano juz uzywany w lokalizacji skrot `jedn.`, niezalezny od wartosci. Zmiany sa ograniczone do tlumaczonego literalnego tekstu; bez edycji pol technicznych, kodu JVM lub mechaniki.

Przyklady (ASCII widoczne w grze):

| Kontekst | Przed | Po |
|---|---|---|
| Premia przemyslu | `Zwieksza produkcje o %s jednostke.` | `Zwieksza produkcje o %s jedn.` |
| Efekt spadku popytu | `Zmniejsza zapotrzebowanie o %s jednostke.` | `Zmniejsza zapotrzebowanie o %s jedn.` |
| Przemysl z ulga kosztowa | `Zmniejsza koszt utrzymania o %s. Zmniejsza zapotrzebowanie o %s jednostke.` | `Zmniejsza koszt utrzymania o %s. Zmniejsza zapotrzebowanie o %s jedn.` |
| Dziewiec budynkow (m.in. baza wojskowa, port kosmiczny, stacja orbitalna, oslona planetarna) | `Zmniejsza koszty utrzymania o %s. Zmniejsza zapotrzebowanie o %s jednostke. ` | `Zmniejsza koszty utrzymania o %s. Zmniejsza zapotrzebowanie o %s jedn. ` |

**Zakres:** 14 rekordow mapy API w 11 klasach, 5260 pozycji mapy zarowno przed, jak i po; 0 nowych kluczy; 0 zmian statusow. Wszystkie 870 plikow `data/` identyczne z 1.0.46. Patcher OBF zostaje nietkniety.

Wersja 1.0.47 `TLUMACZENIA_JAR_1047.csv` SHA256: `9a36861c53e6508f8082a1a2b845e36e6c5d76f44dd1918b3b8e151ae06eaebd`.

## Recenzja historycznych tlumaczen API

Nowe **38** niepowtarzajacych sie recenzji semantycznych offline:
- **12** DRAFT/OPTIONAL komunikatow numerycznych branzy przemyslowej, zgodnych z poprawkami 1.0.47. Dwa pozostale poprawione wiersze mialy juz inny status niz DRAFT i nie podnosza licznika 3658.
- **26** istniejacych przyciskow/opcji ekranow interakcji z flota. Na oryginalnej klasie `FleetInteractionDialogPluginImpl` potwierdzono 32 instrukcje korzystajace z `OptionPanelAPI.addOption`. Nalezy do nich m.in. `Join the battle`, `Take command of the action`, `Open a comm link` oraz `Perform limited emergency repairs` — wszystkie posiadaja polskie odpowiedniki w mapie. W recenzji sprawdzono konkretne znaczenia tych tekstow, nie deklaruje sie testu renderowania w grze.

Rejestr `docs/API_SEMANTIC_REVIEW_1047.json` jest dopisywany do 142 wczesniejszych, zachowanych bajtowo rekordow: **180/3658 offline reviewed**, **3478 historycznych wierszy** do dalszej oceny. Etap nie usuwa z mapy angielskich identyfikatorow i nie zmienia etykiet DRAFT (patcher faktycznie instaluje te teksty).

## Audyt niebezpiecznej kolizji `her` — bez ryzykownej podmiany

Oryginalna klasa `BaseBarEventWithPerson` uzywa tego samego `CONSTANT_String` **#143 = `her`** w metodach `getHimOrHer()` (dopelnienie) oraz `getHisOrHer()` (dzierzawczy). Polszczyzna wymaga odmiennych form, wiec globalna podmiana tej stalej jest **niebezpieczna**. Przy dotychczasowym wymaganiu braku zmian instrukcji JVM sam patcher oparty na mapie literałow nie potrafi rozdzielic referencji `ldc #143` miedzy dwiema metodami. Nie podjeto pozornej naprawy — problem zostaje otwarty (issue #4). Odtwarzalny audyt: `tools/audit_1047_jvm.py`, raport `docs/JVM_ORIGINAL_1047_SUMMARY.json`.

## Oryginalne biblioteki — niezalezny test rzeczywistej instalacji

Na lokalnych kopiach oryginalnych JAR o sprawdzonych SHA256, zbudowanymi patcherami Go Linux, sprawdzono:

| Test | Wynik |
|---|---|
| Oryginalny API, świeże patchowanie 1.0.47 | PASS |
| 1.0.46 -> 1.0.47 na **juz spatchowanym API** | PASS, wynik bajtowo identyczny z fresh |
| OBF: 539 zmodyfikowanych klas | PASS, bez zmian względem 1.0.46 |
| API: 938 zmodyfikowanych klas od oryginalu | PASS |
| API: 11 zmodyfikowanych klas miedzy 1.0.46 a 1.0.47 | PASS, wszystkie oczekiwane |
| Wykonywalny bajtkod metod w zmodyfikowanych klasach | Identyczny |
| Ponowne uruchomienie patchera 1.0.47 | PASS — no-op |
| Celowo zmieniona metadana ZIP spatchowanego JAR | Odrzucona bez nadpisania |
| Przywrócenie obu oryginalnych bibliotek | PASS, bajtowo identyczne |

Hash API po 1.0.46: `581ebc605139ccf9a35ebe3c191e495c4664a255714756577b16d4361741d886`.

Hash API po 1.0.47: `98cc36aec4aa87e37717082469704f973ad7a91f51b7d0222a10a18770e2a277`.

Szczegolowy niekomercyjny raport w `docs/UPGRADE_1047.json`; skrypt `tools/private_upgrade_1047.py`. Oryginalne JAR **nie zostaly opublikowane**.

## Automatyczna walidacja i reprodukcja

Po `tools/restore_snapshot.py`, a nastepnie wszystkich overlayach 1013–1046, w nowym worktree:

```sh
python3 tools/apply_1047.py worktree
python3 tools/verify_1047.py worktree
python3 tools/test_1047.py worktree
python3 tools/verify_review_1047.py worktree --previous docs/API_SEMANTIC_REVIEW_1046.json --ledger docs/API_SEMANTIC_REVIEW_1047.json
python3 tools/check_release_gates_1047.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/API_SEMANTIC_REVIEW_1046.json --ledger docs/API_SEMANTIC_REVIEW_1047.json
python3 tools/test_release_gates_1047.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/API_SEMANTIC_REVIEW_1046.json --ledger docs/API_SEMANTIC_REVIEW_1047.json
(cd worktree && sh build_windows.sh)
python3 tools/package_1047.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.47_MINIMALNY.zip
```

Lokalnie przeszly 42 warianty liczebnikow (14 tekstow x 1,2,5) i 9 testow negatywnych. Poprzedni mapping i wszystkie pola nie-`polish_ascii_draft` pozostaja bez zmian. Scisly test oryginalnego JAR wymaga lokalnych licencjonowanych bibliotek; nie mozna go uruchamiac w publicznym CI bez nich. GitHub Actions bezpiecznie testuje projekt, kompilacje Go, format Windows EXE i pakowanie, ale nie zastępuje uruchomionej gry Windows.

## Pozostale bramki 1.1

- **3478** historycznych API DRAFT/OPTIONAL do recenzji; 180/3658 sprawdzonych offline.
- **186** nierozpatrzonych wywolan getterow zaimkowych Java, w tym kolizja `her` #143.
- **2275** surowych wystapien zaimkow w 1139 rekordach `rules.csv` pozostalo po 1.0.45; wymagaja oceny, nie sa automatycznie 2275 bledami.
- **253** poprawione rekordy dialogow oraz 81 kontekstow PF nadal wymagaja testow wizualnych w grze Windows; nowe 14 komunikatow branzy gospodarczej oraz 26 opcji rowniez bez natywnych testow.
- Brak kompletnego przegladu wszystkich tekstow gracza i natywnych testow rozgrywki. **Nie oznaczac jako 1.1.**
