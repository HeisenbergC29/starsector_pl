# Starsector PL 1.0.23 — wydanie robocze (2026-11-11)

**Zgodność:** Starsector 0.98a-RC8. **Cel pełnej lokalizacji 1.1 NIE jest ukończony.**

## Co przetłumaczono

**67 nowych, rzeczywiście różniących się tekstów** w oryginalnych bibliotekach Java: **41 OBF** oraz **26 API**. Wszystkie nowe angielskie literały występują w `CONSTANT_String` komercyjnych JAR o zweryfikowanych sumach SHA-256; ich użycia sprawdzono w odpowiadających klasach Java przez `javap`. Pseudonimy, imiona, techniczne ID i bajtkod nie były ruszane.

| Grupa UI i klasa Java | OBF | API |
|---|---:|---:|
| `CargoTooltipFactory` — szczegóły uzbrojenia i ładunków, np. Accuracy/Ammo/Charges/Hitpoints | 16 | – |
| `CommodityDetailDialog` — nagłówki gospodarcze i przycisk zamknięcia | 7 | – |
| `CommodityDetailDialogV2` — producenci, odbiorcy, ilości, dostęp | 10 | – |
| `CodexDetailPanel` — nagłówki kodeksu | 6 | – |
| `EconomyOverviewPanel` — napływ/wypływ | 2 | – |
| `SimulatorPluginImpl` — etykiety ustawień symulatora, zachowanie SI | – | 14 |
| `CRPluginImpl` — określenia gotowości i ryzyka awarii | – | 7 |
| `CoreReputationPlugin` — końcówka informacji o niezmienionej reputacji | – | 1 |
| `ToggleAbilityWithCost` — dodatkowy wariant składanej podpowiedzi gotowości bojowej | – | 1 |
| `BaseIndustry` — etykiety ulepszeń, przedmiotów, produkcji | – | 3 |
| **Razem** | **41** | **26** |

Zgodnosc odmiany: `Perfect` w opisie celnosci broni ma poprawna forme `Idealna` (nie `Idealne`).

Nie dodano zerowej podmiany `Administrator` → `Administrator` (poprawna już forma polska). **Celowo nie tłumaczono** `HIGH`, `LOW`, `EXTREME` itd. używanych jako techniczne nazwy stałych enum, mimo że w pobliżu występują etykiety widoczne dla gracza.

W `ToggleAbilityWithCost` zidentyfikowano dwa różne źródłowe literały różniące się końcową spacją: jeden był tłumaczony w 1.0.19, drugi nie. Dodano drugi wariant i przetestowano wynik po połączeniu trzech fragmentów: `Zmniejsza gotowosc bojowa wszystkich okretow...`, bez podwójnych spacji.

## Integralność i aktualizacja (testy lokalne na oryginalnych JAR, Linux)

| Kontrola | Wynik |
|---|---|
| OBF: **3185** podmian, **533** zmienione klasy | PASS |
| API: **5132** podmiany, **936** zmienionych klas (5134 wiersze CSV; 2 historyczne wiersze nie wskazują obecnej klasy w API JAR) | PASS |
| Audyt wszystkich zmienionych klas przeciwko oryginałom: wyłącznie dozwolone referencje `CONSTANT_String` | PASS |
| Niezmieniony kod wykonywalny metod | PASS |
| OBF: poprawione **533** sekcje sum manifestu dla dokładnie tych samych klas | PASS |
| Niezmienione wpisy JAR: OBF **2394**, API **2604** | PASS |
| Instalacja na czystych oryginalnych JAR | PASS |
| Aktualizacja OBF+API z 1.0.22 → 1.0.23: wynik identyczny bajtowo ze świeżą instalacją | PASS |
| Ponowna instalacja (idempotencja) | PASS |
| Przywrócenie obu oryginalnych JAR, bajt w bajt | PASS |
| Celowo uszkodzone oba JAR są odrzucane bez zmiany źródeł | PASS |
| Wszystkie historyczne wiersze map CSV zachowane bez zmian, nowa lista dopuszczonych 67 podmian | PASS |
| **870/870 plików danych** bajtowo identycznych z 1.0.22 | PASS |
| `rules.csv` — **7371/7371** opcji dialogowych poprawnych | PASS |
| Go test/vet OBF, API, instalatora, trzy Windows x64 PE32+ cross-build | PASS |
| ZIP: **873 wpisy**, CRC, brak oryginalnych JAR | PASS |
| Natywny test Windows oraz uruchomiona gra | **NIE WYKONANO** |
| Gotowa kompletna wersja 1.1 | **NIE** |

**Oryginały (SHA-256):**
- OBF: `5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8`
- API: `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`

**Po instalacji 1.0.23 (SHA-256):**
- OBF: `f391bc4f0a0c6078845f02415b80378a9d45375ab37eb6c287fcac4058b46abb`
- API: `562877340d26fecabb5c34f38b9fbe11ed8d2c781faa78b307c7150bc018cb10`

**Pakiet:** `Starsector_PL_ASCII_0.98a_RC8_1.0.23_MINIMALNY.zip`, **12 697 625 B**, SHA-256 `1476d7f23cb03d6167c256e6d7e2fc1261524d7e474975acd18cc773ae2d7dd4`. ZIP oraz `Starsector_PL_1.0.23_TESTY.json` zapisano w prywatnej Bibliotece projektu.

**GitHub Actions:** pełne odtworzenie nakładek 1013–1023, walidacje danych, testy map, Go test/vet i kompilacja Windows x64: **PASS** — [przebieg 43107856887](https://github.com/HeisenbergC29/starsector_pl/actions/runs/43107856887). Jest to test CI na Linuksie, nie test uruchomionej gry na Windows.

## Reprodukcja stanu z GitHub

```bash
python3 tools/restore_snapshot.py
for n in 1013 1014 1015 1016 1017 1018 1019 1020 1021 1022 1023; do
  python3 "tools/apply_$n.py" worktree
done
python3 tools/verify_1023_ui.py worktree
python3 tools/check_project.py worktree/mod
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
python3 tools/package_1023.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.23_MINIMALNY.zip
```

Do weryfikacji JAR konieczny jest oryginalny prywatny `starfarer_obf.jar` i `starfarer.api.jar` (nie wolno ich publikować). Po instalacji można użyć `tools/audit_1015_jars.py` do ścisłej kontroli bajtkodu oraz map, wskazując oryginał, patch i odpowiedni aktywny plik CSV.

## Nadal do zrobienia przed pełną 1.1

1. Dalsze nieprzetłumaczone napisy Java API/OBF: krótkie etykiety oraz dynamicznie składane teksty; klasyfikować widoczność, nie tłumaczyć samych ID.
2. Odmiana zaimków w 219 wywołaniach oraz 81 użyciach `Misc.STORY` — bez ryzykownej podmiany globalnej.
3. Audyt semantyczny grup `DRAFT` / `OPTIONAL`, w tym zgodność z polskimi nazwami, nickami i skrótami.
4. Rzeczywisty test uruchomionej gry oraz instalatora na Windows.

Nie deklarować kompletności ani testów, których nie wykonano.
