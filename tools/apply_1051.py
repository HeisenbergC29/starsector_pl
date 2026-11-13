#!/usr/bin/env python3
"""Starsector PL 1.0.51: correct mixed officer personalities without altering identifiers.

Two UI text fragments are updated (class-scoped). One method-local pair of
bytecode constant-pool operands (two bytes total) is retargeted from logic IDs
to existing UI labels. This is a deliberately audited exception to the
otherwise strict bytecode-preservation rule.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,subprocess
from pathlib import Path

OLD='TLUMACZENIA_JAR_1050.csv'
NEW='TLUMACZENIA_JAR_1051.csv'
OLD_SHA='d2f6b355c58a8d2f0c9a5674e19bcaf7e24862ac4a3c28ad6ace97ce0024b41e'
CLASS='com.fs.starfarer.api.impl.campaign.FactionPersonalityPickerPluginImpl'
JVM_CLASS='com/fs/starfarer/api/impl/campaign/FactionPersonalityPickerPluginImpl.class'
ORIGINAL_CLASS_SHA='f1c37918b1ae8542f5f3673775e9343e34bd04c3c075c2a5752f6433ef354949'
FIELDS=['source_class','english_literal','polish_ascii_draft','status']
CORRECTIONS={
 '%s officers and ship commanders.':('%s oficerow i dowodcow okretow.','Oficerowie i dowodcy okretow: %s.'),
 'A mix of %s and %s officers and ship commanders.':('Mieszanka oficerow i dowodcow okretow o cechach %s i %s.','Oficerowie i dowodcy okretow: %s oraz %s.'),
}

def sha(b):return hashlib.sha256(b).hexdigest()
def once(s,old,new):
 if s.count(old)!=1:raise ValueError(('exactly one occurrence required',old,s.count(old)))
 return s.replace(old,new)
def readmap(path):
 with Path(path).open(encoding='utf8',newline='') as f:
  reader=csv.DictReader(f)
  if reader.fieldnames!=FIELDS:raise ValueError(('changed CSV columns',reader.fieldnames))
  return list(reader)
def serialize(rows):
 fp=io.StringIO(newline='')
 out=csv.DictWriter(fp,fieldnames=FIELDS,lineterminator='\r\n');out.writeheader();out.writerows(rows)
 return fp.getvalue().encode('utf8')
def corrected_rows(src):
 if len(src)!=5269:raise ValueError('Expected 5269 API rows')
 if len({(r['source_class'],r['english_literal']) for r in src})!=5269:raise ValueError('Duplicate translation key')
 out=[];count=0
 for row in src:
  r=row.copy();key=r['english_literal']
  if r['source_class']==CLASS and key in CORRECTIONS:
   old,new=CORRECTIONS[key]
   if r['polish_ascii_draft']!=old:raise ValueError(('unexpected prior UI translation',key,r['polish_ascii_draft']))
   if r['status']!='DRAFT_ONLY_NOT_INSTALLED':raise ValueError(('unexpected review status',key,r['status']))
   if old.count('%s')!=new.count('%s') or not new.isascii():raise ValueError(('placeholder corruption',key))
   r['polish_ascii_draft']=new;count+=1
  out.append(r)
 if count!=2:raise ValueError(('incorrect mapped changes',count))
 for row in out:
  if row['source_class']==CLASS and row['english_literal'] in ('aggressive','reckless','cautious','steady'):
   raise ValueError('Unexpected attempt to translate internal personality IDs')
 return out

GO_ADDITION = '''// Only the display call in addDescToTooltip is allowed to reference translated
// personality labels; the createPersonalityPicker method must continue to use
// lower-case technical personality IDs. Source class bytes are SHA-pinned.
const personalityClassPath = "com/fs/starfarer/api/impl/campaign/FactionPersonalityPickerPluginImpl.class"
const personalitySourceSHA = "f1c37918b1ae8542f5f3673775e9343e34bd04c3c075c2a5752f6433ef354949"
const personalityMixEnglish = "A mix of %s and %s officers and ship commanders."
const personalityMixPolish = "Oficerowie i dowodcy okretow: %s oraz %s."

func personalityPoolString(items []entry, i int) (string, error) {
    if i <= 0 || i >= len(items) || items[i].kind != 8 { return "", fmt.Errorf("not a CONSTANT_String: %d", i) }
    ref := int(items[i].ref)
    if ref <= 0 || ref >= len(items) || items[ref].kind != 1 { return "", fmt.Errorf("bad UTF8 reference at %d", i) }
    return string(items[ref].payload), nil
}

// This byte sequence includes the complete two-label UI construction and not
// the similarly spelled IDs in createPersonalityPicker. Both ldc opcodes, the
// array size, and the instruction lengths remain unchanged. Only two operands
// change: #44 -> #80 and #47 -> #84.
var personalityTooltipOriginal = []byte{0x2b, 0x12, 0x52, 0x25, 0x19, 0x04, 0x05, 0xbd, 0x00, 0x44, 0x59, 0x03, 0x12, 0x2c, 0x53, 0x59, 0x04, 0x12, 0x2f, 0x53}
func rewritePersonalityTooltipTail(tail []byte) ([]byte, error) {
    if bytes.Count(tail, personalityTooltipOriginal) != 1 { return nil, errors.New("personality display bytecode not unique or has changed") }
    at := bytes.Index(tail, personalityTooltipOriginal)
    out := append([]byte(nil), tail...)
    out[at+13] = 0x50 // existing translated UI label: Aggressive
    out[at+18] = 0x54 // existing translated UI label: Reckless
    return out, nil
}

func patchPersonalityTooltip(original, patched []byte, mapping map[string]string) ([]byte, error) {
    // The trigger is the new UI-only translation. Historical 1050 and older
    // tables skip this exception, so old-version detection remains exact.
    if mapping[personalityMixEnglish] != personalityMixPolish { return patched, nil }
    if hash(original) != personalitySourceSHA { return nil, errors.New("unexpected original personality class SHA-256") }
    before, originalTail, err := parseClass(original)
    if err != nil { return nil, err }
    after, patchedTail, err := parseClass(patched)
    if err != nil { return nil, err }
    for _, rule := range []struct{i int; en, pl string}{
        {44, "aggressive", "aggressive"},
        {47, "reckless", "reckless"},
        {80, "Aggressive", "Agresywny"},
        {84, "Reckless", "Brawurowy"},
    } {
        en, e := personalityPoolString(before, rule.i)
        if e != nil || en != rule.en { return nil, fmt.Errorf("source personality pool %d: expected %q, found %q: %v", rule.i, rule.en, en, e) }
        pl, e := personalityPoolString(after, rule.i)
        if e != nil || pl != rule.pl { return nil, fmt.Errorf("translated personality pool %d: expected %q, found %q: %v", rule.i, rule.pl, pl, e) }
    }
    if !bytes.Equal(original[originalTail:], patched[patchedTail:]) { return nil, errors.New("unexpected method-byte change before personality UI patch") }
    changed, err := rewritePersonalityTooltipTail(patched[patchedTail:])
    if err != nil { return nil, err }
    return append(append([]byte(nil), patched[:patchedTail]...), changed...), nil
}

'''
# String is included in the overlay in exact bytes, so CI reconstructs the same Go source.


def apply(root):
 root=Path(root);td=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 old=td/OLD;new=td/NEW
 if new.exists():raise FileExistsError('The 1.0.51 map already exists')
 if sha(old.read_bytes())!=OLD_SHA:raise ValueError('Wrong 1.0.50 source map')
 rows=readmap(old)
 if serialize(rows)!=old.read_bytes():raise ValueError('Baseline CSV not byte-exact round-trippable')
 newrows=corrected_rows(rows)
 new.write_bytes(serialize(newrows))
 go=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go'
 code=go.read_text('utf8')
 code=once(code,'const version = "1050"','const version = "1051"')
 code=once(code,'const exeVersion = "1.0.50"','const exeVersion = "1.0.51"')
 code=once(code,'"1047", "1048", "1049", version}', '"1047", "1048", "1049", "1050", version}')
 code=once(code,'PL ASCII patch up to 1.0.50','PL ASCII patch up to 1.0.51')
 code=once(code,'func jarApply(original []byte, table patches) (result, error) {',GO_ADDITION+'func jarApply(original []byte, table patches) (result, error) {')
 # The existing patch-class region, after source literal substitution but before
 # change-count accounting. Exactly one target; never modify earlier knownTables.
 insertion='''\t\t\tif len(pairs) > 0 {\n\t\t\t\tclcount++\n\t\t\t}'''
 hook='''\t\t\tif f.Name == personalityClassPath {\n\t\t\t\tpatched, err = patchPersonalityTooltip(raw, patched, mapping)\n\t\t\t\tif err != nil { return result{}, fmt.Errorf("personality UI exception: %w", err) }\n\t\t\t}\n'''
 code=once(code,insertion,hook+insertion)
 go.write_text(code,encoding='utf8')
 subprocess.run(['gofmt','-w',str(go)],check=True)
 t=Path(__file__).with_name('personality_1051_test.go')
 if not t.is_file():raise FileNotFoundError('Missing CI JVM operand regression tests')
 dest=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/personality_1051_test.go'
 if dest.exists():raise FileExistsError('Already installed 1.0.51 Go tests')
 dest.write_bytes(t.read_bytes())
 subprocess.run(['gofmt','-w',str(dest)],check=True)
 def edit(path,a,b):
  p=root/path;p.write_text(once(p.read_text('utf8'),a,b),encoding='utf8')
 edit('buildtools/NARZEDZIA_INSTALATOR/main.go','const edition = "1.0.50"','const edition = "1.0.51"')
 p=root/'mod/mod_info.json';meta=json.loads(p.read_text('utf8'))
 if meta['version']!='1.0.50' or meta['gameVersion']!='0.98a-RC8':raise ValueError('Wrong prior metadata')
 meta['version']='1.0.51';meta['description']=once(meta['description'],'1.0.50','1.0.51')
 p.write_text(json.dumps(meta,indent=2,ensure_ascii=True)+'\n',encoding='utf8')
 edit('mod/CZYTAJ.txt','STARSECTOR PL ASCII 1.0.50','STARSECTOR PL ASCII 1.0.51')
 with (root/'mod/CZYTAJ.txt').open('a',encoding='utf8') as f:
  f.write('\nPoprawiono opisy osobowosci oficerow. Dwa odwolania UI do technicznych identyfikatorow przeadresowano na istniejące etykiety polskie (2 bajty operandow ldc), bez zmiany logicznego losowania osobowosci. Wersja 1.1 nadal w opracowaniu.\n'.replace('istniejące','istniejace'))
 return {'version':'1.0.51','source_map_sha256':OLD_SHA,'new_map_sha256':sha(new.read_bytes()),'source_rows':5269,'new_rows':5269,'corrected_ui_texts':2,'exception_bytecode_ldc_operands':2,'exception_classes':1,'new_gameplay_test':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 print(json.dumps(apply(p.parse_args().worktree),indent=2))
