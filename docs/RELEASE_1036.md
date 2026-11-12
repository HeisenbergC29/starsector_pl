# Starsector PL ASCII 1.0.36 — reflexive pronoun and planetary-shield context

**Target game:** Starsector 0.98a-RC8. **Target complete Polish release 1.1 is NOT finished.** The source maps, tooling and documentation are public. Copyrighted original game JARs and full commercial source texts stay private.

## What was actually changed

- Exactly one JVM `getHimOrHerself()` callsite was confirmed in the original 0.98a-RC8 API: `PlanetaryShieldBarEvent.optionSelected()` at bytecode offset 663. A `BaseBarEventWithPerson` getter returns `himself` or `herself`; the patched literal values are now `on` or `ona`.
- The surrounding 3 assembled `StringBuilder` fragments were reviewed and corrected together. The comparison now reads: `...[pilot] po tych wydarzeniach jest w znacznie gorszym stanie niz on/ona, a od tamtej pory upija sie do nieprzytomnosci ...`. The pilot's first name and subsequent settlement/preposition insertion are not changed. Both gender forms were checked offline. The location-preposition grammar still needs gameplay testing.
- A fourth correction in the same event changes the speaker-specific `Nie zyczylbym ...` into the gender-independent `Tego losu nie zycze ...`.
- The API map therefore gains **2 rows and corrects 4 previous rows**: 5242 → **5244** CSV rows, **5242 actual string replacements / 938 patched classes**. Existing OBF mappings stay identical to version 1.0.35 (3534 replacements / 539 classes).
- `mod/data/` remains **870/870 identical** to 1.0.35, including all dialogue changes from earlier versions. Only the mod version/README, combined installer edition, active API translation map and API patcher version changed.
- The shared `her` string #143 is still used in **both** `getHimOrHer()` and `getHisOrHer()` and is deliberately **untouched**. A global replacement would be unsafe. This release does not pretend to resolve the remaining gender cases.

## Evidence actually checked with the original commercial JAR

Original SHA-256 API: `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`.

Patched 1.0.36 API SHA-256: `892c20e354b0affa483894606461de4641e9afa3930b25ef83ba219e3f09a339`.

Patchable current OBF 1.0.33/1.0.35 SHA-256: `03729bc8e6ad0100ce4d0f7bf2f71bc198f917ff9e1b2fa5f9dacf4f35960a7a`.

Independent full-JAR compare: **938 modified `.class`**, **5242 approved `CONSTANT_String` replacements**, appended UTF-8 constant-pool entries only, **zero changed method/attribute bytecode**. Original and patched `javap` agree that the sole `getHimOrHerself()` invocation remains at bytecode offset 663. Both `her` getters still share the original #143 entry. No original/commercial JAR committed.

Actual installation tests: original→1.0.36, patched API 1.0.33 (used by 1.0.35)→1.0.36, using the **authentic OBF 1.0.33** as prerequisite, yield byte-identical API JARs. Re-apply is idempotent; verified restore returns the exact original SHA. A deliberately corrupted API JAR was rejected without changing its SHA.

Compiled **three Windows x64 PE32+ executables**. Go tests and vet passed on all three Go modules; **7371** dialogue options parsed, **zero invalid**; **9** negative source-map tests and **14** negative release-gate tests passed. These are offline tests, **not** a game launch on Windows.

## Manually reviewed API translations

The append-only [`API_SEMANTIC_REVIEW_1036.json`](API_SEMANTIC_REVIEW_1036.json) preserves the previous **58** immutable reviewed rows, and adds **20** contextually reviewed `PlanetaryShieldBarEvent` entries, with source/translation fingerprints, checked against original and patched class pools. The total is **78 reviewed offline**, leaving **3580** historical DRAFT/OPTIONAL entries without review. The old status `DRAFT_ONLY_NOT_INSTALLED` is misleading: it does not prevent patching.

There are now **25** newer literal rows in the tracked cohort (6 + 17 + 2). Thus **3683** tracked strings still lack gameplay verification, irrespective of offline review status.

## Gate status for complete 1.1

- Original Java pronoun getter **callsite inventory 219**; **1** of those has a completed offline contextual fix; **218** remain for contextual assessment, and all **219** need Windows/gameplay evidence. The 91 edited `rules.csv` rows and 183 references removed there are separate metrics, not JVM callsites.
- `Misc.STORY` **81/81 reviewed offline**, but **81/81** remain to be viewed in the running game.
- API historical semantic backlog **3580**; text completeness review unfinished.
- Native Windows rendering, interaction and save/reload test **not performed**. `docs/RELEASE_GATES_11.json` still blocks naming the release `1.1`.

## Repeat from the repository

```bash
python3 tools/restore_snapshot.py
for n in 1013 1014 1015 1016 1017 1018 1019 1020 1021 1022 1023 1024 1025 1026 1027 1028 1029 1030 1031 1032 1033 1034 1035 1036; do
  python3 "tools/apply_$n.py" worktree
done
python3 tools/verify_1036.py worktree
python3 tools/verify_review_1036.py worktree --prior-ledger docs/API_SEMANTIC_REVIEW_1033.json --ledger docs/API_SEMANTIC_REVIEW_1036.json
python3 tools/test_1036.py worktree --prior-ledger docs/API_SEMANTIC_REVIEW_1033.json --ledger docs/API_SEMANTIC_REVIEW_1036.json
python3 tools/check_release_gates_1036.py worktree --gates docs/RELEASE_GATES_11.json --prior-api-ledger docs/API_SEMANTIC_REVIEW_1033.json --api-ledger docs/API_SEMANTIC_REVIEW_1036.json --prior-rules-ledger docs/RULES_PRONOUN_REVIEW_1034.json --rules-ledger docs/RULES_PRONOUN_REVIEW_1035.json
python3 tools/test_release_gates_1036.py worktree --gates docs/RELEASE_GATES_11.json --prior-api-ledger docs/API_SEMANTIC_REVIEW_1033.json --api-ledger docs/API_SEMANTIC_REVIEW_1036.json --prior-rules-ledger docs/RULES_PRONOUN_REVIEW_1034.json --rules-ledger docs/RULES_PRONOUN_REVIEW_1035.json
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
python3 tools/package_1036.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.36_MINIMALNY.zip
```

With the user's private original/patched API JARs, run:

```bash
python3 tools/verify_1036.py worktree --original-api /PRIVATE/starfarer.api.jar --patched-api /PRIVATE/installed/starfarer.api.jar
python3 tools/verify_review_1036.py worktree --prior-ledger docs/API_SEMANTIC_REVIEW_1033.json --ledger docs/API_SEMANTIC_REVIEW_1036.json --original-api /PRIVATE/starfarer.api.jar --patched-api /PRIVATE/installed/starfarer.api.jar
```

## Player ZIP

`Starsector_PL_ASCII_0.98a_RC8_1.0.36_MINIMALNY.zip` — **15,403,739 bytes**, **873 files**, 870 data files + metadata/README + Windows x64 installer; CRC PASS. SHA-256: `4ead77404794dcc7872757c08fd8c0a205d47ae5c22da25b67feb473ea406f1c`.
