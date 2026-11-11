#!/usr/bin/env python3
"""Audit exact JVM CONSTANT_String coverage and review-status labels of translation maps.

Requires user's original JARs, not stored in the public repository.
Does not edit JARs, translation CSVs, or game files.
"""
import argparse
import collections
import csv
import hashlib
import json
import struct
import zipfile
from pathlib import Path

ORIGINALS = {
    'OBF': '5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8',
    'API': 'a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a',
}


def string_constants(data: bytes):
    if data[:4] != b'\xca\xfe\xba\xbe':
        raise ValueError('Invalid JVM .class header')
    size = struct.unpack_from('>H', data, 8)[0]
    i, pos, utf8, string_refs = 1, 10, {}, []
    while i < size:
        tag = data[pos]
        pos += 1
        if tag == 1:
            ln = struct.unpack_from('>H', data, pos)[0]
            pos += 2
            utf8[i] = data[pos:pos + ln]
            pos += ln
        elif tag in (3, 4, 9, 10, 11, 12, 17, 18):
            pos += 4
        elif tag in (5, 6):
            pos += 8
            i += 1
        elif tag in (7, 8, 16, 19, 20):
            target = struct.unpack_from('>H', data, pos)[0]
            pos += 2
            if tag == 8:
                string_refs.append(target)
        elif tag == 15:
            pos += 3
        else:
            raise ValueError(f'Unsupported class constant pool tag {tag}')
        i += 1
    return {utf8[ref].decode('utf-8', errors='replace') for ref in string_refs if ref in utf8}


def audit(label, original_jar, translation_csv):
    digest = hashlib.sha256(original_jar.read_bytes()).hexdigest()
    if digest != ORIGINALS[label]:
        raise ValueError(f'{label} JAR is not the expected Starsector 0.98a-RC8 original ({digest})')
    totals = collections.defaultdict(lambda: {'csv_rows': 0, 'constant_string_matches': 0})
    cache = {}
    with zipfile.ZipFile(original_jar) as archive, translation_csv.open(newline='', encoding='utf8') as source:
        all_classes = set(archive.namelist())
        rows = list(csv.DictReader(source))
        for record in rows:
            status = record.get('status', '(no status)')
            name = record['source_class'].replace('.', '/') + '.class'
            if name not in cache:
                cache[name] = string_constants(archive.read(name)) if name in all_classes else set()
            totals[status]['csv_rows'] += 1
            totals[status]['constant_string_matches'] += record['english_literal'] in cache[name]
    return {
        'original_sha256': digest,
        'csv_rows': len(rows),
        'matched_literals': sum(a['constant_string_matches'] for a in totals.values()),
        'review_statuses': dict(sorted(totals.items(), key=lambda x: -x[1]['constant_string_matches'])),
        'status_column_controls_installation': False,
        'note': 'Patchers match literals from all CSV rows; status is not an installation filter. A matched literal is not proof it is UI-visible.',
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--obf-jar', type=Path, required=True)
    ap.add_argument('--api-jar', type=Path, required=True)
    ap.add_argument('--obf-csv', type=Path, required=True)
    ap.add_argument('--api-csv', type=Path, required=True)
    ap.add_argument('--json-output', type=Path)
    args = ap.parse_args()
    report = {
        'OBF': audit('OBF', args.obf_jar, args.obf_csv),
        'API': audit('API', args.api_jar, args.api_csv),
    }
    result = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    if args.json_output:
        args.json_output.write_text(result, encoding='utf8')
    print(result)


if __name__ == '__main__':
    main()