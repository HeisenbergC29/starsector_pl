#!/usr/bin/env python3
"""Guard against replacing canonical forms or technical names by substring."""
import unittest
from apply_1022 import NAME_RE,NAMES,TOKEN_RE

class NameReplacementTests(unittest.TestCase):
 def translate(self,s):return NAME_RE.sub(lambda m:NAMES[m.group(1)],s.encode('ascii')).decode('ascii')
 def test_canonical_names_unmodified(self):
  s='Liga Perseanska, czlonkowie Ligi Perseanskiej i Lige Perseanska.'
  self.assertEqual(self.translate(s),s)
 def test_old_forms_contextual_cases(self):
  s='Liga Perseusza; w Lidze? Zwyciestwo Ligi Persea; przeciw Lige Perseusza.'
  self.assertEqual(self.translate(s),'Liga Perseanska; w Lidze? Zwyciestwo Ligi Perseanskiej; przeciw Lige Perseanska.')
 def test_unrelated_proper_names(self):
  s='Sektor Perseusza, Persea, Perseusz, Ligi Perseanskiej, Ligia Persea.'
  self.assertEqual(self.translate(s),s)
 def test_token_preservation(self):
  s='$personLastName z Ligi Perseusza i $player.theFactionName; <highlight>20%</highlight>'
  new=self.translate(s)
  self.assertEqual(TOKEN_RE.findall(s.encode()),TOKEN_RE.findall(new.encode()))
 def test_legacy_all_cases(self):
  s='Ligi Perseusza | Ligi Persea | Liga Persea | Liga Perseusza | Lige Perseusza'
  self.assertEqual(self.translate(s),'Ligi Perseanskiej | Ligi Perseanskiej | Liga Perseanska | Liga Perseanska | Lige Perseanska')

if __name__=='__main__':unittest.main()