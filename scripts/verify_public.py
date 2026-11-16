"""Standard-library CI gate: tests must pass for these exact public artifact bytes."""
from pathlib import Path
import hashlib, json
root=Path(__file__).resolve().parents[1]
for name in ['static','browser']:
 report=json.loads((root/f'tests/{name}_results.json').read_text(encoding='utf-8'))
 assert report['failed']==0 and report['passed']>0, name+' tests must pass'
expected=json.loads((root/'tests/artifact_hashes.json').read_text(encoding='utf-8'))
actual={p.relative_to(root/'site').as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'site').rglob('*') if p.is_file()}
assert actual==expected,'Public artifact changed since verification; rerun pipeline'
assert not list((root/'site').rglob('*.pdf')),'Do not publish source PDFs'
print('Verified test reports and exact public artifact SHA-256 hashes.')
