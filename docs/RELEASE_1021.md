# Starsector PL 1.0.21 — robocza polonizacja (2026-11-11)

**Gra:** Starsector 0.98a-RC8. **Cel: kompletne 1.1 — NIEOSIĄGNIĘTY.** Wersja 1.0.21 nie wymaga testowania przez gracza przed 1.1.

## Poprawki wykonane i zweryfikowane

**OBF: dwa napisy przycisku opcji zaawansowanych**, sprawdzone przy ustawianiu i aktualizowaniu etykiety przycisku w bajtkodzie:
- `Show advanced options >>>` → `Pokaz opcje zaawansowane >>>`;
- `<<< Hide advanced options` → `<<< Ukryj opcje zaawansowane`.

**API: jeden nagłówek tabeli**, `ConvertedHangar`, w metodzie budującej podpowiedź: `Wing` → `Eskadra`.

**Dane: cztery korekty tekstowe w trzech plikach**, ujednolicające `Liga Perseanska` w odmienionych formach i poprawiające `zaopatrzenie Rycerze Ludda` na `zaopatrzenie Rycerzy Ludda`:
- `data/missions/coralnebula/MissionDefinition.java` — 1 wartość tekstowa.
- `data/missions/coralnebula/mission_text.txt` — 2 fragmenty.
- `data/characters/skills/skill_data.csv` — 1 pole `author` widoczne w grze.

Zachowano wszystkie wcześniejsze mapy tłumaczeń w celu aktualizacji z wydań 1.0.x. Nie zmieniono technicznych identyfikatorów ani bajtkodu metod.

## Testy lokalne wykonane na oryginalnych JAR i `data.rar`

| Kontrola | Wynik |
|---|---|
| OBF: **3144** zatwierdzone podmiany, **533** zmienione klasy | PASS |
| API: **5106** zatwierdzonych podmian, **936** klas | PASS |
| Audyt klasy po klasie: wyłącznie `CONSTANT_String` w metodach | PASS |
| OBF: sumy manifestu poprawione dla **533** zmienionych klas | PASS |
| Świeża instalacja obydwu patcherów na oryginalnych JAR | PASS |
| Aktualizacja **1.0.20 → 1.0.21** daje ten sam SHA-256 co świeża instalacja | PASS |
| Ponowna instalacja (idempotencja) | PASS |
| Przywrócenie obu JAR dokładnie do oryginalnego SHA-256 | PASS |
| 1009 niegenerowanych plików źródłowych odtworzonych identycznie | PASS |
| Go test i vet dla OBF, API, instalatora | PASS |
| Cross-kompilacja 3 **PE32+ Windows x64** | PASS |
| `rules.csv` **7371/7371** poprawnych opcji | PASS |
| Audyt strukturalny **870/870 plików** danych vs oryginał | PASS |
| Testy audytora na 5 syntetycznych przypadkach (w tym niedozwolone zmiany ID/kodu) | PASS |
| ZIP **873 wpisy**, test CRC, brak oryginalnych JAR | PASS |
| GitHub Actions najnowszy commit | WERYFIKOWANY OSOBNO |
| Natywny Windows i gra uruchomiona | NIE TESTOWANO |

**Audyt integralności danych** `tools/verify_source_fields_1021.py` na oryginalnym `data.rar`:
- **833** pliki o strukturze Java/JSON i podobnej: wszystkie różnice w ciągach znakowych ujętych w cudzysłowy, **zero różnic w pozostałych bajtach**;
- **18** plików CSV: zmiany wyłącznie w dozwolonych polach tekstowych, bez modyfikacji kolumn technicznych; w `rules.csv` pięć dodatkowych zmian jedynie argumentów `SetTextHighlights`, z zachowaniem reszty skryptu;
- **19** plików TXT (opisy misji, kodeks) wymagają odrębnego ręcznego audytu znaczenia i kompletności — narzędzie nie zapewnia dla nich weryfikacji struktury.

**Dodatkowy audyt TXT:** `tools/audit_prose_layout_1021.py` porównał wszystkie **19** plików TXT względem oryginału: liczba wierszy, dyrektywy i identyfikatory kodeksu, wartości liczbowe, sekwencje `\\n`, skróty klawiszowe oraz chronione znaczniki. **19/19 PASS, zero naruszeń wykrytych przez test formatu**. Raport w prywatnej Bibliotece: `Starsector_PL_1021_PROSE_LAYOUT_AUDIT.json`. To nadal **nie jest** semantyczna ocena poprawności tłumaczeń TXT.

To dowód niezmienności struktury i pól chronionych według reguł skanera, **nie** dowód poprawności znaczenia wszystkich słów; skrypt Java może zawierać literały techniczne, które wymagają sprawdzenia miejsca użycia.

Szczegółowy raport `Starsector_PL_1021_DATA_FIELD_AUDIT.json` i `Starsector_PL_1.0.21_TESTY.json` są w prywatnej Bibliotece projektu; nie publikowano oryginalnych zasobów gry.

## Sumy

Oryginalne JAR:
- OBF `5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8`
- API `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`

JAR po lokalizacji:
- OBF `cfcf4860d7b451074e6285488f4bf24f91d2dd683aad95ef11ce344894cb84be`
- API `ba0dc5a4a1d20516798e3024c891bb421c55309f9248cffe7f9d8bb7557dcada`

Paczka ZIP: **12 364 600 B**, SHA-256:
`b64d08d0355e0d5e8b91f1422a8aca7c6a994e99de6a9e973f2066bf760e66ff`.

## Odtwarzanie z GitHub

```sh
python3 tools/restore_snapshot.py
for n in 1013 1014 1015 1016 1017 1018 1019 1020 1021; do
    python3 "tools/apply_$n.py" worktree
done
python3 tools/verify_1021_delta.py worktree
python3 tools/test_source_fields_1021.py
python3 tools/check_project.py worktree/mod
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
python3 tools/package_1021.py --worktree worktree --previous /path/to/1.0.20.zip --out Starsector_PL_ASCII_0.98a_RC8_1.0.21_MINIMALNY.zip
```

Pełny audyt z oryginalnym archiwum `data.rar` (wyłącznie prywatnie):

```sh
python3 tools/verify_source_fields_1021.py \
  --original /path/to/original/data \
  --translated worktree/mod/data \
  --out /tmp/starsector_field_audit.json
```

## Nadal otwarte przed 1.1

- Pozostałe literały oryginalnych JAR muszą mieć audyt widoczności w grze; automatyczna heurystyka to tylko lista kandydatów.
- 19 plików narracyjnych TXT wymaga sprawdzenia semantycznego.
- Odmiana dynamicznych zaimków i **81** kontekstów `Misc.STORY` nadal wymagają rozstrzygnięcia; nie należy robić globalnej zamiany.
- **Issue #5:** nowa kontrola wykryła jeszcze **53** wystąpienia form `Liga/Ligi/Lige Perseusza` w `rules.csv`, `strings/descriptions.csv` i opisie misji, równolegle z `Liga Perseanska`. Cztery zmiany dokonane w 1.0.21 nie usuwają całej niespójności. Wymagana odrębna spójna decyzja terminologiczna i kontekstowe poprawki tylko tekstów gracza.
- Rozbieżności, statusy `DRAFT/OPTIONAL`, tłumaczone nazwy, nicki i skróty: dalsza kontrola.
- Faktyczny natywny test Windows i uruchomionej gry wciąż NIE wykonany.
