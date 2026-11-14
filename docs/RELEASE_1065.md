# Starsector PL ASCII 1.0.65 — audyt rajdow i bombardowan, teksty skladane

**Gra:** Starsector 0.98a-RC8. **Platforma instalatora:** Windows x64. **Cel 1.1: NIEUKONCZONY.**

## Faktyczna praca nad tlumaczeniami

Sprawdzono na podstawie oryginalnego `starfarer.api.jar` klase `com.fs.starfarer.api.impl.campaign.rulecmd.salvage.MarketCMD`, ktora tworzy interfejs rajdow, bombardowan i obrony kolonii.

- **104** wpisy `DRAFT/OPTIONAL` tej klasy przejrzano kontekstowo. **17** z nich bylo juz w historycznym rejestrze mimo starego statusu w mapie, dlatego **tylko 87** doliczono jako nowo zrecenzowane. Siedem pozostalych wpisow klasy mialo wczesniejszy status potwierdzenia; jednemu z nich poprawiono brzmienie, ale nie doliczono go jako nowej historycznej recenzji.
- **17** precyzyjnych korekt polskich fragmentow. Nie zmieniono zadnych kluczy technicznych ani innych klas.
- Uporzadkowano skladanie polskich komunikatow z nazwa kolonii, przemyslu, frakcji i stacji wstawiana przez silnik. Zastosowano m.in. `Stabilnosc kolonii: %NAME%`, `Zaatakuj: %NAME% (wraz z obroncami)` i `Rozpocznij rajd. Cel: %NAME%` zamiast wymagac fleksji dynamicznego tekstu.
- Przywrócono poprawna skladnie fragmentow o zakloceniu dzialalnosci i minimalnej skutecznosci rajdu: przykladowo `Minimalna wymagana skutecznosc rajdu: 50.` oraz `Dowodca sil naziemnych ocenia, ze rajd powinien zaklocic dzialanie obiektu: Rafineria przez co najmniej 5 dn.`
- Opisy przewagi orbitalnej nie wymuszaja rodzaju gramatycznego stacji, a tekst o obnizonej skutecznosci rajdu tworzy kompletne polskie zdanie.
- Tlumaczenia maja **ASCII bez znakow diakrytycznych**, zgodnie z aktualnym kontraktem kompatybilnosci silnika; polskie znaki nie sa jeszcze gwarantowane.

## Oryginalny JVM: audyt tekstow i bezpieczeństwa patchera

- `starfarer.api.jar` oryginalny SHA-256 `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`.
- Klasa `MarketCMD`: **363** faktyczne instrukcje `ldc/ldc_w`, **240** unikalnych wartosci `CONSTANT_String`, z czego wszystkie **111** mapowanych tekstow maja rzeczywiste wywolania w oryginalnym JVM. Nowo oceniono 104 pozycje `DRAFT/OPTIONAL` (87 nowych historycznie, 17 ponownie sprawdzonych). Dowody: `docs/JVM_AUDIT_1065.json`, skrypt `tools/audit_original_jvm_1065.py`.
- Nie nalezy uznawac pozostalych **129** nieobjetych mapa stalych za automatycznie gotowe teksty widoczne lub automatycznie bledy; sa tam tez klucze techniczne. Wymagaja osobnej oceny, czy sa prezentowane graczowi.
- Mapa API: **5314 wierszy (bez zmiany liczby)**, 17 zmian tlumaczenia/status 104 recenzji. Po 1.0.65 historyczne recenzje **617/3658**, **3041** pozostale; plik `docs/API_SEMANTIC_REVIEW_1065.json` musi zachowac wszystkie **530** poprzednich odciskow dokladnie. **Nie liczyc drugi raz 17 starych pozycji MarketCMD**. Dwie z nich poprawiono jezykowo w tym wydaniu bez zwiekszania licznika recenzji.
- Mapa OBF oraz **870** plikow `mod/data` sa bajtowo niezmienione. Wszelkie `id`, `script`, `conditions`, nazwy klas i identyfikatory pozostaly oryginalne.
- W oryginalnych prywatnych JAR test **fresh 1.0.65 == upgrade 1.0.64 -> 1.0.65**; zmieniono tylko `MarketCMD.class`. Struktura instrukcji JVM i ich przesuniecia identyczna. Idempotencja, backup/restore oryginalow oraz odmowa modyfikacji uszkodzonego JAR — PASS. Raport `docs/PRIVATE_UPGRADE_1065.json`.
- **55** testow skladania dynamicznych tekstow, **12** odrzuconych niepoprawnych mutacji mapy, **6** testow negatywnych kontraktu dystrybucji. Testy `go test` / `go vet` dla patcherow OBF, API i instalatora oraz kompilacja PE32+ Windows x64 — PASS. 7371 opcji dialogowych — 0 bledow.

## Ustalenie uzytkownika: testy w grze PO wersji 1.1

Od 2026-11-14 testowanie uruchomionej gry Windows zostalo **celowo odlozone do czasu po stworzeniu wersji 1.1**. Nie jest wymaganiem wstepnym publikacji 1.1. Jest nim natomiast ukonczenie tlumaczen i automatyczne testy plikow/pakietu/JVM opisane w `docs/TEST_POLICY_11.md`. Brak natywnych testow gry nie moze byc pozornie zaliczany.

**1.1 nie jest gotowa z powodu nieukonczonej polonizacji**, a nie z powodu odlozonych testow w grze. Nadal do przejrzenia: **3041** historyczne wpisy API, **186** kontekstow getterow JVM i **1953** surowe dynamiczne znaczniki plciowe w 1006 dialogach (nie kazdy jest bledem). Oprócz tego kompletnosc innych widocznych tekstow i bezpieczne przetlumaczenie potrzebnych skrótów.

## Reprodukcja wydania

Po przywroceniu snapshotu 1.0.12 i nakladek 1013–1064, z repozytorium:

```sh
python3 tools/apply_1065.py worktree
python3 tools/verify_1065.py worktree
python3 tools/test_1065.py worktree
python3 tools/test_package_contract_1065.py worktree
python3 tools/build_review_1065.py worktree --record docs/MARKETCMD_REVIEW_1065.json --previous docs/API_SEMANTIC_REVIEW_1064.json --ledger docs/API_SEMANTIC_REVIEW_1065.json
python3 tools/check_release_gates_1065.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/RELEASE_GATES_1064.json --prior-semantic docs/API_SEMANTIC_REVIEW_1064.json --semantic docs/API_SEMANTIC_REVIEW_1065.json
python3 tools/test_release_gates_1065.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/RELEASE_GATES_1064.json --prior-semantic docs/API_SEMANTIC_REVIEW_1064.json --semantic docs/API_SEMANTIC_REVIEW_1065.json
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
python3 tools/package_1065.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.65_MINIMALNY.zip
```

Prywatne testy JAR wymagaja plikow dostarczonych przez wlasciciela gry i nie sa odtwarzane w publicznym CI:

```sh
python3 tools/audit_original_jvm_1065.py --jar /PRIVATE/starfarer.api.jar --worktree worktree
python3 tools/private_upgrade_1065.py --jars /PRIVATE/original_core --worktree worktree
```

Nie commitowac komercyjnych JAR, prywatnych plikow gry, sciezek komputera ani nieautoryzowanych danych.
