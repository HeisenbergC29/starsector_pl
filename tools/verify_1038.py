#!/usr/bin/env python3
"""Strict 1.0.38 map/grammar validation with optional whole-JAR bytecode proof.

13 original HistorianBarEvent getter callsites verified; this never claims
other callers or native Windows gameplay have been tested.
"""
from __future__ import annotations
import argparse,collections,csv,hashlib,json,re,subprocess,zipfile
from pathlib import Path
from apply_1038 import NEW,CORRECT,DATA,BAR,DONATION,STATUS,FIELDS
from verify_story_1033 import proof_class_files,class_entries,texts

ORIGINAL_SHA='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
HIST_CALLS={'getManOrWoman':(14,14,247),'getHeOrShe':(26,31,137,179,260,813),'getHimOrHer':(43,764),'getHisOrHer':(296,777)}
BASE='com.fs.starfarer.api.impl.campaign.intel.bar.events.BaseBarEventWithPerson'
DRAFT={'DRAFT_ONLY_NOT_INSTALLED','OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
 with p.open('r',encoding='utf8',newline='') as f:
  rdr=csv.DictReader(f);assert rdr.fieldnames==FIELDS;return list(rdr)

def validate_map(root):
 path=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';t=path/'translations'
 prev=rows(t/'TLUMACZENIA_JAR_1037.csv');cur=rows(t/'TLUMACZENIA_JAR_1038.csv')
 assert len(prev)==5245 and len(cur)==5254
 changed={(cl,en):(bef,aft) for cl,items in CORRECT.items() for en,(bef,aft) in items.items()}
 found=[]
 for a,b in zip(prev,cur):
  k=(a['source_class'],a['english_literal'])
  if k not in changed: assert a==b,('unapproved existing change',k)
  else:
   expected=changed[k];assert (a['polish_ascii_draft'],b['polish_ascii_draft'])==expected,(k,a,b)
   assert a['status']==b['status'] and a['english_literal']==b['english_literal']
   found.append(k)
 assert len(found)==len(changed)==12 and set(found)==set(changed)
 added={(cl,en):(pl,STATUS) for cl,xx in NEW.items() for en,pl in xx.items()}
 assert len(added)==9
 assert {(r['source_class'],r['english_literal']):(r['polish_ascii_draft'],r['status']) for r in cur[len(prev):]}==added
 keys=[(r['source_class'],r['english_literal']) for r in cur]
 assert len(set(keys))==len(keys)==5254 and all(x['polish_ascii_draft'].isascii() for x in cur)
 assert not any(cl==BASE and en in ('her','his','him','man','woman') for cl,en in keys)
 assert 'const version = "1038"' in (path/'main.go').read_text('utf8')
 assert '"1036", "1037", version}' in (path/'main.go').read_text('utf8')
 assert 'const edition = "1.0.38"' in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8')
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 assert meta['version']=='1.0.38' and meta['gameVersion']=='0.98a-RC8' and len(meta['replace'])==41
 data=[x for x in (root/'mod/data').rglob('*') if x.is_file()]
 assert len(data)==870 and all(x.read_bytes().isascii() for x in data)
 return {'api_map_rows':5254,'new_api':9,'corrected_api':12,'reviewable_draft_rows':sum(x['status'] in DRAFT for x in cur),'data_files':870}

def phrases(root):
 path=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1038.csv'
 mapping={(r['source_class'],r['english_literal']):r['polish_ascii_draft'] for r in rows(path)}
 def t(en):return mapping.get((BAR,en),en)
 result={}
 for sex in ('male','female'):
  male=sex=='male';person='mezczyzna' if male else 'kobieta'
  subject='on' if male else 'ona';him='mu' if male else 'jej';his='jego' if male else 'jej'
  p={
   'donation':(mapping[(DONATION,'... some promising leads that a ')]+ '20 000' + mapping[(DONATION,' donation would let ')]+him+mapping[(DONATION,' pursue')]),
   'option':t('Go over to the ')+person+t(' with the paper book and see what ')+subject+t(' wants'),
   'prompt':t('An old ')+person+t(' sits alone at a table, ')+t('leafing through what looks like a genuine hardcopy paper book. As you walk by, ')+subject+t(' looks up and offers the seat across from ')+him+'.',
   'greeting':t('"Welcome, welcome, please sit! I\'m sure you\'re wondering why I called you over."\n\n')+subject.capitalize()+t(' leans in as if conspiring, "')+t('I think we can help each other, you and I. See, I have the information," ')+subject+t(' taps the book, ')+t('"And you have the means."'),
   'after_backstory':'Po tych slowach '+subject+t(' leans back, looking pleased.'),
   'weary':t('A weary expression passes over the ')+person+t("'s face for just a moment before ")+subject+t(' resumes an energetic demeanor.'),
   'wrinkle':'Kolejna zmarszczka pojawia sie na '+his+t(' face at this.'),
   'thank':t('You thank ')+him+t(' for ')+his+t(' the information and get up to leave.'),
   'farewell':t('"See you again soon, somewhere!" ')+subject+t(' says. "In my line of work, even I don\'t ')+t('know for sure where I\'ll end up in a couple of months."'),
  }
  for k,v in p.items():
   assert v.isascii() and '  ' not in v and 'nie nie wiem' not in v and '""' not in v,(sex,k,v)
   assert not any(b in v for b in (' wants',' says.',' old ',' stands ',' him',' her',' his',' woman',' man ')),(sex,k,v)
   assert '\x00' not in v
  assert p['donation']=='... obiecujace tropy, ktore darowizna w wysokosci 20 000 pozwolilaby '+him+' zbadac'
  assert p['option'].startswith('Porozmawiaj z '+person)
  assert p['prompt'].startswith('Przy stoliku siedzi '+person+' w podeszlym wieku')
  assert p['greeting'].startswith('"Witaj, witaj') and '\n\n'+subject.capitalize()+' nachyla' in p['greeting']
  assert p['weary']=='Przez chwile '+person+' wyglada na osobe zmeczona, ale zaraz '+subject+' znow nabiera wigoru.'
  assert p['thank']=='Dziekujesz '+him+' za '+his+' informacje i wstajesz, zeby odejsc.'
  assert p['farewell'].endswith('W mojej pracy nawet ja nie wiem na pewno, gdzie bede za kilka miesiecy."')
  result[sex]=p
 return result

def check_jars(original,patched,root):
 assert sha(original)==ORIGINAL_SHA
 mapping={(r['source_class'],r['english_literal']):r['polish_ascii_draft'] for r in rows(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1038.csv')}
 summary=proof_class_files(original,patched,mapping)
 assert summary['modified_classes']==938 and summary['mapped_string_constants']==5252,summary
 with zipfile.ZipFile(original) as org,zipfile.ZipFile(patched) as pat:
  for cl,pairs in NEW.items():
   n=cl.replace('.','/')+'.class';before=texts(class_entries(org.read(n))[0]);after=texts(class_entries(pat.read(n))[0]);
   for en,pl in pairs.items():
    assert en in before and pl in after and en not in after,(cl,en)
  for cl,pairs in CORRECT.items():
   n=cl.replace('.','/')+'.class';before=texts(class_entries(org.read(n))[0]);after=texts(class_entries(pat.read(n))[0]);
   for en,(_,pl) in pairs.items():assert en in before and pl in after and en not in after,(cl,en)
  base=BASE.replace('.','/')+'.class';a=class_entries(org.read(base))[0];b=class_entries(pat.read(base))[0]
  assert a[143]==b[143] and texts(b)['her']>=1
 for jar in (original,patched):
  cmds=subprocess.run(['javap','-c','-p','-classpath',str(jar),BAR],capture_output=True,text=True,check=True).stdout
  hits={k:[] for k in HIST_CALLS}
  for line in cmds.splitlines():
   m=re.search(r'^\s*(\d+):\s+invokevirtual\s+#[0-9]+\s+// Method com/fs/starfarer/api/impl/campaign/intel/bar/events/historian/HistorianData\.(getManOrWoman|getHeOrShe|getHimOrHer|getHisOrHer):',line)
   if m:hits[m.group(2)].append(int(m.group(1)))
  assert {k:tuple(v) for k,v in hits.items()}=={k:tuple(sorted(v)) for k,v in HIST_CALLS.items()},hits
 for jar in (original,patched):
  s=subprocess.run(['javap','-c','-p','-classpath',str(jar),DONATION],capture_output=True,text=True,check=True).stdout
  assert re.search(r'^\s*36:\s+invokevirtual\s+#[0-9]+\s+// Method com/fs/starfarer/api/impl/campaign/intel/bar/events/historian/HistorianData\.getHimOrHer:',s,re.M),('DonationOffer getter shifted',jar)
 return {'original_sha256':sha(original),'patched_sha256':sha(patched),**summary,'historian_getter_calls_verified':14,'shared_her_base_index_143_unchanged':True}

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('worktree',type=Path)
 a.add_argument('--original-api',type=Path);a.add_argument('--patched-api',type=Path);a.add_argument('--previous-zip',type=Path)
 opt=a.parse_args();out=validate_map(opt.worktree);pv=phrases(opt.worktree);assert len(pv)==2 and all(len(v)==9 for v in pv.values());out['complete_gendered_phrase_variants']=18
 if opt.previous_zip:
  with zipfile.ZipFile(opt.previous_zip) as z:
   prev={k.removeprefix('Starsector_PL_ASCII/'):z.read(k) for k in z.namelist() if k.startswith('Starsector_PL_ASCII/data/')}
  curr={x.relative_to(opt.worktree/'mod').as_posix():x.read_bytes() for x in (opt.worktree/'mod/data').rglob('*') if x.is_file()}
  assert prev==curr and len(prev)==870;out['unchanged_data_files']=870
 if opt.original_api or opt.patched_api:
  assert opt.original_api and opt.patched_api
  out.update(check_jars(opt.original_api,opt.patched_api,opt.worktree))
 print(json.dumps(out,indent=2))
