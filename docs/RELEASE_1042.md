# Starsector PL ASCII 1.0.42 — usuniecie podwojnych kropek po skrotach

**Data:** 2026-11-13  
**Gra:** Starsector 0.98a-RC8  
**Poprzednie wydanie:** 1.0.41; commit `b54454852d12fd943417a0a94ac670913ce85865`  
**Status:** poprawka 1.0.42 wykonana i zweryfikowana offline. **Nie jest to kompletna wersja 1.1.**

## Wykryta regresja z 1.0.41

Wersja 1.0.41 zastapila stale formy liczby mnogiej skrotami `jedn.`, `pkt` i `l. sw.`, zeby liczba `%s` mogla wynosic 1 lub wiecej. W 15 miejscach poprzedni tekst mial juz kropke na koncu zdania. Po zamianie powstalo `jedn..` i `l. sw..` — blad ujawniony pelnym audytem wszystkich 5257 tekstow API.

W `TLUMACZENIA_JAR_1042.csv` naprawiono dokladnie:

- **11 ×** `%s jedn..` → `%s jedn.`;
- **4 ×** `%s l. sw..` → `%s l. sw.`.

To 15 zmian w 15 klasach (m.in. `ItemEffectsRepo`, `Mining`, `GraviticScanAbility`, `DiktatLobsterBarEvent`). W zadnej innej klasie, statusie, angielskim literale, identyfikatorze technicznym ani w bajtkodzie nie wprowadzono zmian. Pozostale 5242 wpisy mapy sa bajtowo zgodne z 1.0.41. Nie poprawiano przy tym innych bledow leksykalnych lub gramatycznych wymagajacych kontekstu.

## Sprawdzone wyniki

| Kontrola | Wynik |
| --- | --- |
| Mapy API 1.0.41 → 1.0.42 | 5257 wierszy, dokladnie 15 zmian, 0 pozostawionych podwojnych kropek |
| Dokladny, niezmienny plan zmian | SHA-256 `fc7bf29cfc7f327342060c7a6eb36f3662d72d2cd097431c6141c9b32ff2a761` |
| Oryginalny oraz spatchowany `starfarer.api.jar` | 5255 podmian `CONSTANT_String` w 938 klasach; niezmieniony wykonywalny kod JVM |
| Swieza instalacja oraz rzeczywista aktualizacja 1.0.41 → 1.0.42 | Identyczny JAR (`ae2cfb7b…cf4`) |
| Ponowne uruchomienie patchera | Bez zmian |
| Przywracanie oryginalnej biblioteki | Identyczny SHA-256 oryginalu |
| Celowo uszkodzone metadane ZIP z prawidlowymi payloadami | Odrzucone bez nadpisania uszkodzonego JAR i backupu |
| Testy negatywne mapy | 14/14 PASS |
| Testy negatywne bramek wydania 1.1 | 14/14 PASS |
| `rules.csv` | 7371 poprawnych opcji, 0 bledow |
| Go test/vet, 3 programy Windows x64 | PASS |
| 870 plikow `data/` | Identyczne z 1.0.41 |
| Instalator EXE | Zawiera dokladnie skompilowane, aktualne `obf_windows.exe` i `api_windows.exe` (porownanie bajtowe) |
| ZIP | 873 wpisy, CRC PASS, bez oryginalnych komercyjnych JAR |

**Oryginalny API SHA-256:** `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`  
**API po 1.0.42 SHA-256:** `ae2cfb7bda28b58e20bd31976e1f399174c9eab564f5b98c192f2464ecf3bcf4`  
**OBF bez zmian:** `03729bc8e6ad0100ce4d0f7bf2f71bc198f917ff9e1b2fa5f9dacf4f35960a7a`  
**Wydanie ZIP SHA-256:** `514129a508e2e39851c569170ba21bd5aa93d2c02e1f4dddafc145f8aa3f027d` — **16 468 322 bajty**.

## Odtwarzanie

Po odtworzeniu snapshotu 1.0.12 i zastosowaniu nakladek 1013–1041 w kolejnosci:

```bash
python3 tools/apply_1042.py worktree
python3 tools/verify_1042.py worktree
python3 tools/test_1042.py worktree
python3 tools/check_release_gates_1042.py worktree --gates docs/RELEASE_GATES_11.json
python3 tools/test_release_gates_1042.py worktree --gates docs/RELEASE_GATES_11.json
(cd worktree && sh build_windows.sh)
python3 tools/package_1042.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.42_MINIMALNY.zip
```

Dodatkowe, wymagajace **prywatnego oryginalnego JAR** testy nie sa odtwarzane w publicznym GitHub Actions:

```bash
python3 tools/verify_1042.py worktree \
  --original-api /sciezka/do/starfarer.api.jar.oryginal \
  --patched-api /sciezka/do/starfarer.api.jar.po_1042
python3 tools/test_noop_integrity_1042.py \
  --exe /sciezka/do/api_linux \
  --original-api /sciezka/do/starfarer.api.jar.oryginal \
  --patched-api /sciezka/do/starfarer.api.jar.po_1042 \
  --obf /sciezka/do/starfarer_obf.jar
```

## Warunki do pelnego 1.1

**Wersja 1.0.42 nie rozwiazuje dotychczasowych blokad:** 186 wywolan getterow zaimkow i konflikt wspoldzielonego `her`, 3536 historycznych tlumaczen API do pelnego przegladu znaczenia, 81 kontekstow `Misc.STORY` oraz 153 przeredagowane dialogi oczekujace na test w dzialajacej grze Windows. Nowe 15 poprawek interpunkcji takze wymagaja wizualnego potwierdzenia. Zadnych takich testow Windows gameplay nie przeprowadzono. Wszystkie te bramki pozostaja otwarte.
