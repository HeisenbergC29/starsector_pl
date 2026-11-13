# Starsector PL ASCII 1.0.43 — poprawki wyrazen dzierzawczych w dialogach

**Data:** 2026-11-13  
**Gra:** Starsector 0.98a-RC8  
**Poprzednia wersja:** 1.0.42 (commit `94f1bd42d6e301072f662236674497c2eb0a5d62`)  
**Status:** poprawka robocza; **NIE** jest ukończoną polonizacją 1.1.

## Faktycznie zmienione teksty

W `data/campaign/rules.csv` zmieniono **31** rekordow, wszystkie w kolumnie `text`, wykonujac **36** kontrolowanych podmian. Z 31 rekordow usunieto **36** wystapien zmiennych zaimkowych typu `$hisOrHer` / `$HisOrHer` tam, gdzie w oryginalnym zdaniu laczyly sie z czesciami ciala lub zalogami. Identyfikatory (`id`), warunki (`conditions`), skrypty (`script`), wyzwalacze (`trigger`), etykiety opcji (`options`) i notatki (`notes`) pozostaly nietkniete.

Przyklady: `Na $hisOrHer twarzy` -> `Na twarzy rozmowcy`, `sklada $hisOrHer dlonie` -> `sklada dlonie`, `do $hisOrHer zalogi` -> `do wlasnej zalogi`, `$HisOrHer glos` -> `Glos rozmowcy`. W jednym dialogu poprawiono tez przecinek po cytowanej wypowiedzi na kropke. Pojedyncze zdania moga zawierac inne bledy gramatyczne: recenzja obejmuje **tylko wskazane 36 fragmentow**, nie gwarantuje poprawnosci calego dialogu.

Rejestr zmian: [`docs/RULES_POSSESSIVE_REVIEW_1043.json`](RULES_POSSESSIVE_REVIEW_1043.json) (31 identyfikatorow, hashe tekstow przed/po). Kontrola tego rejestru wymaga zachowania w całości poprzednich **153** zatwierdzonych wierszy (`1034`, `1035`, `1039`). Lacznie **184** wiersze z poprawkami tekstow zatwierdzonymi offline, **296** usunietych odniesien do zmiennych, **184** wiersze do natywnej kontroli Windows.

**Wazne:** zadna z tych zmian nie edytuje **219 wywolan getterow Java**. Z nich **33** sprawdzono kontekstowo offline w poprzednich wydaniach, **186** wymaga przegladu; konflikt wspoldzielonej stalej `her` nadal istnieje.

## Weryfikacja i bezpieczeństwo

| Kontrola | Potwierdzony wynik |
| --- | --- |
| Liczba zmienionych wierszy `rules.csv` | **31/31** |
| Precyzyjne podmiany i usuniete wstawki | **36/36** |
| Zmiany innych kolumn CSV | **0** |
| Pozostale 869 plikow `data/` | **Bajtowo bez zmian** |
| Cofniecie 1.0.43 -> 1.0.42 | **Identyczny SHA-256 `rules.csv`** |
| Stare 153 rekordy recenzji | **Wszystkie zachowane** |
| Poprawnosc opcji w `rules.csv` | **7371, zero bledow** |
| Testy negatywne zmiany danych | **12/12 PASS** |
| Testy negatywne blokad wydania 1.1 | **15/15 PASS** |
| `go test` / `go vet` | **3 komponenty PASS** |
| Cross-kompilacja Windows x64 | **3 EXE PE32+ PASS** |
| Zgodnosc osadzonych patcherow w instalatorze | **Bajtowa zgodnosc** |
| Archiwum minimalne | **873 wpisy, CRC PASS, bez oryginalnych JAR** |
| Natywny test w działającej grze | **NIEWYKONANY** |

Nie bylo potrzeby ponownego patchowania JAR-ow: **mapy API/OBF oraz kod wykonywalny patcherow Java nie zostaly zmienione w stosunku do 1.0.42**. Instalatorem zarzadza nowszy numer wydania 1.0.43; zawarte w nim podprogramy patchujące Java sa identyczne funkcjonalnie z 1.0.42.

## Sumy kontrolne

- `rules.csv` 1.0.42: `fd7697b869bc4951204a7e90583ab8526ae1d046ba715454048b7cbaedcd3751`
- `rules.csv` 1.0.43: `a43f8a4f5acf91e67c7331c7828e3152564f2e224ea2a6bb46e49b9d6374f8a0`
- Niezmieniona mapa `TLUMACZENIA_JAR_1042.csv`: `abaa3521fb8906e9686603ea38252cde5e4b00745761ccb11a7588a410bbb9e9`
- Niezmieniony `starfarer.api.jar` po spatchowaniu wersji 1.0.42: `ae2cfb7bda28b58e20bd31976e1f399174c9eab564f5b98c192f2464ecf3bcf4` (w tej wersji nie wykonywano nowego patchowania JAR-ow).
- **Paczka 1.0.43 ZIP:** `2ee2a4692fe27e544afa12ac9de2daf333f6ee9a4a05d2dc5216f431ed3a1f1b` (**16 468 391 bajtow**, 873 wpisy).

## Odtworzenie z GitHuba

Po odtworzeniu bazowego snapshotu 1.0.12 i zastosowaniu wszystkich nakladek 1013–1042:

```bash
python3 tools/apply_1043.py worktree
python3 tools/verify_1043.py worktree
python3 tools/verify_review_1043.py worktree --ledger34 docs/RULES_PRONOUN_REVIEW_1034.json --ledger35 docs/RULES_PRONOUN_REVIEW_1035.json --ledger39 docs/RULES_PRONOUN_REVIEW_1039.json --ledger docs/RULES_POSSESSIVE_REVIEW_1043.json
python3 tools/test_1043.py worktree
python3 tools/check_release_gates_1043.py worktree --gates docs/RELEASE_GATES_11.json
python3 tools/test_release_gates_1043.py worktree --gates docs/RELEASE_GATES_11.json
(cd worktree && sh build_windows.sh)
python3 tools/package_1043.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.43_MINIMALNY.zip
```

CI nie publikuje komercyjnych oryginalnych JAR; bez natywnego Windows nie mozna sprawdzic wygladu napisow w rozgrywce. Do pelnej 1.1 pozostaja 186 nierozpatrzonych getterow Java, 3536 historycznych tekstow API do recenzji, testy 81 kontekstow PF, 184 zmienionych wierszy dialogow, 77 poprawek jednostek i 15 interpunkcji oraz audyt kompletności calej gry.
