# Starsector PL 1.0.22 — poprawka terminologii (2026-11-11)

**Gra:** 0.98a-RC8. **Cel pełnej lokalizacji 1.1 nadal otwarty.**

## Wykonane zmiany

W danych 1.0.21 pozostawały niejednolite nazwy jednej frakcji: **53** wystąpienia `Liga/Ligi/Lige Perseusza` i **12** `Liga/Ligi Persea`. Po sprawdzeniu kontekstu pól widocznych dla gracza wszystkie **65** wystąpień w trzech plikach zmieniono na polską odmianę używaną już w reszcie lokalizacji:

| Forma źródłowa w 1.0.21 | Liczba | Forma docelowa w 1.0.22 |
|---|---:|---|
| `Ligi Perseusza` | 45 | `Ligi Perseanskiej` |
| `Ligi Persea` | 11 | `Ligi Perseanskiej` |
| `Liga Perseusza` | 4 | `Liga Perseanska` |
| `Liga Persea` | 1 | `Liga Perseanska` |
| `Lige Perseusza` | 4 | `Lige Perseanska` |

**Zmienione dokładnie trzy pliki `mod/data`:**
- `campaign/rules.csv` — 59 wystąpień; wszystkie w kolumnie `text`.
- `strings/descriptions.csv` — 4 wystąpienia; wszystkie w kolumnach tekstowych `text1..text5`.
- `missions/coralnebula/mission_text.txt` — 2 wystąpienia.

Pozostałe **867/870** plików danych identyczne bajtowo z 1.0.21. Nie ruszano imion i nazwisk, technicznych ID, skryptów, znaczników, warunków ani opcji dialogowych. Test wyklucza przypadkowe podmienienie ciągu `Ligi Persea` wewnątrz poprawnej formy `Ligi Perseanskiej`.

**Mapy i kod patcherów OBF/API są niezmienione**: wydanie 1.0.22 zmienia tylko pliki danych, numer wersji moda, opis CZYTAJ i numer wydania instalatora. Nazwy podzespołów Java nadal raportują komponent 1.0.21; to prawidłowe, bo żaden literał Java nie został zmieniony.

## Wyniki rzeczywistych testów (Linux, oryginalne JAR i data.rar)

| Test | Wynik |
|---|---|
| Dokładny diff ZIP 1.0.21 → 1.0.22 | 6 wpisów: 3 dane, `mod_info.json`, `CZYTAJ.txt`, instalator |
| Zatwierdzone 65 zmian terminologicznych, identyczne wszystkie pozostałe teksty | PASS |
| Pozostałe 867 danych, sprawdzone sumą drzewa SHA-256 | PASS |
| Audyt oryginalne data.rar kontra 870 plików: 833 strukturalnych + 18 CSV + 19 TXT | PASS, 0 naruszeń reguł struktury |
| Pola techniczne CSV, w tym `id`, `script`, `conditions` | 0 zmian |
| Format, dyrektywy i znaczniki 19 TXT | PASS |
| Test regresji słów i form przypadków, plus negatywne testy skanera ID | 10/10 PASS |
| Walidacja opcji `rules.csv` | 7371/7371 PASS |
| Go test/vet dla OBF, API i instalatora | PASS |
| Trzy pliki EXE PE32+ dla Windows x64 | PASS |
| Preview, świeża instalacja, idempotencja i restore na oryginalnych JAR | PASS |
| Po instalacji OBF/API: identyczny SHA jak w wydaniu 1.0.21 | PASS |
| Przywrócenie oryginalnych SHA-256 obu JAR | PASS |
| ZIP, 873 pozycje, CRC; brak oryginalnych komercyjnych JAR | PASS |
| Test w uruchomionym Starsector Windows | **NIE WYKONANO** |
| Kompletność polonizacji 1.1 | **NIE POTWIERDZONO** |

**JAR po patchu (niezmienione wobec 1.0.21):**
- OBF 3144 podmiany: `cfcf4860d7b451074e6285488f4bf24f91d2dd683aad95ef11ce344894cb84be`
- API 5106 podmian: `ba0dc5a4a1d20516798e3024c891bb421c55309f9248cffe7f9d8bb7557dcada`

**ZIP wydania:** `Starsector_PL_ASCII_0.98a_RC8_1.0.22_MINIMALNY.zip`, **12 364 615 bajtów**; SHA-256 `824534b9be176af16d09874a74f8d9e14c09174414edc58ced6a9a82dba244bf`.

ZIP, raport testów i szczegółowe audyty danych/TXT znajdują się w prywatnej Bibliotece projektu. Oryginalnych JAR i `data.rar` nie należy publikować w GitHub.

## Odtworzenie z publicznych narzędzi

```sh
python3 tools/restore_snapshot.py
for n in 1013 1014 1015 1016 1017 1018 1019 1020 1021 1022; do
  python3 "tools/apply_$n.py" worktree
done
python3 tools/verify_1022_names.py worktree
python3 tools/test_1022_names.py
python3 tools/test_source_fields_1021.py
python3 tools/check_project.py worktree/mod
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
python3 tools/package_1022.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.22_MINIMALNY.zip
```

Jeśli poprzedni ZIP 1.0.21 jest dostępny, podaj `--previous-zip /sciezka/1.0.21.zip` do `verify_1022_names.py`, a `--previous /sciezka/1.0.21.zip` do `package_1022.py`; wymusi to dokładne porównanie 870 plików oraz tylko trzech dopuszczonych zmian.

## Niezakończone przed 1.1

Pozostałe dynamiczne zaimki z odmianą, 81 użyć `Misc.STORY`, semantyczny audyt starszych map `DRAFT/OPTIONAL`, weryfikacja pokrycia wszystkich pól i nazw widocznych w grze, a także natywny test na Windows. Przejście testów struktur nie dowodzi semantycznej kompletności. Test gry na Windows nie był wykonywany.
