#!/usr/bin/env python3
"""Read-only audit of Starsector's shared STORY word and grammatical pronouns.

Only original game JARs, supplied privately by their owner, are accepted.
Private output contains limited nearby source literals for translation review; do not
commit it or original JARs to GitHub. The public summary contains counts only.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, re, subprocess, zipfile
from pathlib import Path

ORIGINAL = {
    'OBF': '5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8',
    'API': 'a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a',
}
PATCHED_1029 = {
    'OBF': 'fe13bdd519414be15e290ab1fcf84724524ea5e2f133b1bae6ce4e12ad90e71a',
    'API': '030e3f3e1f4649de423a8dce5e64b0acd7849a9cd26063b38a87974eb954e0f2',
}
FIELD = 'Field com/fs/starfarer/api/util/Misc.STORY:Ljava/lang/String;'
# Process one instruction at a time and never cross a Java method boundary.
INSN = re.compile(r'^\s*(\d+):\s+(\S+).*?(?:// (.*))?$')
LITERAL = re.compile(r'// String (.*)$')
METHOD = re.compile(r'^  (?:public|private|protected|static|final|synchronized|abstract|native).*\);$')
BAR_CLASS = 'com.fs.starfarer.api.impl.campaign.intel.bar.events.BaseBarEventWithPerson'

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check_hash(path: Path, expected: str, kind: str) -> None:
    actual = sha(path)
    if actual != expected:
        raise ValueError(f'{kind} SHA mismatch: {actual} != {expected}')

def run_javap(jar: Path, classname: str) -> list[str]:
    proc = subprocess.run(['javap', '-classpath', str(jar), '-c', '-p', classname],
                          capture_output=True, text=True, check=True)
    return proc.stdout.splitlines()

def parse_methods(lines: list[str]) -> list[tuple[str, list[dict]]]:
    """Extract method-scoped bytecodes; preserve absolute bytecode offsets."""
    result = []
    name = None
    insns = []
    for line in lines:
        if METHOD.match(line):
            if name is not None:
                result.append((name, insns))
            name, insns = line.strip(), []
        if name is None:
            continue
        match = INSN.match(line)
        if match:
            insns.append({'offset': int(match.group(1)),
                          'opcode': match.group(2), 'raw': line.strip(),
                          'text': match.group(3) or ''})
    if name is not None:
        result.append((name, insns))
    return result

def contexts(jar: Path, classname: str) -> list[dict]:
    out = []
    for method, instructions in parse_methods(run_javap(jar, classname)):
        for ix, ins in enumerate(instructions):
            if FIELD not in ins['raw']:
                continue
            before = [m.group(1) for c in instructions[max(0,ix-25):ix]
                      if (m:=LITERAL.search(c['raw']))]
            after = [m.group(1) for c in instructions[ix+1:ix+26]
                     if (m:=LITERAL.search(c['raw']))]
            suffix = after[0] if after else None
            out.append({'method': method, 'offset': ins['offset'],
                        'before_literals': before[-3:], 'after_literals': after[:3],
                        'next_literal': suffix,
                        'next_is_point': bool(suffix and re.match(r'^\s*points?\b', suffix))})
    return out

def find_her_reuse(api_jar: Path) -> dict:
    methods = parse_methods(run_javap(api_jar, BAR_CLASS))
    ids = {}
    for name, instr in methods:
        for target in ('getHimOrHer', 'getHisOrHer'):
            if target+'(' not in name:
                continue
            candidates = []
            for ins in instr:
                if re.search(r'// String her$', ins['raw']):
                    match = re.search(r'#(\d+)\s+// String her$', ins['raw'])
                    assert match, (name, ins)
                    candidates.append(int(match.group(1)))
            assert len(candidates)==1,(name,candidates)
            ids[target]=candidates[0]
    assert len(ids)==2 and ids['getHimOrHer']==ids['getHisOrHer'],ids
    return {'class': BAR_CLASS, 'same_constant_pool_string_reference': True,
            'constant_pool_index': ids['getHimOrHer'],
            'methods': sorted(ids.keys()),
            'incompatibility': 'one shared her string requires different grammatical Polish forms'}

def audit(obf: Path, api: Path, patched_obf=None, patched_api=None, prior=None):
    jars = {'OBF': obf, 'API': api}
    for kind,path in jars.items():
        check_hash(path, ORIGINAL[kind],kind)
    source = {}
    for kind, jar in jars.items():
        with zipfile.ZipFile(jar) as z:
            classes = [p[:-6].replace('/', '.') for p in z.namelist()
                       if p.endswith('.class') and b'Misc' in z.read(p) and b'STORY' in z.read(p)]
        for cl in classes:
            spots=contexts(jar,cl)
            if spots:
                source[(kind,cl)] = spots
    total=sum(map(len,source.values()))
    bykind=collections.Counter({kind:sum(len(v) for (k,_),v in source.items() if k==kind)
                               for kind in jars})
    assert (total,len(source),bykind['OBF'],bykind['API']) == (81,24,65,16), (total,len(source),bykind)
    # A separately published legacy report establishes the broader 219 call-site scope;
    # it is optional so this audit can run using *only* originals and javap.
    if prior:
        previous=json.loads(prior.read_text(encoding='utf8'))
        assert previous['stats']['story']==81 and previous['stats']['pronoun']==219
    collision=find_her_reuse(api)
    patched = {}
    if patched_obf or patched_api:
        if not patched_obf or not patched_api:
            raise ValueError('Both patched JARs are required')
        for kind,path in [('OBF',patched_obf),('API',patched_api)]:
            check_hash(path,PATCHED_1029[kind], 'patched '+kind)
        for (kind,cl), old in source.items():
            path = patched_obf if kind == 'OBF' else patched_api
            new=contexts(path,cl)
            assert [(x['method'],x['offset']) for x in new] == [(x['method'],x['offset']) for x in old]
            patched[(kind,cl)] = new
        misc=run_javap(patched_api,'com.fs.starfarer.api.util.Misc')
        assert any('// String story' in line for line in misc),'STORY may have been changed'
    records=[]
    for key, spots in sorted(source.items()):
        for i,spot in enumerate(spots):
            rec={'jar':key[0],'class':key[1],**spot}
            if patched:
                rec['patched_1029']={k:v for k,v in patched[key][i].items()
                                      if k in ('before_literals','after_literals','next_literal')}
            records.append(rec)
    count_suffix=sum(x['next_is_point'] for x in records)
    # Every match is method-scoped. Discrepancies against historical 69 are a
    # useful signal rather than an excuse to fake that number.
    summary={'game_version':'0.98a-RC8','baseline':'1.0.29',
             'original_SHA256':ORIGINAL,'patched_1029_SHA256':PATCHED_1029 if patched else None,
             'story_field_reads':total,'classes_using_story':len(source),
             'story_jar_counts':dict(bykind),'method_scoped_next_point_literal':count_suffix,
             'historical_loose_lookahead_point_count':69,
             'pronoun_calls_from_prior_audit':219 if prior else 'not_rechecked',
             'her_aliasing':collision,
             'translation_status':'BLOCKED: no blanket replacement of shared STORY/her',
             'native_windows_gameplay_tested':False}
    return summary,{'summary':summary,'references':records}

def main():
    p=argparse.ArgumentParser()
    for arg in ('obf','api','out','summary'):
        p.add_argument('--'+arg,type=Path,required=True)
    for arg in ('patched-obf','patched-api','prior'):
        p.add_argument('--'+arg,type=Path)
    a=p.parse_args()
    summary,detail=audit(a.obf,a.api,a.patched_obf,a.patched_api,a.prior)
    a.out.write_text(json.dumps(detail,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
    a.summary.write_text(json.dumps(summary,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps(summary,ensure_ascii=True,indent=2))
if __name__=='__main__':main()
