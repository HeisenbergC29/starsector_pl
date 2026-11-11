# Starsector PL 1.0.13 — wydanie robocze, 2026-11-11

**Zgodnosc:** Starsector 0.98a-RC8, Windows x64. **Nie jest to ukonczona lokalizacja 1.1.**

## Zmiany w stosunku do 1.0.12

- 15 nowych tlumaczen opisow wyswietlanych przez JAR API (klasy tooltipow): distress call, neutrino detector / slipstreams, pirate protection, Luddic Church events, hyperspace topography, Tri-Tachyon commerce raiding oraz hullmods Converted Hangar, High Resolution Sensors, Neural Interface i Phase Field.
- 870 plikow data pozostalo bajtowo identycznych z 1.0.12.
- OBF 3116 podmian w 526 klasach — bez zmian.
- API 5057 rekordow mapy, 5055 faktycznych podmian w 931 klasach. Nowa mapa 1013 zachowuje starsza mape 1010 do autentykacji podmian i aktualizacji.
- Instalator i metadane wersji: 1.0.13.

## Testy faktycznie wykonane lokalnie w Linuxie

| Scenariusz | Wynik |
|---|---|
| OBF: preview, install, repeat, restore na oryginalnym starfarer_obf.jar | PASS |
| API: preview, install, repeat, restore na oryginalnym starfarer.api.jar | PASS |
| API: instalacja 1010 -> preview 1013 -> install 1013 -> restore | PASS |
| Go tests / vet OBF, API, instalator | PASS |
| Cross-build 3 PE32+ Windows x64 | PASS |
| 7371 / 7371 opcji rules.csv, brak niepoprawnych | PASS |
| ZIP integralnosc, 873 wpisy, 870 plikow data | PASS |
| Porownanie danych mod 1.0.13 z ZIP 1.0.12, 870 / 870 identyczne | PASS |
| Test natywny Windows i uruchomienie Starsector | NIE URUCHAMIANO |
| Pelne 100% tlumaczenia i estetyka tekstow in-game | NIE POTWIERDZONO |

Oryginalne SHA-256 JAR w testach:
- OBF: `5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8`
- API: `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`

ZIP: `Starsector_PL_ASCII_0.98a_RC8_1.0.13_MINIMALNY.zip`
- Rozmiar: **10 082 424 B**
- SHA-256: `07308708c90af2864a75508b4b72428f7d49b4090d853d72c1c4c8e11323ce59`
- Uzytkownik ma ZIP i JSON raportu w prywatnej Bibliotece projektu.

## Odtwarzanie z GitHub

```sh
python3 tools/restore_snapshot.py
python3 tools/apply_1013.py worktree
python3 tools/check_project.py worktree/mod
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
```

**Uwaga:** migawka w `snapshots/` to 1.0.12. Aktualne zmiany 1.0.13 sa deterministycznym overlay z `tools/apply_1013.py`. Zarowno materialy komercyjne gry, jak i oryginalne JAR zostaja poza publicznym repozytorium.

## Otwarte

- Issue #1: test Windows i test w grze (w tym regresja dawnego bledu 1.0.9).
- Issue #2: pelny audyt tekstow widocznych, nazw i skrotow, wariantow tekstow dynamicznych.
- Issue #3: kolumna `status` nie blokuje wpisow `DRAFT_ONLY_NOT_INSTALLED`, nadal potrzebna weryfikacja kontekstow.
