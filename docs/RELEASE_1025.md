# Starsector PL 1.0.25 — 81 etykiet OBF i audyt DRAFT/OPTIONAL (2026-11-11)

**Gra:** Starsector 0.98a-RC8. **Cel kompletnej wersji 1.1 nadal OTWARTY.**

## Faktycznie wykonane tłumaczenia

**81 nowych podmian tekstów w OBF, w 12 klasach**, bez zmian wartości mapy Java API i bez zmian plików danych. Zastosowano polski ASCII wymagany przez fonty gry.

| Obszar (oryginalna klasa) | Nowe literały |
|---|---:|
| Doktryny i rozkazy flot — `campaign.command.J` | 7 |
| Produkcja na zamówienie — `CustomProductionPanel` | 10 |
| Wykaz placówek — `OutpostListPanel` | 6 |
| Rachunek dochodów — `IntelIncomePanel` | 3 |
| Przeglądarka schematów uzbrojenia — `WeaponBlueprintBrowser` | 9 |
| Przeglądarka schematów eskadr — `FighterBlueprintBrowser` | 6 |
| Przeglądarka schematów okrętów — `ShipBlueprintBrowser` | 10 |
| Panel oficerów — `coreui.ooo0` | 6 |
| Generator nazw — `campaign.save.null` | 5 |
| Kategorie i decyzje dziennika misji — `campaign.comms.v2.D` | 10 |
| Stosunek floty do gracza — `StandardTooltipV2$9` | 4 |
| Wypadki floty i utrata gotowości — `accidents.ShipLoss` | 5 |
| **Razem** | **81** |

**Przykłady:** `Upkeep` → `Utrzymanie`, `Frigates` → `Fregaty`, `Qty` → `Ilosc`, `Unassigned` → `Nieprzydzielony`, `Warships` → `Okrety wojenne`.

**Naprawa dynamicznego tekstu gotowości bojowej:** w `ShipLoss` dotąd pozostawały angielskie `lost `, ` losing ` i ` CR`. Skomponowano i przetestowano całe polskie warianty `utrata 17% GB`, `skrzydlo Osa - utrata 17% GB`, `okret Jastrzab - utrata 17% GB`. Neutralna konstrukcja `- utrata` zapobiega błędom rodzaju. **Skrót CR zmieniono na GB tylko w tej klasie**, nie w identyfikatorach technicznych.

Celowo odrzucono wpis `Mentor...` → `Mentor...` (brak rzeczywistej zmiany) i literał `Phase ships`, który w klasie przeglądarki był już przetłumaczony. Nie dodawano wartości enum/identyfikatorów.

## Audyt starszych map API — 3659 aktywnych podmian

Wbrew nazwom statusów `DRAFT_ONLY_NOT_INSTALLED` i `DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME`, odpowiednie wiersze **są** stosowane przez patcher; nie wolno ich pomijać w audycie.

- `DRAFT_ONLY_NOT_INSTALLED`: **1008** wierszy.
- `OPTIONAL_PATCHER_NOT_GAME_TESTED`: **2295** wierszy.
- `DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME`: **356** wierszy.
- **Razem 3659**: zero utraconych znaczników formatu rozpoznawanych przez audytor, zero uszkodzonych separatorów wierszy, końcowych/przednich spacji oraz wynikowych znaków spoza ASCII.
- **Dwa** przypadki przecinka `, and` → ` i` w `FleetInteractionDialogPluginImpl`: zweryfikowano różne warianty oryginalnego składania listy okrętów i eskadr; usunięcie przecinka przed polskim `i` jest celowe i poprawne.

Raport **`ST_1025_DRAFT_AUDIT.json`** i kod **`tools/audit_draft_boundaries_1025.py`**. **To automatyczna kontrola formatowania i dokładna analiza dwóch wyjątków, nie ręczne ocenienie znaczenia wszystkich 3659 tłumaczeń.** Pozostały audyt semantyczny statusów DRAFT/OPTIONAL jest otwarty.

## Testy lokalne na oryginalnych JAR (Linux)

| Kontrola | Wynik |
|---|---|
| OBF: **3294** poprawne podmiany `CONSTANT_String`, **533** zmienione klasy | PASS |
| API: **5148** podmian w **936** klasach, wynikowy JAR bajtowo identyczny z 1.0.24 | PASS |
| Audyt wszystkich zmienionych klas na poziomie CP i pozostałego bajtkodu | PASS — niedozwolonych zmian **0** |
| Zmienione sekcje sum kontrolnych manifestu OBF | **533/533** poprawne |
| Niezmienione wpisy ZIP w bibliotekach | OBF **2394**, API **2604** |
| 81 literałów potwierdzonych w oryginalnej puli stałych i w **100 miejscach** kodu `ldc` w 12 klasach | PASS |
| Świeża instalacja obu JAR na oryginalnych plikach | PASS |
| **Rzeczywisty upgrade:** najpierw spatchowano oba JAR wersją 1.0.24, potem wykonano update 1.0.25 | PASS |
| Po aktualizacji oba JAR są identyczne z wynikami świeżej instalacji | PASS |
| Ponowne uruchomienie patcherów — idempotencja | PASS |
| Restore dokładnych oryginalnych sum obu JAR | PASS |
| Celowo uszkodzony OBF jest odrzucony bez nadpisania | PASS |
| Negatywne testy nieuprawnionych zmian starych/nowych map | **5/5 PASS** |
| 870/870 plików danych identycznych z 1.0.24 | PASS |
| 1018 niegenerowanych plików źródłowych odtworzonych bajtowo | PASS |
| `rules.csv`: 7371/7371 poprawnych opcji | PASS |
| Go test/vet OBF, API, instalator; 3 Windows x64 PE32+ cross-build | PASS |
| ZIP 873 wpisy, CRC bez błędów, brak oryginalnych JAR | PASS |
| Uruchomienie instalatora oraz gry na Windows | **NIE WYKONANO** |
| Finalne pokrycie 1.1 | **NIE POTWIERDZONO** |

**Uwaga o reprodukowalności:** źródła porównano po wyłączeniu wygenerowanych EXE i dwóch binarnych wkładów do instalatora; EXE zweryfikowano niezależnie jako poprawne obrazy PE32+. Pierwszy test rzekomego upgrade'u startował z przywróconych oryginałów i został powtórzony z prawdziwą spatchowaną instalacją 1.0.24.

**SHA-256 oryginalne:** OBF `5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8`; API `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`.

**SHA-256 po instalacji:** OBF `dc1fecf61d12d8819bab11b3d1bf20c4aecc294ac27ebce747e08b0dd35ae033`; API `3d584fb28a334adc62894795bb197e3618eee718d1830de129eec22accd5b843` (identyczne API jak w 1.0.24).

**Paczka:** `Starsector_PL_ASCII_0.98a_RC8_1.0.25_MINIMALNY.zip` — **13 156 854 B**, SHA-256 `e5ccc7b05ab90f4f368061af019896e006a010346d10a0961a62e9b56e8eda04`. ZIP, `Starsector_PL_1.0.25_TESTY.json`, `ST_1025_DRAFT_AUDIT.json` i `ST_1025_CALLSITES.json` zapisano w prywatnej Bibliotece.

## Odtworzenie i dalsza praca

```sh
python3 tools/restore_snapshot.py
for n in 1013 1014 1015 1016 1017 1018 1019 1020 1021 1022 1023 1024 1025; do
  python3 "tools/apply_$n.py" worktree
done
python3 tools/verify_1025_ui.py worktree
python3 tools/test_1025_delta.py worktree
python3 tools/audit_draft_boundaries_1025.py worktree/buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1025.csv --out draft_audit.json
python3 tools/check_project.py worktree/mod
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
python3 tools/package_1025.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.25_MINIMALNY.zip
```

Odrębny audyt oryginalnych stałych z prywatnym komercyjnym JAR i JDK:

```sh
python3 tools/verify_1025_callsites.py --obf /prywatna/sciezka/starfarer_obf.jar --out /tmp/ST_1025_CALLSITES.json
```

Następne priorytety: dalsze krótkie etykiety OBF/API, 81 kontekstów `Misc.STORY`, zaimki w dynamicznych zdaniach (219 wywołań), audyt znaczenia starszych tłumaczeń DRAFT/OPTIONAL i **rzeczywisty test Windows/grania**. Nie deklarować kompletnego 1.1 bez tych prac.
