# Starsector PL 1.0.17 — wydanie robocze 2026-11-11

**Zgodność:** Starsector 0.98a-RC8. **Cel 1.1 jeszcze NIE jest ukończony.**

## Zmiany względem 1.0.16

- **OBF +15:** 12 długich komunikatów samouczka dowodzenia flotą, 2 opisy wymagań przy usuwaniu modyfikacji kadłuba, 1 opis strumienia uzbrojenia.
- **API +2:** nazwa okrętu `Princess of Persea` → `Ksiezniczka Persei` oraz brakujący fragment `Knights of Ludd ` → `Rycerze Ludda `.
- **Korekta istniejącego API:** `Larger non-hostile colony in same system` miało błędne `Wieksza nieprzyjazna kolonia...`, poprawiono na `Wieksza niewroga kolonia w tym samym ukladzie`. Zmiana koryguje znaczenie, a nie liczbę pozycji mapy.
- Terminologia samouczka jest spójna z polskimi danymi: Wasp → Osa, Dagger → Sztylet, Gemini → Bliznieta, Rally carrier → Zbiorka lotniskowcow.
- 870/870 plików `data/` identycznych bajtowo z 1.0.16. Oryginalne komercyjne JAR **nie są** w repo ani paczce.

## Zweryfikowane na oryginalnych JAR (Linux)

| Test | Wynik |
|---|---|
| OBF 3140 zatwierdzonych referencji, 532 zmienione klasy | PASS |
| API 5094 zatwierdzone referencje, 934 zmienione klasy | PASS |
| Audyt: kod metod i niewskazane elementy JAR pozostają niezmienione | PASS |
| Manifest OBF: 532 zmienione sekcje sum dla 532 zmienionych klas | PASS |
| Świeża instalacja obu JAR i idempotencja | PASS |
| Aktualizacja 1.0.16 → 1.0.17 i identyczne wynikowe sumy | PASS |
| Przywracanie obu oryginalnych JAR z pełną zgodnością bajtową | PASS |
| Odmowa uszkodzonego OBF i API bez zmiany plików | PASS |
| Odtworzenie 1000 plików źródłowych z bazowego worktree | PASS |
| Go test i vet OBF, API, instalator | PASS |
| Trzy PE32+ Windows x64 — cross-build | PASS |
| `rules.csv` 11107 rekordów, 7371/7371 poprawnych opcji | PASS |
| ZIP 873 pliki, CRC, 870 danych | PASS |
| Test natywny Windows / uruchomiona gra | NIE WYKONANO |
| Pełne 100% tłumaczenia | NIE POTWIERDZONO |

**Oryginalne biblioteki:** OBF `5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8`; API `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`.

**Po patchowaniu:** OBF `c5035d4c06b747604652760b162ed163ebdf6a956d419963c38f594ad0fa1a11`; API `115b597f3b988850ef76f3d9a13beeb30af487c98fbf61a6658eb3f9b83fa9b8`.

## Paczka i odtwarzanie

Paczka użytkownika: `Starsector_PL_ASCII_0.98a_RC8_1.0.17_MINIMALNY.zip`

- Rozmiar: **11 277 508 B**
- SHA-256: `51d131098cbdcc8540dbf9ad192a008f09fcc20c0719940677e99aa6364e47fa`
- Paczka i `Starsector_PL_1.0.17_TESTY.json` znajdują się w prywatnej Bibliotece projektu.

```bash
python3 tools/restore_snapshot.py
python3 tools/apply_1013.py worktree
python3 tools/apply_1014.py worktree
python3 tools/apply_1015.py worktree
python3 tools/apply_1016.py worktree
python3 tools/apply_1017.py worktree
python3 tools/check_project.py worktree/mod
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
```

## Do wydania 1.1

1. Dalszy audyt wszystkich literałów faktycznie wyświetlanych przez OBF/API, dynamicznych wypowiedzi i wyświetlanych nazw.
2. Audyt semantyczny wcześniejszych map i błędnych tłumaczeń; duże grupy oznaczone `DRAFT` i `OPTIONAL` są instalowane mimo tych statusów.
3. Dalsza kontrola 529 niepodmienianych plików źródłowych, kontekstów i wariantów.
4. Test instalatora i rozgrywki na Windows; dotychczasowe testy techniczne Linux nie zastępują tej kontroli.
