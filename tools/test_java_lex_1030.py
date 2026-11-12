#!/usr/bin/env python3
"""Synthetic tests for comment-safe Java source literal scanner."""
import importlib.util
from pathlib import Path
p=Path(__file__).resolve().parent/'audit_java_source_1030.py'
spec=importlib.util.spec_from_file_location('java_scan_1030',p)
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
code='''// "This is a developer comment"
/* "And this is also a comment" */
public class Example {
 String x = "actual phrase"; // "not actual"
 String y = "a\\\"b";
 /* multiline
  "hidden string"
 */
 char c = '\\'';
 String z = "real";
}'''
found=a.java_strings(code)
assert [s for line,s in found]==['actual phrase','a\\"b','real'],found
assert [line for line,s in found]==[4,5,10],found
print('Java literal lexer 1030 synthetic tests: PASS')
