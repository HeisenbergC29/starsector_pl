#!/usr/bin/env python3
"""Read-only, reproducible localization risk audit of the current 1.0.21 worktree.

This produces candidates for HUMAN review. It is not a coverage percentage,
does not edit source material, and does not assert that a literal is UI-visible.
"""
import argparse
import collections
import csv
import json
import re
from pathlib import Path

MAPS = {
    "OBF": "buildtools/NARZEDZIA_OBF/TLUMACZENIA_OBF_10121.csv",
    "API": "buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1021.csv",
}
# Deliberately narrow: avoid confusing ordinary punctuation with dynamic tokens.
TOKENS = re.compile(
    r"\$[A-Za-z_][A-Za-z_0-9]*"
    r"|\{(?:\d+|[A-Za-z_][A-Za-z_0-9]*)(?:[:!][^{}]*)?\}"
    r"|%(?:(?:\d+)\$)?[-+# 0,(]*(?:\d+)?(?:\.\d+)?[a-zA-Z%]"
)
ENGLISH = re.compile(
    r"\b(?:the|your|you|with|when|during|destroy|capture|press|"
    r"select|ship|ships|weapon|weapons|mission|enemy|enemies|"
    r"deployment|objectives|objectives|success|failure)\b", re.I
)
MAX_EXAMPLES = 14


def snippet(s):
    return s.replace("\r", "\\r").replace("\n", "\\n")[:115]


def signatures(s):
    return collections.Counter(TOKENS.findall(s))


def map_audit(path):
    counters = collections.Counter()
    examples = collections.defaultdict(list)
    by_key = {}
    statuses = collections.Counter()
    with path.open(newline="", encoding="utf-8-sig") as stream:
        records = csv.DictReader(stream)
        needed = {"source_class", "english_literal", "polish_ascii_draft", "status"}
        if not needed.issubset(records.fieldnames or []):
            raise ValueError(f"Unexpected CSV headers: {path}, {records.fieldnames}")
        for line, row in enumerate(records, 2):
            counters["rows"] += 1
            source = row["english_literal"]
            target = row["polish_ascii_draft"]
            key = (row["source_class"], source)
            status = row["status"]
            statuses[status] += 1
            if target == source and len(source.strip()) >= 5 and re.search("[A-Za-z]", source):
                flag = "unchanged_long_literal"
            elif not target.strip() and source.strip():
                flag = "empty_translation"
            else:
                flag = None
            if flag:
                counters[flag] += 1
                if len(examples[flag]) < MAX_EXAMPLES:
                    examples[flag].append({"line": line, "class": row["source_class"], "source": snippet(source), "status": status})
            if key in by_key and by_key[key] != target:
                counters["conflicting_translation"] += 1
                if len(examples["conflicting_translation"]) < MAX_EXAMPLES:
                    examples["conflicting_translation"].append({"line": line, "class": row["source_class"], "source": snippet(source), "first": snippet(by_key[key]), "second": snippet(target)})
            by_key.setdefault(key, target)
            if signatures(source) != signatures(target):
                counters["token_drift"] += 1
                if len(examples["token_drift"]) < MAX_EXAMPLES:
                    examples["token_drift"].append({"line": line, "class": row["source_class"], "source": snippet(source), "target": snippet(target)})
            if source.count("\\n") != target.count("\\n"):
                counters["literal_newline_drift"] += 1
                if len(examples["literal_newline_drift"]) < MAX_EXAMPLES:
                    examples["literal_newline_drift"].append({"line": line, "class": row["source_class"], "source": snippet(source), "target": snippet(target)})
    return {"counts": dict(counters), "statuses": dict(statuses.most_common()), "examples": dict(examples)}


def mission_audit(mod):
    mission_files = sorted((mod / "data" / "missions").glob("*/mission_text.txt"))
    untranslated_candidates = []
    for f in mission_files:
        for i, line in enumerate(f.read_text(encoding="ascii").splitlines(), 1):
            if ENGLISH.search(line) and len(untranslated_candidates) < 35:
                untranslated_candidates.append({
                    "file": f.relative_to(mod).as_posix(), "line": i, "text": snippet(line)
                })
    return {
        "translated_mission_text_file_count": len(mission_files),
        "files": [f.relative_to(mod).as_posix() for f in mission_files],
        "english_word_candidates": untranslated_candidates,
        "warning": "English-word candidates are heuristics; names/identifiers and Polish context may cause false positives.",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("worktree", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    report = {
        "base": "Starsector PL 1.0.12 snapshot",
        "map_audit": {name: map_audit(args.worktree / path) for name, path in MAPS.items()},
        "mission_audit": mission_audit(args.worktree / "mod"),
        "scope": "Static read-only; no private original JAR access or in-game verification.",
    }
    payload = json.dumps(report, indent=2, ensure_ascii=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
