#!/usr/bin/env python3
"""Verify 1.0.17 translation delta and combat tutorial terminology (no game files needed)."""
from collections import Counter
from pathlib import Path
import argparse
import csv
import json
import re

MARKUP = [r'<[^<>]+>', r'\{\{[^{}]+\}\}', r'\$[A-Za-z_][\w]*',
          r'%(?:(?:\d+)\$)?[-+# 0,(]*(?:\d+)?(?:\.\d+)?[a-zA-Z%]']
FIX = ('com.fs.starfarer.api.impl.campaign.population.CoreImmigrationPluginImpl',
       'Larger non-hostile colony in same system')

def rows(filename):
    with filename.open(newline='', encoding='utf-8') as stream:
        records = list(csv.DictReader(stream))
    keys = [(r['source_class'], r['english_literal']) for r in records]
    assert len(keys) == len(set(keys)), 'Duplicate source key'
    return {key: value for key, value in zip(keys, records)}

def check(worktree):
    base = worktree / 'buildtools'
    obf_old = rows(base / 'NARZEDZIA_OBF/TLUMACZENIA_OBF_10116.csv')
    obf_new = rows(base / 'NARZEDZIA_OBF/TLUMACZENIA_OBF_10117.csv')
    api_old = rows(base / 'NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1016.csv')
    api_new = rows(base / 'NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1017.csv')
    assert set(obf_old).issubset(obf_new)
    assert set(api_old).issubset(api_new)
    obf_added = [v for k, v in obf_new.items() if k not in obf_old]
    api_added = [v for k, v in api_new.items() if k not in api_old]
    assert len(obf_added) == 15 and len(api_added) == 2, (len(obf_added), len(api_added))
    for key, previous in obf_old.items():
        assert obf_new[key] == previous, ('OBF historical row modified', key)
    modified = [key for key, previous in api_old.items() if previous != api_new[key]]
    assert modified == [FIX], modified
    assert api_old[FIX]['polish_ascii_draft'] == 'Wieksza nieprzyjazna kolonia w tym samym ukladzie'
    assert api_new[FIX]['polish_ascii_draft'] == 'Wieksza niewroga kolonia w tym samym ukladzie'
    for record in obf_added + api_added:
        eng, pl = record['english_literal'], record['polish_ascii_draft']
        assert pl.isascii() and pl.strip(), ('non-ASCII or blank target', record['source_class'])
        assert eng.count('\n') == pl.count('\n'), ('newline mismatch', record['source_class'])
        for rule in MARKUP:
            assert Counter(re.findall(rule, eng)) == Counter(re.findall(rule, pl)), ('marker mismatch', rule, eng[:100])
        assert record['status'] == 'VERIFIED_JAVAP_UI_CALLSITE_1017'
    tutorial = [v for v in obf_added if v['source_class'].startswith('com.fs.starfarer.tutorial.oOOO.')]
    assert len(tutorial) == 12, len(tutorial)
    tutorial_text = '\n'.join(v['polish_ascii_draft'] for v in tutorial)
    assert 'Wasp' not in tutorial_text and 'Gemini' not in tutorial_text and 'Dagger' not in tutorial_text
    for name in ('Osa', 'Sztylet', 'Bliznieta', 'Zbiorka lotniskowcow'):
        assert name in tutorial_text, name
    carrier = [r for r in obf_new.values() if r['english_literal'] == 'Rally carrier']
    assert any(r['polish_ascii_draft'] == 'Zbiorka lotniskowcow' for r in carrier)
    strike = [r for r in obf_new.values() if r['english_literal'] == 'Rally strike force']
    assert any(r['polish_ascii_draft'] == 'Zbiorka grupy uderzeniowej' for r in strike)
    return {'OBF_new': 15, 'API_new': 2, 'API_semantic_correction': 1,
            'tutorial_paragraphs': 12, 'markup_check': 'PASS',
            'tutorial_ship_names_and_commands': 'PASS', 'historical_map_unchanged_except_intended_correction': 'PASS'}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('worktree', type=Path)
    arg = ap.parse_args()
    print(json.dumps(check(arg.worktree), indent=2))

if __name__ == '__main__':
    main()