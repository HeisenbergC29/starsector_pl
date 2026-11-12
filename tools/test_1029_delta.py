#!/usr/bin/env python3
"""Regression tests: no historical map mutation, ID-like edits or malformed UI fragments."""
from __future__ import annotations
import csv,copy
from pathlib import Path
from apply_1029 import OBF,API
from verify_1029_ui import rows,verify_delta

def reject(old,new,mapping,n):
 try:verify_delta(old,new,mapping,n)
 except AssertionError:return
 raise AssertionError('An invalid patch delta was accepted')

def main(worktree):
 o=worktree/'buildtools/NARZEDZIA_OBF';a=worktree/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 testsets=[(rows(o/'TLUMACZENIA_OBF_10128.csv'),rows(o/'TLUMACZENIA_OBF_10129.csv'),OBF,23),
           (rows(a/'TLUMACZENIA_JAR_1028.csv'),rows(a/'TLUMACZENIA_JAR_1029.csv'),API,7)]
 negative=0
 for old,new,mapping,n in testsets:
  verify_delta(old,new,mapping,n)
  broken=copy.deepcopy(new);broken[0]['polish_ascii_draft']='BROKEN';reject(old,broken,mapping,n);negative+=1
  broken=copy.deepcopy(new);broken[-1]['polish_ascii_draft']=broken[-1]['english_literal'];reject(old,broken,mapping,n);negative+=1
  broken=copy.deepcopy(new);broken[-1]['source_class']='com.example.WrongClass';reject(old,broken,mapping,n);negative+=1
  broken=copy.deepcopy(new);broken.append(copy.deepcopy(broken[-1]));reject(old,broken,mapping,n);negative+=1
  broken=copy.deepcopy(new);broken[-1]['status']='DRAFT_ONLY_NOT_INSTALLED';reject(old,broken,mapping,n);negative+=1
  broken=copy.deepcopy(new);broken[-1]['polish_ascii_draft']+=' ';reject(old,broken,mapping,n);negative+=1
 assert negative==12
 print('PASS:',negative,'negative mapping checks; both original map prefixes unchanged')

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('worktree',type=Path);main(ap.parse_args().worktree)
