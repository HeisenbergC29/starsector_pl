#!/usr/bin/env python3
"""Synthetic negative and positive fixtures for original-vs-localized data audit."""
import tempfile,unittest
from pathlib import Path
from verify_source_fields_1021 import audit

class SourceIntegrityTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();base=Path(self.temp.name)
  self.old=base/'original';self.new=base/'translated'
  for p in (self.old,self.new):p.mkdir()
 def tearDown(self):self.temp.cleanup()
 def put(self,path,a,b):
  for root,val in ((self.old,a),(self.new,b)):
   f=root/path;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(val)
 def test_allowed_quoted_values(self):
  self.put('world/factions/hegemony.faction',b'{"displayName":"Hegemony", "id":"hegemony", "growth":4}',b'{"displayName":"Hegemonia", "id":"hegemony", "growth":4}')
  self.put('campaign/commodities.csv',b'id,name\nore,Ore\n',b'id,name\nore,Ruda\n')
  r=audit(self.old,self.new);self.assertEqual(r['status'],'PASS');self.assertEqual(r['violations'],[])
 def test_reject_code_change(self):
  self.put('world/factions/hegemony.faction',b'{"displayName":"Hegemony", "id":"hegemony", "growth":4}',b'{"displayName":"Hegemonia", "id":"hegemony", "growth":5}')
  self.assertEqual(audit(self.old,self.new)['violations'][0]['kind'],'non_string_byte_change')
 def test_reject_technical_csv_id(self):
  self.put('campaign/commodities.csv',b'id,name\nore,Ore\n',b'id,name\ngold,Ruda\n')
  self.assertEqual(audit(self.old,self.new)['violations'][0]['kind'],'protected_column')
 def test_reject_json_key(self):
  self.put('world/factions/hegemony.faction',b'{"displayName":"Hegemony", "id":"hegemony"}',b'{"visibleName":"Hegemonia", "id":"hegemony"}')
  self.assertEqual(audit(self.old,self.new)['violations'][0]['kind'],'json_key_change')
 def test_reject_bad_script(self):
  self.put('campaign/rules.csv',b'id,script\nx,"SetTextHighlights \\"English\\""\n',b'id,script\nx,"SetTextHighlights \\"Polish\\"; SetGlobal bad"\n')
  self.assertEqual(audit(self.old,self.new)['violations'][0]['kind'],'script_change')

if __name__=='__main__':unittest.main()