# Audyt 1.1: teksty dynamiczne Java (stan 1.0.17)

**Status:** problem potwierdzony na oryginalnych bibliotekach Starsector 0.98a-RC8. Nie wprowadzono zmian w plikach gry ani w mapach 1.0.17.

**Aktualizacja:** w wersji 1.0.18 podmiotowe `he/she` przetlumaczono na `on/ona` w OBF `Person` i API `BaseBarEventWithPerson` oraz `HistorianData`. Pozostale zaimki i `Misc.STORY` nadal wymagaja pracy. Ponizsze liczby dotycza audytu stanu 1.0.17. Zobacz `docs/RELEASE_1018.md`. Audyt jest wykonywalny i nie zawiera komercyjnych JAR.

## Wyniki — dialogi w barach

Klasa `com.fs.starfarer.api.impl.campaign.intel.bar.events.BaseBarEventWithPerson` zwraca angielskie zaimki z literałów kodu:

| Metoda | Oryginał |
| --- | --- |
| `getManOrWoman` | `man`, `woman` |
| `getHeOrShe` | `he`, `she` |
| `getHimOrHer` | `him`, `her` |
| `getHimOrHerself` | `himself`, `herself` |
| `getHisOrHer` | `his`, `her` |

Żaden z tych literałów klasy bazowej nie jest objęty bieżącą mapą API 1017.

W `PlanetaryShieldBarEvent` odnaleziono 18 wywołań tych metod (10 `getHeOrShe`, 6 `getHisOrHer`, po jednym `getHimOrHer` i `getHimOrHerself`). Jednocześnie **53 fragmenty tego dialogu są już podmieniane na polskie**: 42 ze statusem `DRAFT_ONLY_NOT_INSTALLED`, 10 `OPTIONAL_PATCHER_NOT_GAME_TESTED`, 1 `REVIEWED_UI_LITERAL_1005`. Statusy `DRAFT` nie są filtrowane przy instalacji.

Krytyczne ograniczenie: `her` jest jednym literałem wspólnym dla dwóch metod o innych rolach gramatycznych (dopełnienie / zaimek dzierżawczy). Globalna podmiana `her` na jedno polskie słowo może zepsuć odmianę innych zdań. Trzeba prześledzić wszystkie wywołania, ustalić bezpieczną odmianę i ewentualnie przebudować tłumaczenia sąsiednich fragmentów bez naruszania kodu. **Nie patchować automatycznie całej grupy.**

Przykładowe dalsze brakujące literały z tej klasy: tekst o utraconych oczach, sklejany z `getHisOrHer`, pozostaje po angielsku.

## Wyniki — premia doświadczenia

Dwie klasy interfejsu OBF:
- `com.fs.starfarer.coreui.refit.ModPickerDialogV3$PermaModInfoWidget$1`
- `com.fs.starfarer.ui.newui.FleetMemberRecoveryDialog$7`

W obu metoda `createImpl` tworzy tooltip z długim nieprzetłumaczonym pierwszym fragmentem, dwukrotnym użyciem `Misc.STORY` i trzema późniejszymi fragmentami objętymi polonizacją. `Misc.STORY` ma oryginalną wartość `story` i nie jest tłumaczone w mapie API 1017.

Sama zmiana angielskiego początku nie wystarczy: trzeba sprawdzić wszystkie zastosowania `Misc.STORY` przed jego tłumaczeniem, bo potencjalnie uczestniczy również w składaniu innych tekstów i/lub elementach technicznych. Zachować poprawną odmianę `punkt fabularny` w obu miejscach.

## Reprodukcja (oryginalne JAR wyłącznie lokalnie)

```sh
python3 tools/restore_snapshot.py
python3 tools/apply_1013.py worktree
python3 tools/apply_1014.py worktree
python3 tools/apply_1015.py worktree
python3 tools/apply_1016.py worktree
python3 tools/apply_1017.py worktree

python3 tools/audit_dynamic_fragments.py \
  --obf /prywatna/sciezka/starfarer_obf.jar \
  --api /prywatna/sciezka/starfarer.api.jar \
  --worktree worktree --out /tmp/AUDIT_DYNAMIC_1018.json
```

Skrypt weryfikuje dokładne SHA-256 oryginalnych JAR i sprawdza miejsca wywołań przez `javap` (wymagany JDK), nie modyfikuje plików, a raport zawiera tylko nazwy klas, krótkie literały, wartości liczbowe oraz flagi diagnostyczne. Zweryfikowany raport `AUDIT_DYNAMIC_1018.json` zapisano w prywatnej Bibliotece projektu.

**Wniosek:** mapy 1.0.17 nie gwarantują poprawnej polszczyzny w dynamicznie składanych zdaniach. Przed 1.1 wymagany audyt kontekstów i kontrola, czy każda zmiana nadal dotyczy tylko wyświetlanego tekstu. Test uruchomionej gry na Windows nie został wykonany.
