# Build / walidacja

Wymagania: Python 3, Go, zstd, tar. `python3 tools/restore_snapshot.py` tworzy katalog `worktree`.

```bash
python3 tools/restore_snapshot.py
python3 tools/apply_1013.py worktree
python3 tools/apply_1014.py worktree
python3 tools/apply_1015.py worktree
python3 tools/apply_1016.py worktree
python3 tools/apply_1017.py worktree
python3 tools/apply_1018.py worktree
python3 tools/apply_1019.py worktree
python3 tools/apply_1020.py worktree
python3 tools/verify_1020_dialogs.py worktree
python3 tools/apply_1021.py worktree
python3 tools/verify_1021_delta.py worktree
python3 tools/apply_1022.py worktree
python3 tools/verify_1022_names.py worktree
python3 tools/test_1022_names.py
python3 tools/apply_1023.py worktree
python3 tools/verify_1023_ui.py worktree
python3 tools/test_source_fields_1021.py
python3 tools/verify_1019_tooltip.py worktree
python3 tools/verify_subject_pronouns_1018.py worktree
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
cd worktree
(cd buildtools/NARZEDZIA_OBF && GO111MODULE=off go test ./... && GO111MODULE=off go vet ./...)
(cd buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO && GO111MODULE=off go test ./... && GO111MODULE=off go vet ./...)
sh build_windows.sh
(cd buildtools/NARZEDZIA_INSTALATOR && GO111MODULE=off go test ./... && GO111MODULE=off go vet ./...)
file obf_windows.exe api_windows.exe Starsector_PL_Instalator.exe
```

**Wazne:** testy instalatora wymagaja istnienia `buildtools/NARZEDZIA_INSTALATOR/bin/{api,obf}.bin` osadzanych przez `//go:embed`. `build_windows.sh` tworzy je po cross-kompilacji. Samo `go test` instalatora przed tym etapem moze zakonczyc sie bledem o brakujacych plikach bin.

Paczka gracza: zawartosc `worktree/mod/` + `worktree/Starsector_PL_Instalator.exe`, z katalogiem glownym `Starsector_PL_ASCII/`. Nie wkladaj do ZIP zrodel, raportow, testow ani oryginalnych JAR. W ZIP 1.0.23 jest 870 plikow data + mod_info.json + CZYTAJ.txt + EXE = 873. Wszystkie 870 danych pozostaja identyczne z 1.0.22, nowa mapa OBF 10123 zawiera +41 etykiet UI, nowa mapa API 1023 ma +26. Testy oryginalnych JAR i pelnej gry sa osobne.

Testy instalacji na oryginalnych JAR i natywny Windows wymagaja osobnych, rzeczywistych uruchomien.

**Stan zrodel:** `tools/restore_snapshot.py` odtwarza z GitHub wersje bazowa 1.0.12. `tools/apply_1013.py worktree`, `tools/apply_1014.py worktree` oraz `tools/apply_1015.py worktree`, `tools/apply_1016.py worktree` oraz `tools/apply_1017.py worktree`, `tools/apply_1018.py worktree` oraz `tools/apply_1019.py worktree` oraz `tools/apply_1020.py worktree` oraz `tools/apply_1021.py worktree` oraz `tools/apply_1022.py worktree` i `tools/apply_1023.py worktree` sa niezbedne, by uzyskac 1.0.23. Nigdy nie dystrybuuj oryginalnych JAR.
