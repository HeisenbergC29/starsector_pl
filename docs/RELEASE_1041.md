# Starsector PL ASCII 1.0.41 — kontrolowane poprawki liczebników i integralności instalatora

**Data:** 2026-11-13  
**Gra:** Starsector 0.98a-RC8  
**Bazowe wydanie:** 1.0.40, commit `322742237d46971a644150a957ba3578bae7c20b`  
**Status:** wydanie techniczne 1.0.41; **nie** oznacza ukończenia lokalizacji 1.1.

## Wdrożone poprawki

1. **77 aktywnych mapowanych tekstów API w 59 klasach**: sztywne formy mnogie po numerycznym `%s` zostały zastąpione jednoznacznymi skrótami polskimi ASCII. Podział:
   - 40 × `%s jednostek` → `%s jedn.`;
   - 25 × `%s punktow` → `%s pkt`;
   - 12 × `%s lat swietlnych` → `%s l. sw.`.
   Skrypty kontrolne wymagają zachowania liczby `%s`, otaczających spacji oraz wszystkich identyfikatorów, oryginalnych literałów i statusów. Zmiana dotyczy odmiany **wskazanych 77 miejsc**, nie pełnej recenzji znaczenia zdań.
2. **Naprawa błędu instalatora API na już spatchowanym JAR-ze**: gdy 1.0.41 zostaje rozpoznana po zawartości, przed komunikatem „Version already installed” porównywany jest również SHA-256 **wszystkich bajtów JAR** z biblioteką wygenerowaną od oryginału. To odrzuca archiwum o zmienionych bajtach nagłówków ZIP, nawet gdy jego wewnętrzne wpisy nadal dają te same rozpakowane dane. Nie nadpisuje uszkodzonego pliku ani zweryfikowanej kopii zapasowej.
3. Aktualizacja identyfikatorów Go patchera API i wspólnego instalatora, dokumentów paczki i numeru `mod_info.json`. Patchery OBF i wszystkie **870 plików `data/`** są niezmienione względem 1.0.40.

## Wyniki weryfikacji

| Sprawdzany obszar | Potwierdzony wynik |
| --- | --- |
| API `TLUMACZENIA_JAR_1041.csv` | 5257 wierszy, 77 zmian, 59 klas |
| Zmiany w `starfarer.api.jar` | 5255 tekstów w 938 klasach |
| Zmiany wykonywalnego bajtkodu Java | **0** — porównanie 938 klas po puli stałych |
| Aktualizacja 1.0.40 → 1.0.41 | Identyczna suma JAR jak przy czystej instalacji |
| Ponowna instalacja prawidłowej 1.0.41 | Bez zmian |
| Niewłaściwy JAR: zmiana bajtu metadanych ZIP | **Odrzucony bez nadpisania**, mimo prawidłowego odczytu i CRC danych |
| Przywracanie oryginalnego JAR | Oryginalne SHA-256 potwierdzone |
| Testy negatywne mapy | 14/14 odrzuconych błędnych modyfikacji |
| Testy negatywne bramek 1.1 | 14/14 odrzuconych fałszywych potwierdzeń |
| `rules.csv` | 7371 opcji, **0** błędów |
| Narzędzia Go | `go test` i `go vet` na 3 komponentach: PASS |
| Kompilacja Windows | 3 × PE32+ x86-64: PASS |
| Paczka ZIP | 873 wpisy, CRC PASS, 870 plików danych, **bez komercyjnych oryginalnych JAR** |

### Sumy kontrolne (SHA-256)

- Oryginalny `starfarer.api.jar`: `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`
- API po 1.0.41: `be752bc07ca3965435ad34bab2e12febd80a7883818a430d8c007999b562e5c9`
- OBF pozostawiony na 1.0.40: `03729bc8e6ad0100ce4d0f7bf2f71bc198f917ff9e1b2fa5f9dacf4f35960a7a`
- Plan dokładnie 77 wierszy: `8edfe27a4ce166d1dad5be44555ccdd13346b7f48c97013051be4321ea30456f`
- **Końcowa** paczka `Starsector_PL_ASCII_0.98a_RC8_1.0.41_MINIMALNY.zip`: `ca780e8d6ca4e3ccbfba385c94d7508f25c58c4c3e740b5023d0fa902ef4e2d1` (**16 256 610 bajtów**).

**Uwaga o paczce:** pierwsza lokalna kompilacja ZIP zawierała wcześniejszy instalator (sprzed zabezpieczenia SHA). Weryfikacja porównująca wszystkie wpisy dwóch ZIP-ów wykazała różnicę wyłącznie w `Starsector_PL_Instalator.exe`. Pakiet został **przebudowany** z poprawionym plikiem EXE i po tej przebudowie uzyskał powyższą końcową sumę. Test potwierdził bajtową identyczność EXE w końcowym ZIP z przetestowanym, zaktualizowanym instalatorem. **Nie udostępniać wcześniejszego ZIP z SHA `81cee23f4888e5fc7f6b9776097a987bbf8802144440047487ba813af8fc1e22`.**

## Powtarzalne narzędzia

Po odtworzeniu snapshotu 1.0.12 oraz zastosowaniu nakładek 1013–1040, uruchomić:

```bash
python3 tools/apply_1041.py worktree
python3 tools/verify_1041.py worktree
python3 tools/test_1041.py worktree
python3 tools/check_release_gates_1041.py worktree --gates docs/RELEASE_GATES_11.json
python3 tools/test_release_gates_1041.py worktree --gates docs/RELEASE_GATES_11.json
(cd worktree && sh build_windows.sh)
python3 tools/package_1041.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.41_MINIMALNY.zip
```

Dodatkowy test **wyłącznie na lokalnych, legalnie dostępnych oryginalnych JAR-ach** (nie są częścią repozytorium):

```bash
python3 tools/verify_1041.py worktree \
  --original-api /sciezka/do/oryginalnego/starfarer.api.jar \
  --patched-api /sciezka/do/starfarer.api.jar.po_1041 \
  --previous-zip /sciezka/do/paczki_1040.zip
python3 tools/test_noop_integrity_1041.py \
  --exe /sciezka/do/skompilowanego/api_linux \
  --original-api /sciezka/do/oryginalnego/starfarer.api.jar \
  --patched-api /sciezka/do/starfarer.api.jar.po_1041 \
  --obf /sciezka/do/starego_lub_spatchowanego/starfarer_obf.jar
```

## Stan wymagany przed wydaniem 1.1

- **186 z 219** kontekstów getterów Java nadal wymaga audytu językowego; współdzielone `her` w dwóch bazach wydarzeń nadal otwarte.
- **3536** historycznych tekstów API nadal bez pełnej recenzji semantycznej. Żaden z 77 skrótów nie jest automatycznie zaliczony do tego licznika.
- 81 kontekstów PF i 153 poprawione dialogi czekają na wizualne sprawdzenie w działającej grze Windows.
- Wszystkie 77 nowych poprawek liczebników wymagają późniejszego testu wyświetlania w grze.
- **Brak natywnego testu rozgrywki Windows**. Cross-kompilacja i testy strukturalne nie są tym samym.
