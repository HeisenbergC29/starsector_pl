#!/usr/bin/env python3
"""Native patcher regression on *privately supplied* original/translated JARs.
Never commits or packages these game-owned archives. Distinguishes a legitimate
same-version no-op from a ZIP-metadata-only corruption with identical payloads.
"""
import argparse, hashlib, shutil, subprocess, tempfile, zipfile
from pathlib import Path

sha=lambda b:hashlib.sha256(b).hexdigest()

def test(exe,original_api,patched_api,obf):
    original_api=Path(original_api).read_bytes()
    patched_api=Path(patched_api).read_bytes()
    obf=Path(obf).read_bytes()
    with tempfile.TemporaryDirectory(prefix='st_1041_zipmeta_') as tmp:
        core=Path(tmp)/'starsector-core';core.mkdir()
        jar=core/'starfarer.api.jar'
        jar.write_bytes(patched_api)
        (core/'starfarer_obf.jar').write_bytes(obf)
        (core/'starfarer.api.jar.PL_ASCII_backup_1041').write_bytes(original_api)
        args=[str(exe),'--game',str(core),'--apply','--yes']
        result=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=60)
        if result.returncode or 'Version already installed. No files modified.' not in result.stdout:
            raise AssertionError(('valid noop failed',result.returncode,result.stdout[-450:],result.stderr[-450:]))
        assert jar.read_bytes()==patched_api
        bad=bytearray(patched_api)
        cen=bad.find(b'PK\x01\x02')
        assert cen>=0
        # central-directory modification time, no decompression-data changes
        bad[cen+12]^=1
        assert bytes(bad)!=patched_api
        jar.write_bytes(bad)
        with zipfile.ZipFile(jar) as z:
            assert z.testzip() is None
        result=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=60)
        if result.returncode==0:
            raise AssertionError(('corrupted ZIP incorrectly accepted as noop',result.stdout[-450:]))
        if 'unexpected ZIP bytes; refusing no-op' not in result.stderr:
            raise AssertionError(('corruption refused for unexpected reason',result.stderr[-800:]))
        assert jar.read_bytes()==bad, 'rejection modified game JAR'
        assert (core/'starfarer.api.jar.PL_ASCII_backup_1041').read_bytes()==original_api
        return {'valid_same_version_noop':'PASS','payload_equivalent_zip_metadata_tampering':'REJECTED','corrupted_jar_unchanged':True,'original_backup_unchanged':True,'tampered_zip_still_readable':True,'original_hash':sha(original_api),'patched_hash':sha(patched_api)}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--exe',type=Path,required=True);p.add_argument('--original-api',type=Path,required=True);p.add_argument('--patched-api',type=Path,required=True);p.add_argument('--obf',type=Path,required=True)
    a=p.parse_args();print(test(a.exe,a.original_api,a.patched_api,a.obf))
