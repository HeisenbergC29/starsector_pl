#!/usr/bin/env python3
"""Negative tests: reject non-authorized source changes, stale semantic approvals."""
from __future__ import annotations
import json,sys,unittest
from pathlib import Path
from apply_1031 import translate_text,BEFORE,AFTER
from verify_review_1031 import verify as verify_ledger
from audit_api_effective_1031 import class_literals,rows_from_csv

ROOT=Path(__file__).resolve().parent.parent

class Regressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping=rows_from_csv(ROOT/'worktree/buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1030.csv')
        cls.ledger=json.loads((ROOT/'docs/API_SEMANTIC_REVIEW_1031.json').read_text('utf8'))
        final=(ROOT/'worktree/mod/data/hullmods/SurveyingEquipment.java').read_bytes()
        cls.original=final.replace(AFTER,BEFORE,1)
        cls.final=final
    def test_exact_source_change(self):
        self.assertEqual(translate_text(self.original),self.final)
    def test_wrong_source_rejected(self):
        with self.assertRaises(ValueError):translate_text(self.original+b' ')
    def test_source_broken_placeholder_rejected(self):
        with self.assertRaises(ValueError):translate_text(self.original.replace(b'%s',b'%d',1))
    def test_class_parser_rejects_non_class(self):
        with self.assertRaises(ValueError):class_literals(b'not a JVM class')
    def test_30_reviews(self):
        self.assertEqual(verify_ledger(self.mapping,self.ledger)['still_need_review'],3628)
    def test_stale_review_fingerprint_rejected(self):
        tampered=[dict(r) for r in self.mapping];
        idx=next(i for i,r in enumerate(tampered) if r['source_class']==self.ledger['reviewed'][0]['source_class'])
        tampered[idx]['polish_ascii_draft']+='!'
        with self.assertRaises(AssertionError):verify_ledger(tampered,self.ledger)
    def test_duplicate_review_rejected(self):
        bad=json.loads(json.dumps(self.ledger));bad['reviewed'][1]=dict(bad['reviewed'][0])
        with self.assertRaises(AssertionError):verify_ledger(self.mapping,bad)
    def test_fake_review_category_rejected(self):
        bad=json.loads(json.dumps(self.ledger));bad['reviewed'][0]['evidence']='runtime_gameplay_pass'
        with self.assertRaises(AssertionError):verify_ledger(self.mapping,bad)

if __name__=='__main__':unittest.main(verbosity=2)
