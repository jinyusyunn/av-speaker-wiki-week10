"""Package the shareable, reproducible project; never package local source corpus."""
from pathlib import Path
import hashlib, json, subprocess, sys, zipfile
ROOT=Path(__file__).resolve().parents[1]

def main():
 subprocess.run([sys.executable,'scripts/verify_public.py'],cwd=ROOT,check=True)
 p=subprocess.run(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT,capture_output=True,check=True)
 files=sorted(set(name for name in p.stdout.decode('utf-8').split('\0') if name))
 files=[name for name in files if not name.startswith(('deliverables/','data/','workflow/rejected_')) and name!='tests/query_cli_output.json']
 assert not any(name.endswith('.pdf') or name=='.env' for name in files)
 folder=ROOT/'deliverables';folder.mkdir(exist_ok=True)
 target=folder/'week10_submission.zip'
 with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as archive:
  for name in files:
   if (ROOT/name).is_file(): archive.write(ROOT/name,arcname='week10_submission/'+name)
 with zipfile.ZipFile(target) as archive:
  assert archive.testzip() is None
  for needed in ['submission.md','README.md','site/slides.html','site/wiki.html','workflow/graph.md','tests/static_results.json']:
   assert 'week10_submission/'+needed in archive.namelist()
 print(json.dumps({'zip':str(target),'files':len(files),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'zip_integrity':'passed'},ensure_ascii=False))

if __name__=='__main__':
 sys.stdout.reconfigure(encoding='utf-8');main()
