# Starsector PL 1.0.18 — wersja robocza, 2026-11-11

**Cel 1.1 nieosiagniety.** Zgodnosc z Starsector 0.98a-RC8.

## Zmiany wzgledem 1.0.17

- **6 bezpiecznych nowych podmian** angielskich zaimkow podmiotowych (`he` → `on`, `she` → `ona`) w trzech klasach:
  - OBF `com.fs.starfarer.rpg.Person` — 2 literały.
  - API `com.fs.starfarer.api.impl.campaign.intel.bar.events.BaseBarEventWithPerson` — 2 literały.
  - API `com.fs.starfarer.api.impl.campaign.intel.bar.events.historian.HistorianData` — 2 literały; wspólne dla `getHeOrShe` i `getUCHeOrShe` (wielka litera przez `Misc.ucFirst`).
- Zastosowano tylko w wartosciach tekstowych oryginalnych metod zwracajacych **podmiot** zdania. Zachowano bez zmian `him`, `her`, `his`, `himself`, `herself`, `man`, `woman`: wymagaja indywidualnych kontekstow i odmiany. Szczegolnie `her` jest wspolnym literałem metod dopełnienia i zaimka dzierzawczego.
- **Nie zmieniono** `Misc.STORY` (wartosc `story`): audyt oryginalnego bajtkodu ujawnil **81 odwolan**: 16 w API i 65 w OBF. Globalna podmiana zagrazalaby odmiana w wielu interfejsach. Dwa tooltipy premii doswiadczenia oraz inne pozostaja do naprawy.
- **870/870 plikow `data/`** bajtowo identycznych z 1.0.17. Nie zmieniono technicznych ID ani kodu gry.

## Kontrola struktury na rzeczywistych oryginalnych JAR (Linux)

| Kontrola | Wynik |
| --- | --- |
| Oryginalne OBF i API: SHA-256 odpowiada 0.98a-RC8 | PASS |
| OBF: 3142 podmiany `CONSTANT_String`, 533 klasy | PASS |
| API: 5098 podmian `CONSTANT_String`, 936 klas | PASS |
| Audyt oryginał → patch: zero zmian bajtkodu metod | PASS |
| OBF: 533 poprawione wpisy sum kontrolnych manifestu dla 533 klas | PASS |
| Nieprzetworzone elementy ZIP: 2394 OBF i 2604 API | PASS |
| Patcher OBF/API: świeża instalacja na oryginalnych plikach | PASS |
| Aktualizacja obu bibliotek 1.0.17 → 1.0.18 (wynik równy świeżej instalacji) | PASS |
| Ponowna instalacja bez dodatkowych zmian | PASS |
| Przywrócenie dokładnych oryginalnych JAR | PASS |
| Porównanie 1003 odtworzonych plikow źródłowych (pomijajac generowane EXE/bin) | PASS |
| Go test/vet (OBF, API, instalator) i cross-build trzech EXE Windows x64 | PASS |
| `rules.csv`: 7371/7371 poprawnych opcji | PASS |
| ZIP: 873 wpisy, 870 plików danych, test CRC | PASS |
| Natywny test na Windows i rozgrywka | NIE WYKONANO |
| Pełna polonizacja | NIE POTWIERDZONA |

Obecna mapa OBF ma 3142 wiersze, a API 5100 (z czego 5098 jest rzeczywistymi trafieniami na oryginalnym JAR).

SHA-256 bibliotek po instalacji:
- OBF `c95b45715e4d7c1b982d154acdc6776a3cf60756e83eefb00ea526a96c5a6c92`.
- API `22a092f0f47a13b1e80c92893bc5be6db181eec967299227f741739299b87b3e`.

## Pakiet

`Starsector_PL_ASCII_0.98a_RC8_1.0.18_MINIMALNY.zip`
- Rozmiar: **11 608 950 bajtów**
- SHA-256: `a63018089acfb440fecfb9827111d52f5c685765768a3ee1d136101515470566`
- 873 wpisy: 870 `data` + `mod_info.json`, `CZYTAJ.txt`, jeden EXE instalatora.
- Paczka i `Starsector_PL_1.0.18_TESTY.json` zapisane w prywatnej Bibliotece. Repozytorium nie zawiera plików JAR gry.

## Reprodukcja stanu

```sh
python3 tools/restore_snapshot.py
python3 tools/apply_1013.py worktree
python3 tools/apply_1014.py worktree
python3 tools/apply_1015.py worktree
python3 tools/apply_1016.py worktree
python3 tools/apply_1017.py worktree
python3 tools/apply_1018.py worktree
python3 tools/verify_subject_pronouns_1018.py worktree
python3 tools/check_project.py worktree/mod
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
```

## Otwarte zadania

- Issue #4 (dialogi dynamiczne): `he/she` poprawione tylko jako podmioty; `him/her/his/herself` oraz wyrażenia dynamiczne nadal nie są w pełni polskie.
- `Misc.STORY` wymaga audytu wszystkich 81 miejsc przed globalną zmianą, a przetłumaczone fragmenty tooltipów muszą mieć zgodną odmianę.
- Issue #3: status `DRAFT_ONLY_NOT_INSTALLED` jest ignorowany przez patcher i pozycje te są faktycznie podmieniane.
- Potrzeba pełnego audytu wszystkich pól, tekstów, nazw, pseudonimów i skrótów. **1.1 nie jest gotowe.**

