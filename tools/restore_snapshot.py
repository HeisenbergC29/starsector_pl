#!/usr/bin/env python3
"""Restore complete Starsector PL project snapshot (never includes original game JAR)."""
from pathlib import Path
import hashlib
import io
import json
import subprocess
import tarfile

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / 'snapshots/manifest.json').read_text())
buffers = []
for part in manifest['parts']:
    name = root / 'snapshots' / part['file']
    raw = name.read_bytes()
    if len(raw) != part['size'] or hashlib.sha256(raw).hexdigest() != part['sha256']:
        raise RuntimeError(f'Invalid or missing part {name}')
    buffers.append(raw)
data = b''.join(buffers)
if len(data) != manifest['size'] or hashlib.sha256(data).hexdigest() != manifest['sha256']:
    raise RuntimeError('Source archive hash mismatch')
r = subprocess.run(['zstd', '--decompress', '--stdout'], input=data, capture_output=True, check=True)
target = root / 'worktree'
target.mkdir(exist_ok=True)
with tarfile.open(fileobj=io.BytesIO(r.stdout), mode='r:') as tf:
    for item in tf.getmembers():
        path = Path(item.name)
        if item.name.startswith('/') or '..' in path.parts or path.parts[0] not in ('mod','buildtools','maintenance','build_windows.sh'):
            raise RuntimeError(f'Unsafe member: {item.name}')
    tf.extractall(target)
print('Restored project into', target)
