#!/usr/bin/env python3
"""Classify files kept unchanged by a Starsector data-overlay localization.

This is a *coverage audit*, not proof that code scripts or variant names are
invisible. Never automatically translate technical IDs or raw structure.
"""
from __future__ import annotations
import argparse,collections,csv,json,re
from pathlib import Path

def rows(path):
    with path.open('r',encoding='utf8',newline='') as f:return {r['id']:r for r in csv.DictReader(f)}

def classify(original: Path, overlay: Path) -> tuple[dict,dict]:
    src=original/'data' if (original/'data').is_dir() else original
    dst=overlay/'data' if (overlay/'data').is_dir() else overlay
    assert src.is_dir() and dst.is_dir()
    original_files={p.relative_to(src):p for p in src.rglob('*') if p.is_file()}
    overlay_files={p.relative_to(dst):p for p in dst.rglob('*') if p.is_file()}
    assert len(original_files)==1399,len(original_files)
    assert len(overlay_files)==870,len(overlay_files)
    assert set(overlay_files).issubset(original_files),'Overlay contains source paths not in original'
    omitted=sorted(set(original_files)-set(overlay_files))
    assert len(omitted)==529,len(omitted)
    base_ship=rows(src/'hulls/ship_data.csv')
    translated_ship=rows(dst/'hulls/ship_data.csv')
    entries=[];candidates=[];hull_checked=0
    for relative in omitted:
        path=original_files[relative];suffix=relative.suffix
        entry={'path':relative.as_posix(),'suffix':suffix,'classification':'untouched_reference'}
        if suffix in ('.png','.jpg'):
            entry['classification']='image_data'
        elif suffix=='.java':
            entry['classification']='script_manual_check'
        elif relative==Path('codex/game_mechanics.txt'):
            contents=(src/'codex/text_codex_entries.csv').read_text('utf8')
            assert '#data/codex/game_mechanics.txt' in contents
            entry['classification']='disabled_codex'
        elif suffix=='.ship':
            names=re.findall(r'"hullName"\s*:\s*"([^"]+)"',path.read_text('utf8'))
            if names:
                assert len(names)==1
                rid=relative.stem
                assert rid in base_ship and rid in translated_ship,rid
                entry['hullName']=names[0]
                assert base_ship[rid]['name']==names[0],(rid,names[0],base_ship[rid]['name'])
                if translated_ship[rid]['name'] != names[0]:
                    entry['classification']='hull_name_conflict_review'
                    candidates.append(entry)
                else:
                    hull_checked+=1;entry['classification']='hull_name_equals_localized_csv'
            else:entry['classification']='ship_without_hull_name'
        elif suffix=='.variant':
            names=re.findall(r'"displayName"\s*:\s*"([^"]+)"',path.read_text('utf8'))
            if names:
                entry['displayName']=names;entry['classification']='variant_display_name_manual_check';candidates.append(entry)
        entries.append(entry)
    summary={'game_version':'0.98a-RC8','original_files':len(original_files),
             'localized_overlay_files':len(overlay_files),'unmodified_source_files':len(omitted),
             'by_extension':dict(sorted(collections.Counter(x['suffix'] for x in entries).items())),
             'classifications':dict(sorted(collections.Counter(x['classification'] for x in entries).items())),
             'hull_names_identical_to_localized_csv':hull_checked,
             'unresolved_hull_name_conflicts':sum(x['classification']=='hull_name_conflict_review' for x in candidates),
             'variant_display_name_review_count':sum(x['classification']=='variant_display_name_manual_check' for x in candidates),
             'java_scripts_pending_manual_callsite_review':sum(x['classification']=='script_manual_check' for x in entries),
             'meaning_or_runtime_visibility_fully_verified':False}
    return summary,{'summary':summary,'entries':entries,'candidates':candidates}

def main():
    p=argparse.ArgumentParser();p.add_argument('--original',type=Path,required=True)
    p.add_argument('--localized',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--summary',type=Path,required=True)
    args=p.parse_args();summary,detail=classify(args.original,args.localized)
    args.out.write_text(json.dumps(detail,ensure_ascii=True,indent=2)+'\n')
    args.summary.write_text(json.dumps(summary,ensure_ascii=True,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=True,indent=2))
if __name__=='__main__':main()
