#!/usr/bin/env python3
"""Negative cases: old translations, keys, status, new values, ordering, duplicates."""
from copy import deepcopy
from verify_1027_ui import verify_delta
from apply_1027 import OBF,API,STATUS
FIELDS=['source_class','english_literal','polish_ascii_draft','status']

def make_cases(mapping):
  old=[dict(zip(FIELDS,("A","Earlier","Wczesniej","VERIFIED"))) ]
  expected=[dict(source_class=cl,english_literal=en,polish_ascii_draft=pl,status=STATUS)
            for cl,items in mapping.items() for en,pl in items.items()]
  return old,old+expected,len(expected)

def must_reject(old,new,who,amount,msg):
  try:verify_delta(old,new,who,amount)
  except AssertionError:return msg
  raise AssertionError('Unsafe change accepted: '+msg)

def run():
  n=0
  for label,mapping in [('OBF',OBF),('API',API)]:
    old,new,amount=make_cases(mapping)
    assert verify_delta(old,new,mapping,amount)
    for name,fix in (
       ('historical text', lambda x:x[0].update(polish_ascii_draft='Popsute')),
       ('new translation',lambda x:x[-1].update(polish_ascii_draft='Wrong!')),
       ('new source class',lambda x:x[-1].update(source_class='tech.id')),
       ('status',lambda x:x[-1].update(status='NONE')),
       ('reorder',lambda x:x.__setitem__(slice(-2,None),list(reversed(x[-2:])))),
       ('duplicate',lambda x:x.append(deepcopy(x[-1]))),
       ('leading whitespace',lambda x:x[-1].update(polish_ascii_draft=' '+x[-1]['polish_ascii_draft'])),
    ):
      z=deepcopy(new);fix(z);must_reject(old,z,mapping,amount,label+': '+name);n+=1
  print('NEGATIVE 1.0.27 PASS',n,'/ 14 rejected unsafe mutations')
if __name__=='__main__':run()