# Starsector PL ASCII 1.0.48 — odmiana liczebnikow w tekstach Java API

**Data:** 2026-11-13  
**Gra:** Starsector 0.98a-RC8  
**Baza:** 1.0.47; `TLUMACZENIA_JAR_1047.csv` SHA256 `9a36861c53e6508f8082a1a2b845e36e6c5d76f44dd1918b3b8e151ae06eaebd`.  
**Nowa mapa:** `TLUMACZENIA_JAR_1048.csv` SHA256 `2f85b133be0d3087321d16dd71080f5214cf9e2932cc60381ecbab521b273289`.  
**Status:** 1.0.48, nie ukonczona polonizacja 1.1. ASCII w plikach gry; nie zmieniano algorytmow ani danych gry.

## Zakres prac

Poprawiono 29 aktywnych wierszy mapy Java API w 19 klasach, zachowujac bez zmian 5260 angielskich kluczy, przypisanie klas, statusy DRAFT/OPTIONAL i identyfikatory. Problem dotyczy dynamicznie podstawianych liczb: **1 kredytow, 1 dniach, 1 punkt** sa niepoprawne. Wybrano jednoznaczne skroty ASCII `kred.`, `dn.`, `pkt`, `os.`, `okr.`, `s`, pozwalajace uniknac blednej odmiany po 1/2/5. W komunikacie stabilizacji kolonii przestawiono cale zdanie z powodu niepoprawnej skladni `z ... punktami`.

Zweryfikowane obszary to: wynagrodzenia oficerow, zalogi i marines w raporcie miesiecznym; czas bombardowania, zaklocen i zlecen; czasowy bonus wolnego rynku; zlecenia dostawy; kredyty; pojemnosc zalogi; stabilizacja kolonii i niepokoje; zadanie samouczka; opisy `ConvertedHangar`, `PhaseField`, `ShroudedThunderheadHullmod`.

Przyklady (teksty wewnatrz gry to polski ASCII):

| Typ | Wczesniej | W 1.0.48 |
| --- | --- | --- |
| Pensje | `%s kredytow miesiecznie` | `%s kred. miesiecznie` |
| Wplyw na kolonie | `po %s dniach` | `po %s dn.` |
| Niepokoje | `maleje o %s punkt` | `maleje o %s pkt` |
| Pojemnosc floty | `jeszcze %s osob.` | `jeszcze %s os.` |
| Okrety fazowe | `%s okretow fazowych` | `%s okr. fazowych` |
| Impulsy burzowe | `ostatnich %s sekund` | `ostatnich %s s` |

Przeglad kontekstowy przeprowadzono na wszystkich 29 calych stringach, a nie tylko na samej frazie. Pozostale teksty / klasy nie zostaly automatycznie przepisywane. Nie dodano zadnej nowej klasy do mapy.

## Semantyczny rejestr API

- **23** nowo zrecenzowane historyczne wiersze DRAFT/OPTIONAL w mapie API (kazdy potwierdzony w oryginalnym JVM constant pool).
- **3** historyczne wiersze juz zrecenzowane zostaly ponownie poprawione; ich stare hashe sa jawnie zachowane w polach `superseded_1047_row_sha256`, nie liczone ponownie.
- **3** inne poprawione teksty mialy starszy status `VERIFIED_TOOLTIP_CALLSITE`/`REVIEWED_UI_CALLSITE`, poza historyczna pula DRAFT; rowniez nie podwyzszaja jej licznikow.
- Stan: **203/3658** historycznych wpisow ma recenzje offline; **3455** pozostaje bez niej. Dokument `docs/API_SEMANTIC_REVIEW_1048.json`, deterministyczny walidator `tools/verify_review_1048.py`.

## Wyniki testow na oryginalnych JAR

- `tools/audit_original_1048.py`: wszystkie **29/29** angielskich literałów sprawdzone jako dokladne `CONSTANT_String` w **19** klasach oryginalnego `starfarer.api.jar` 0.98a-RC8.
- `tools/verify_1048.py`: nienaruszona liczba 5260 mapowan, dokladnie 29 zmienionych pol tlumaczenia, stare i nowe SHA-256, wersje Go i instalatora, struktura 870 plikow danych (wszystkie bajtowo identyczne z 1.0.47).
- `tools/test_1048.py`: **87** podstawien numerycznych 1/2/5; **8** kontrolowanych blednych modyfikacji odrzuconych. Prosze nie mylic symulacji podstawienia z rzeczywista kontrola w wyswietlanym GUI.
- Rzeczywista **aktualizacja API JAR 1.0.47 -> 1.0.48** (Go patcher na Linuxie, prywatne oryginalne JAR): wynik ze starego spatchowanego JAR jest bajtowo identyczny ze swieza instalacja 1.0.48. Dokladnie **19** klas zmienilo swoje literały miedzy wersjami; cala pozostala struktura klas i kod wykonywalny Java nie sa zmienione.
- Ponowna instalacja 1.0.48 (idempotencja), odmowa spatchowania JAR z naruszona metadana ZIP, a takze przywrocenie obu oryginalnych JAR: **PASS**.
- OBF nadal ma 3534 trafienia w 539 klasach bez zmian. Nowy wynik API 1.0.48: **SHA256 `65c308e455cdc2edadebab4af2a7ec1b6081c774826dd5e5074b7d5b6d12d1d7`**, 938 zmodyfikowanych klas od oryginalu.
- Logi bez oryginalnych komercyjnych bibliotek: `docs/UPGRADE_1048.json` i `docs/JVM_ORIGINAL_1048_SUMMARY.json`. Nie przechowuje sie prywatnych JAR-ow w repozytorium.
- Kompilacja trzech Windows EXE, integralnosc zintegrowanych patcherow i paczka minimalna pozostaja testami GitHub Actions; powyższe testy Linux same w sobie nie oznaczaja sukcesu CI.

## Krytyczna blokada 1.1: `her`

Niezalezna analiza `BaseBarEventWithPerson.getHimOrHer()` oraz `getHisOrHer()` ponownie potwierdzila wspolny literal `her` w puli JVM (#143), wykorzystywany przez dwie formy gramatyczne. Prosta globalna podmiana stalej nie jest bezpieczna. **186** oryginalnych callsite getterow Java pozostaje do recenzji, bez zmian w tym wydaniu. 81 kontekstow PF, 253 wczesniej zrecenzowane dialogi, pozostale surowe zmienne w rules.csv i wszystkie teksty 1.0.48 wymagaja natywnego testu w grze Windows.

## Reprodukcja

Po odtworzeniu 1.0.47 z publicznego GitHuba:

```bash
python3 tools/apply_1048.py worktree --report /tmp/NUMERIC_DELTA_1048.json
python3 tools/verify_1048.py worktree
python3 tools/test_1048.py worktree
python3 tools/verify_review_1048.py worktree --previous docs/API_SEMANTIC_REVIEW_1047.json --ledger docs/API_SEMANTIC_REVIEW_1048.json
python3 tools/check_release_gates_1048.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/API_SEMANTIC_REVIEW_1047.json --ledger docs/API_SEMANTIC_REVIEW_1048.json
python3 tools/test_release_gates_1048.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/API_SEMANTIC_REVIEW_1047.json --ledger docs/API_SEMANTIC_REVIEW_1048.json
(cd worktree && sh build_windows.sh)
python3 tools/package_1048.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.48_MINIMALNY.zip
```

**Nie oznaczac jako 1.1 bez pelnego audytu i uruchomionej gry Windows.**
