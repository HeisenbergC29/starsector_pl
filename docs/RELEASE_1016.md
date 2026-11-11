# Starsector PL 1.0.16 — wydanie robocze (2026-11-11)

**Gra:** Starsector 0.98a-RC8. **Wersja 1.1 nie jest jeszcze ukonczona.**

## Tlumaczenia od 1.0.15

- OBF +4: podpowiedz filtrow planet (zachowano `{{Ctrl-S}}`), objaśnienie dostawcy w tabeli towarow, ostrzezenie o pamieci w launcherze, komunikat uszkodzenia zapisu.
- API +17: 7 nazw okretow Ligi (bez zmieniania imion i nazwisk), 3 opcje generatora floty, 7 fragmentow dialogow i opisow postaci (historyk, naukowiec i rolnik luddystyczny).
- Dla dlugich tekstow zachowano oryginalne znaczniki formatowania, liczbe nowych linii i strukture polaczonych fragmentow tekstu.
- W `mod/data/` **870/870 plikow jest identycznych bajtowo z 1.0.15**.

## Rzeczywiste wyniki testow lokalnych (Linux + oryginalne JAR uzytkownika)

| Kontrola | Wynik |
|---|---|
| SHA-256 obu oryginalnych JAR zgodne z 0.98a-RC8 | PASS |
| OBF: 3125 podmian `CONSTANT_String`, 527 klas | PASS |
| API: 5092 podmiany `CONSTANT_String`, 934 klasy | PASS |
| Audyt klasy po klasie wzgledem oryginalu, brak zmian bajtkodu metod | PASS |
| OBF: 527 sekcji sum kontrolnych manifestu poprawnie przepisanych | PASS |
| Pozostale pozycje JAR niezmienione: OBF 2400, API 2606 | PASS |
| Instalacja na swiezych bibliotekach | PASS |
| Aktualizacja OBF i API z 1.0.15 do 1.0.16 | PASS |
| Ponowne uruchomienie patcherow bez zmiany wynikowych SHA | PASS |
| Przywracanie obu oryginalnych JAR | PASS |
| Odrzucanie dwoch celowo uszkodzonych JAR bez nadpisywania | PASS |
| Powtorne odtworzenie 121 plikow z overlay | PASS |
| Go test/vet OBF, API, instalator | PASS |
| Cross-kompilacja 3 PE32+ EXE Windows x64 | PASS |
| `rules.csv`: 7371/7371 opcji poprawnych | PASS |
| ZIP: 873 wpisy, 870 data, CRC i struktura poprawne | PASS |
| Natywny Windows / uruchomienie gry | NIE TESTOWANO |

**Nowy SHA-256 OBF:** `c3dcae2341f5fa96cb92b6a1cb1a59ec5f32cdf4579f77fe5ad30985764ee78c`

**Nowy SHA-256 API:** `340ba4eeda9b560224a0661d6766699009a3985a4822d53bc0ae08144613ae81`

**ZIP:** `Starsector_PL_ASCII_0.98a_RC8_1.0.16_MINIMALNY.zip`

- Rozmiar **10 941 417 bajtow**.
- SHA-256: `af214cba2a8c96029437bfb1d03d08a6fa26aec52fd2af70012999759e4d8297`
- ZIP i `Starsector_PL_1.0.16_TESTY.json` sa w prywatnej Bibliotece projektu.
- Oryginalnych JAR i `data.rar` nie ma w publicznym repo.

## Odtwarzanie stanu z GitHuba

```sh
python3 tools/restore_snapshot.py
python3 tools/apply_1013.py worktree
python3 tools/apply_1014.py worktree
python3 tools/apply_1015.py worktree
python3 tools/apply_1016.py worktree
python3 tools/check_project.py worktree/mod
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
```

Snapshot bazowy z `snapshots/` to 1.0.12. Nowsze zmiany sa niezaleznymi, deterministycznymi overlayami. Mapy historyczne zostaja na potrzeby aktualizacji.

## Nadal otwarte do celu 1.1

- Pelna klasyfikacja pozostałych literałów Java i pol widocznych z `data/`, z uwzglednieniem nazw zwyczajowych, pseudonimow i skrotow z polskimi rozwinieciami.
- Przeglad skladowych tekstow dynamicznych z uwzglednieniem odmiany zaimkow / rodzaju.
- Audyt etykiet `DRAFT_ONLY_NOT_INSTALLED` i `OPTIONAL_PATCHER_NOT_GAME_TESTED`: etykieta statusu NIE blokuje instalacji.
- Test uruchomienia gry i instalatora w Windows (w tym regresja `rules.csv` z 1.0.9).

**Nie twierdzic, ze 1.1, 100% polonizacji lub test w uruchomionej grze sa zakonczone.**
