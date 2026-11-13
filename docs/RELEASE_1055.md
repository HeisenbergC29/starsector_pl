# Starsector PL ASCII v1.0.55 — blokady: jednostki czasu i poprawna skladnia opisow

**Data:** 2026-11-14  
**Gra:** Starsector 0.98a-RC8, Windows x64  
**Status:** poprawka roboczej polonizacji; docelowa **1.1 NIE jest ukonczona**. Wszystkie teksty w grze pozostaja w polskim ASCII.  
**Baza:** v1.0.54, API mapa SHA-256 `d7256e12565e62d3cce7c67479014af9857a1b9357e252bcca26a7ae79067ce0`.  
**Nowa mapa:** 5298 wpisow SHA-256 `c45d1e8e33240b7716e94b9e5ca1f3ae7b74eb1314db38fb57f146b85b863848` (5296 faktycznych podmian w 938 klasach, pozostale dwa historyczne wpisy API sa obslugiwane w OBF/mod/data).

## Poprawki z oryginalnego JVM

- `BlockadeFGI`: `day -> dzien`, `days -> dni`, `more  -> <pusto>`, `Assessment -> Ocena`.
- `KnightsOfLuddTakeoverExpedition`: te same cztery mapowania, lecz scisle przypisane do osobnej klasy.
- `GenericRaidFGI`: skorygowano **dwa istniejace** fragmenty zdania `There are no colonies for the ` + nazwa operacji + ` to target in the system.`. Dawny przeklad dublowal „do zaatakowania” i mial niepoprawna skladnie. Obecne skladanie daje np. `W tym ukladzie nie ma kolonii dostepnych jako cel operacji: "blokada".`. Cudzyslow umozliwia wstawienie dowolnej nazwy operacji bez wymagania odmiany.

**Dlaczego `more ` jest puste?** Oryginalny Java StringBuilder sklada najpierw caly zwrot `potrwa okolo %s `, a dopiero po liczbie w przypadku trwajacej blokady dokleja `more ` + `day(s)`. Doslowne polskie `jeszcze` w tej pozycji tworzy bledny zwrot `potrwa okolo 2 jeszcze dni`. Zachowano poprawna ogolna dlugosc `potrwa okolo 2 dni` w obu stanach, pomijajac dodatkowe angielskie `more` bez ryzykownego przepisania kodu JVM. Jest to **kompromis semantyczny**: przy trwajacej blokadzie tekst nie wyraza juz oddzielnie „kolejnych/pozostalych dni”. Pełniejsze rozroznienie wymagaloby ingerencji w skladanie zdania i osobnego testu w grze; nie jest deklarowane jako ukonczone.

W metodach UI obu blokad osobne oryginalne stale `Assessment` nadal byly widocznymi naglowkami angielskimi, chociaz nadklasa `GenericRaidFGI` miala juz polskie `Ocena`. Nowe mapowania dzialaja tylko w klasach, ktore faktycznie zawieraja te stale.

## Dowody i testy

- Zweryfikowano w oryginalnym prywatnym `starfarer.api.jar` **10/10** zmienianych `CONSTANT_String` i ich aktywne instrukcje `ldc/ldc_w`; dodatkowo **48** historycznych juz mapowanych tekstow z trzech klas potwierdzono jako uzywane przez oryginalny bajtkod i zrecenzowano semantycznie.
- W stosunku do 1.0.54 zmieniaja sie dokladnie trzy pliki `.class`, weryfikowane binarnie; **wszystkie instrukcje JVM niezmienione**. Poprzednia scisle kontrolowana poprawka dwoch operandow z 1.0.51 pozostaje nietknieta.
- **20** skladanych zwrotow czasu dla dwoch klas, pieciu liczb `1, 2, 5, 12, 21` i dwoch stanow blokady, plus **4** skladane opisy braku kolonii z roznie nazwanymi operacjami.
- **7** negatywnych testow mapy i **10** testow falszywego domkniecia 1.1 przechodzi przez prawidlowe odrzucenie.
- **870** plikow `mod/data/` i patcher OBF/3537 podmian w 539 klasach pozostaja bajtowo bez zmian.
- Testy Go API: `go test ./...` i `go vet ./...` PASS.
- Prawdziwy test na prywatnych oryginalnych JAR: swieza instalacja i upgrade **1.0.54 -> 1.0.55** sa bajtowo identyczne; ponowny patch obu bibliotek to no-op, uszkodzona metadana ZIP odrzucona bez nadpisania, restore obydwu oryginalow bajtowo identyczny.
- Wynik API JAR SHA-256: `57004e66715ce8ccaec236a85d73961290cb4ebbbdc0282abd12a31c9b0c6be8`; OBF bez zmian SHA-256 `85b4b2afb4f6175cabedf1ef5cb9976e0097e39403dff0fc18c728c9d48894e1`.

## Semantyczny rejestr API

Poprzednie **343** historyczne recenzje pozostaja w rejestrze bez zmian. Nowe **48** wpisow (BlockadeFGI 14, KnightsOfLuddTakeoverExpedition 10, GenericRaidFGI 24) maja oryginalny `CONSTANT_String`, instrukcje wywolujaca i fingerprint calego wiersza. Lacznie **391/3658** ocenionych historycznych DRAFT/OPTIONAL offline, **3267** do dalszej recenzji. Osiem nowych literalow wersji 1.0.55 nie zawyzaja licznika historycznego.

## Odtworzenie z repozytorium

Po uruchomieniu sekwencji `tools/restore_snapshot.py`, `tools/apply_1013.py` ... `tools/apply_1054.py`:

```bash
python3 tools/apply_1055.py worktree
python3 tools/verify_1055.py worktree
python3 tools/test_1055.py worktree
python3 tools/verify_review_1055.py worktree --previous docs/API_SEMANTIC_REVIEW_1054.json --ledger docs/API_SEMANTIC_REVIEW_1055.json
python3 tools/check_release_gates_1055.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/API_SEMANTIC_REVIEW_1054.json --ledger docs/API_SEMANTIC_REVIEW_1055.json
python3 tools/test_release_gates_1055.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/API_SEMANTIC_REVIEW_1054.json --ledger docs/API_SEMANTIC_REVIEW_1055.json
(cd worktree && sh build_windows.sh)
python3 tools/package_1055.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.55_MINIMALNY.zip
```

Dowody z prywatnego oryginalnego JVM: `docs/JVM_AUDIT_1055.json`, `docs/UPGRADE_1055.json`; skrypty `tools/audit_jvm_1055.py`, `tools/private_upgrade_1055.py`. **Nie commitowac ani nie publikowac komercyjnych JAR.** GitHub Actions sprawdza strukture i kompilacje bez tych plikow, prywatny audyt sprawdza binaria na posiadanej kopii.

## Wciaz blokuje ukonczenie 1.1

Historyczny audyt 3267 pozostalych wpisow API, 186 nierozpatrzonych innych wywolan getterow zaimkowych i 2275 surowych odniesien do placeholderow plciowych w 1139 dialogach wymagajacych dalszego kontekstowego audytu. **Natywny gameplay i wizualna kontrola tekstow w uruchomionej grze Windows nie byly przeprowadzone**. Obejscie `more` opisane wyzej jest gramatycznie poprawne, ale nie zachowuje kazdego odcienia czasu; wymagane sa testy gry.
