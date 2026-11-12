#!/usr/bin/env python3
"""Negative gate-control tests for 1.0.31. Correct numbers never imply a 1.1 release."""
from __future__ import annotations
import json,tempfile,unittest
from pathlib import Path
from check_release_gates_1031 import check

ROOT=Path(__file__).resolve().parent.parent

class GateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.worktree=ROOT/'worktree'
        cls.manifest=ROOT/'docs/RELEASE_GATES_11.json'
        cls.ledger=ROOT/'docs/API_SEMANTIC_REVIEW_1031.json'
    def test_normal_development_is_allowed(self):
        r=check(self.worktree,self.manifest,self.ledger)
        self.assertEqual(r['current_version'],'1.0.31')
        self.assertEqual((r['pending_semantic_review'],r['pending_windows_gameplay_checks']),(3628,3658))
        self.assertFalse(r['final_release_allowed'])
    def test_strict_release_is_blocked(self):
        with self.assertRaises(RuntimeError):check(self.worktree,self.manifest,self.ledger,True)
    def test_unjustified_review_count_is_rejected(self):
        manifest=json.loads(self.manifest.read_text('utf8'))
        next(x for x in manifest['gates'] if x['id']=='draft_semantics')['unresolved_count']=3627
        with tempfile.TemporaryDirectory() as d:
            m=Path(d)/'gates.json';m.write_text(json.dumps(manifest),'utf8')
            with self.assertRaises(AssertionError):check(self.worktree,m,self.ledger)
    def test_stale_review_ledger_is_rejected(self):
        ledger=json.loads(self.ledger.read_text('utf8'))
        ledger['reviewed'][0]['row_sha256']='0'*64
        with tempfile.TemporaryDirectory() as d:
            l=Path(d)/'ledger.json';l.write_text(json.dumps(ledger),'utf8')
            with self.assertRaises(AssertionError):check(self.worktree,self.manifest,l)
if __name__=='__main__':unittest.main(verbosity=2)
