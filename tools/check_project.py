#!/usr/bin/env python3
"""Fail-closed structural checks for restored Starsector PL project data."""
import argparse
import csv
import io
import json
from pathlib import Path

EXPECTED_RULE_COLUMNS = ['id', 'trigger', 'conditions', 'script', 'text', 'options', 'notes']


def audit_mod(mod: Path):
    errors = []
    info_path = mod / 'mod_info.json'
    info = json.loads(info_path.read_text(encoding='utf-8'))
    if info.get('gameVersion') != '0.98a-RC8':
        errors.append('Wrong gameVersion in mod_info.json')
    files = [p for p in (mod / 'data').rglob('*') if p.is_file()]
    if len(files) != 870:
        errors.append(f'Expected 870 data files, got {len(files)}')
    non_ascii = [p.relative_to(mod).as_posix() for p in files if not p.read_bytes().isascii()]
    if non_ascii:
        errors.append(f'Non-ASCII data files: {non_ascii[:20]}')
    replaces = info.get('replace', [])
    if len(replaces) != len(set(replaces)):
        errors.append('Duplicate replace entries in mod_info.json')
    missing = [p for p in replaces if not (mod / p).is_file()]
    if missing:
        errors.append(f'Replace entries missing from package: {missing}')
    rules = mod / 'data' / 'campaign' / 'rules.csv'
    content = rules.read_bytes()
    with io.StringIO(content.decode('ascii'), newline='') as src:
        rd = csv.DictReader(src)
        if rd.fieldnames != EXPECTED_RULE_COLUMNS:
            errors.append('Unexpected rules.csv column structure')
        rows = list(rd)
    if len(rows) != 11107:
        errors.append(f'Expected 11107 dialog records, got {len(rows)}')
    options = 0
    for idx, r in enumerate(rows, start=2):
        if r['id'].startswith('#'):
            continue
        for opt in r['options'].splitlines():
            opt = opt.strip()
            if not opt or opt.startswith('#'):
                continue
            options += 1
            chunks = opt.split(':')
            if len(chunks) == 2 and chunks[0] and chunks[1]:
                continue
            if len(chunks) == 3 and chunks[1] and chunks[2]:
                try:
                    float(chunks[0])
                except ValueError:
                    pass
                else:
                    continue
            errors.append(f'Invalid option in row {idx} ({r["id"]}): {opt[:120]}')
    return {'data_files': len(files), 'dialog_records': len(rows), 'dialog_options': options,
            'replace_entries': len(replaces), 'non_ascii_files': len(non_ascii),
            'errors': errors}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mod', type=Path)
    args = ap.parse_args()
    report = audit_mod(args.mod)
    print(json.dumps(report, indent=2))
    raise SystemExit(1 if report['errors'] else 0)


if __name__ == '__main__':
    main()