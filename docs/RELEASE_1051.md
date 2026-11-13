# Starsector PL ASCII 1.0.51 — rozdzielenie nazw osobowosci w UI od identyfikatorow technicznych

**Data:** 2026-11-13  
**Gra:** Starsector 0.98a-RC8  
**Baza:** 1.0.50 (`TLUMACZENIA_JAR_1050.csv` SHA-256 `d2f6b355c58a8d2f0c9a5674e19bcaf7e24862ac4a3c28ad6ace97ce0024b41e`).  
**Wynik:** `TLUMACZENIA_JAR_1051.csv` SHA-256 `099abe6d62264e6b1d4ff66b9aba196ecb7d11845b7d2b2207aab4a8b8f66aa4`.  
**Status:** robocze wydanie 1.0.51, **NIE** pelna lokalizacja 1.1.

## Udokumentowane wyjatkowe poprawienie dwoch operandow JVM

W `com.fs.starfarer.api.impl.campaign.FactionPersonalityPickerPluginImpl` potwierdzono na oryginalnym JAR (SHA klasy `f1c37918b1ae8542f5f3673775e9343e34bd04c3c075c2a5752f6433ef354949`), ze:

- `createPersonalityPicker()` uzywa **technicznych** identyfikatorow `cautious`, `steady`, `aggressive` i `reckless`; musza pozostac angielskie.
- `addDescToTooltip()` przekazuje nazwy osobowosci do **widocznego** `TooltipMakerAPI.addPara`. Przy pojedynczych cechach uzywa juz odrebnych stalych `Cautious`, `Steady`, `Aggressive` i `Reckless`, ktore mapa tlumaczy jako `Ostrozny`, `Opanowany`, `Agresywny` i `Brawurowy`.
- Dla mieszanego zachowania klasowy UI uzywal **technicznych** `aggressive` i `reckless`, a wiec pokazywal angielski tekst w polskiej podpowiedzi.

Zmieniono **wylacznie dwa odwolania `ldc` wewnatrz `addDescToTooltip()`**: indeks JVM `#44` na istniejacy indeks etykiety `#80` oraz `#47` na `#84`. Sa to dwie zmienione wartosci operandow po jednym bajcie; dlugosc instrukcji, ich kody operacji, stos JVM, kolejność wykonania, polskie mapowanie pozostalych napisow i wszystkie instrukcje `createPersonalityPicker()` zostaja bez zmian. **To swiadomy, dokladnie opisany wyjatek od historycznej reguly niezmieniania bajtkodu — nie wolno uogolniac go na inne klasy.** Oryginalny SHA klasy oraz unikalny 20-bajtowy fragment otaczajacy oba `ldc` sa warunkami wykonania patcha. Patcher odmawia zmiany dla klasy o innych bajtach.

Poprawiono ponadto obie postaci tekstu podpowiedzi (tylko kolumna `polish_ascii_draft`):

| Kontekst | Przed | Po |
| --- | --- | --- |
| Pojedyncza osobowosc | `%s oficerow i dowodcow okretow.` | `Oficerowie i dowodcy okretow: %s.` |
| Mieszana osobowosc | `Mieszanka oficerow i dowodcow okretow o cechach %s i %s.` | `Oficerowie i dowodcy okretow: %s oraz %s.` |

Skladany wynik, np. **`Oficerowie i dowodcy okretow: Agresywny oraz Brawurowy.`**; pozostale warianty: `Ostrozny`, `Opanowany`, `Agresywny`, `Brawurowy`. Zostaly zachowane oba `%s` w mieszanym tekstowym szablonie, opcje kolorowania `addPara` i wszystkie angielskie techniczne nazwy. Nie modyfikowano `rules.csv`, zadnych 870 plikow danych ani OBF.

## Weryfikacja na oryginalnych komercyjnych JAR

- Zmodyfikowanych klas API wzgledem oryginalu: **938**; wzgledem 1.0.50: **jedna** (`FactionPersonalityPickerPluginImpl`).
- `tools/private_jvm_1051.py` porownuje strukture puli stalych i kod wszystkich zmienionych klas. We wskazanej klasie: **dokladnie 2 dopuszczone bajty operandow**, kazdy inny bajt wykonywalnego kodu JVM identyczny. 0 dodatkowych zmian instrukcji.
- `javap -c -p` potwierdza `ldc #80` / `ldc #84` w widocznym interfejsie, przy niezmienionych `ldc #44` / `ldc #47` w `createPersonalityPicker()`.
- Oryginalny API SHA-256: `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`.
- 1.0.50 API SHA-256: `35e086aed9380cf481bd6e48bfc29017cb5ee94012e5292953c9d53e44a540df`.
- 1.0.51 API SHA-256: `cf26c3aa2885df954f4914b584ff1552b3b3c8f8d9290adfb8a03a9d6dff7a13`.
- **Fresh instalacja = prawdziwy upgrade 1.0.50 → 1.0.51**; ponowna aplikacja, odmowa dla ZIP z naruszona metadana i przywrocenie oryginalu: PASS.
- Dwa nowe przypadki testow Go: podmiana **wylacznie** docelowych operandow (w tym sztucznie zmienione/wielokrotne wzorce) i brak wyjatku dla historycznych tabel. 8 testow negatywnych danych API.
- `docs/API_SEMANTIC_REVIEW_1051.json`: 312 poprzednich rekordow bez zmian i 2 nowe semantyczne recenzje. Stan: **314/3658** historycznych wierszy offline; **3344** pozostale. Zaliczenie nie jest rownowazne natywnemu testowi w grze.
- Wszystkie **870 danych** identyczne z 1.0.50, nowe metadane instalatora. Komercyjne JAR nie sa publikowane ani pakowane.

## Reprodukcja

Odtworz GitHub snapshot 1.0.12 z nakladkami `apply_1013.py` ... `apply_1050.py`, nastepnie:

```bash
python3 tools/apply_1051.py worktree
python3 tools/verify_1051.py worktree
python3 tools/test_1051.py worktree
python3 tools/verify_review_1051.py worktree --previous docs/API_SEMANTIC_REVIEW_1050.json --ledger docs/API_SEMANTIC_REVIEW_1051.json
python3 tools/check_release_gates_1051.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/API_SEMANTIC_REVIEW_1050.json --ledger docs/API_SEMANTIC_REVIEW_1051.json
python3 tools/test_release_gates_1051.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/API_SEMANTIC_REVIEW_1050.json --ledger docs/API_SEMANTIC_REVIEW_1051.json
(cd worktree && sh build_windows.sh)
python3 tools/package_1051.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.51_MINIMALNY.zip
```

Opcjonalnie na **prywatnych oryginalnych JAR**: `tools/private_jvm_1051.py` i `tools/private_upgrade_1051.py` wraz z Go patcherami Linux. Raporty `docs/JVM_PERSONALITY_EXCEPTION_1051.json`, `docs/UPGRADE_1051.json` sa tylko anonimowymi licznikami / SHA, bez bajtow bibliotek.

## Pozostale blokady docelowej 1.1

**3344** historycznych wpisow API do semantycznej recenzji, **186** nieprzejrzanych getter-callsite Java, nadal nierozwiazana wspoldzielona stala `her` w `BaseBarEventWithPerson` i 2275 surowych zmiennych zaimkowych w 1139 wierszach `rules.csv` (kandydaci, nie potwierdzone bledy). Brak testu natywnej rozgrywki Windows i pelnego audytu kazdego wyswietlanego tekstu. **Nie oznaczac jako 1.1.**
