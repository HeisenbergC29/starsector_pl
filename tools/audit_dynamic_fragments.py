#!/usr/bin/env python3
"""Read-only audit of Java-composed, user-facing strings in Starsector PL.

Requires privately supplied *original* 0.98a-RC8 JARs and the restored 1.0.17
worktree. Writes no game files or proprietary binary material to the repository.
This detects hard obstacles to complete localization; it is not a patcher.
"""
import argparse
import collections
import csv
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path

ORIGINAL_SHA = {
    'obf': '5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8',
    'api': 'a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a',
}
PRONOUN_CLASS = 'com.fs.starfarer.api.impl.campaign.intel.bar.events.BaseBarEventWithPerson'
SHIELD_CLASS = 'com.fs.starfarer.api.impl.campaign.intel.bar.events.PlanetaryShieldBarEvent'
TOOLTIPS = [
    'com.fs.starfarer.coreui.refit.ModPickerDialogV3$PermaModInfoWidget$1',
    'com.fs.starfarer.ui.newui.FleetMemberRecoveryDialog$7',
]


def jclass(jar, name):
    with zipfile.ZipFile(jar) as z:
        return z.read(name.replace('.', '/') + '.class')


def javap(jar, name):
    proc = subprocess.run(['javap', '-classpath', str(jar), '-c', '-p', name],
                          check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True)
    return proc.stdout


def mapped(worktree, kind):
    prefix = worktree / 'buildtools'
    filename = (prefix / 'NARZEDZIA_OBF/TLUMACZENIA_OBF_10117.csv' if kind == 'obf'
                else prefix / 'NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1017.csv')
    with filename.open(newline='', encoding='utf-8') as f:
        records = list(csv.DictReader(f))
    return {(r['source_class'], r['english_literal']): r for r in records}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--obf', type=Path, required=True)
    ap.add_argument('--api', type=Path, required=True)
    ap.add_argument('--worktree', type=Path, required=True)
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    for key in ('obf', 'api'):
        jar = getattr(args, key)
        assert hashlib.sha256(jar.read_bytes()).hexdigest() == ORIGINAL_SHA[key], f'Unexpected {key.upper()} original'
    obf_map = mapped(args.worktree, 'obf')
    api_map = mapped(args.worktree, 'api')
    pronoun_text = javap(args.api, PRONOUN_CLASS)
    methods = {}
    for name in ('getManOrWoman', 'getHeOrShe', 'getHimOrHer', 'getHimOrHerself', 'getHisOrHer'):
        match = re.search(r'(?m)^  protected java\.lang\.String ' + name + r'\(\);\s+Code:\s*(.*?)(?=\n  (?:protected|public|private) |\Z)', pronoun_text, re.S)
        if not match:
            raise AssertionError('Missing method: ' + name)
        values = re.findall(r'// String ([^\n]+)', match.group(1))
        methods[name] = values
    assert methods['getHeOrShe'] == ['he', 'she']
    assert methods['getHimOrHer'] == ['him', 'her']
    assert methods['getHisOrHer'] == ['his', 'her']
    assert not any((PRONOUN_CLASS, v) in api_map for values in methods.values() for v in values), 'Prior map state changed: re-audit'
    shield_code = javap(args.api, SHIELD_CLASS)
    shield_hits = {m: len(re.findall(r'// Method ' + m + r':', shield_code)) for m in methods}
    shield_rows = [v for (cls, _), v in api_map.items() if cls == SHIELD_CLASS]
    shield_unmapped = []
    for needle in (' lost eyes.', ' seat, cybernetic eyes'):
        assert needle.encode() in jclass(args.api, SHIELD_CLASS)
        # This is intentionally only a prefix/substring diagnostic; no binary content exported.
        shield_unmapped.append({'prefix': needle, 'mapped': any(cls == SHIELD_CLASS and needle in literal for cls, literal in api_map)})
    tooltips = []
    for cls in TOOLTIPS:
        text = javap(args.obf, cls)
        snippet = 'Bonus experience doubles your experience gain'
        assert snippet in text
        assert 'Misc.STORY' in text
        assert (cls, next((s for c,s in obf_map if c == cls and s.startswith(snippet)), '')) not in obf_map
        tooltips.append({
            'class': cls,
            'missing_leading_bonus_experience_literal': True,
            'uses_dynamic_misc_story': text.count('Field com/fs/starfarer/api/util/Misc.STORY:') == 2,
            'already_translated_following_fragments': sum(1 for (c, s) in obf_map if c == cls and s in (' point", eventually compensating ', 'for the use of one ', ' point entirely.')),
        })
    misc_text = javap(args.api, 'com.fs.starfarer.api.util.Misc')
    assert re.search(r'// String story\s*\n\s*\d+: putstatic.*Field STORY:', misc_text), 'Misc.STORY initializer changed'
    result = {
        'input_release': '1.0.17', 'verified_original_jar_checksums': True,
        'dynamic_pronouns': {'class': PRONOUN_CLASS, 'original_method_literals': methods,
                             'api_translation_map_entries_for_these_literals': 0,
                             'shared_source_literal_her': ['getHimOrHer', 'getHisOrHer'],
                             'shared_her_requires_context_specific_polish': True,
                             'planetary_shield_method_call_count': shield_hits,
                             'planetary_shield_mapped_fragments': len(shield_rows),
                             'planetary_shield_review_statuses': dict(collections.Counter(r['status'] for r in shield_rows)),
                             'unmapped_examples': shield_unmapped},
        'bonus_experience': {'misc_story_original_value': 'story',
                             'misc_story_translation_entry_exists': ('com.fs.starfarer.api.util.Misc', 'story') in api_map,
                             'tooltip_classes': tooltips},
        'status': 'CONFIRMED_UNRESOLVED',
        'warning': 'Do not blindly replace shared pronoun literals or Misc.STORY without callsite and technical-reference audit.',
    }
    content = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.out:
        args.out.write_text(content, encoding='utf-8')
    print(content)


if __name__ == '__main__':
    main()