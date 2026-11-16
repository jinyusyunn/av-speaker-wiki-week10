"""Read credentials only in memory; never write or print tokens."""
from pathlib import Path
import subprocess, json, requests
root=Path(__file__).resolve().parents[1]
status_path=root/'workflow'/'github_status.json'
result=json.loads(status_path.read_text(encoding='utf-8')) if status_path.exists() else {'target_confirmed':False,'deployed':False}
result.update(repository_initialized=(root/'.git').exists(),gh_available=False)
try:
 p=subprocess.run(['git','credential-manager','get'],input='protocol=https\nhost=github.com\n\n',text=True,capture_output=True,timeout=30)
 values=dict(line.split('=',1) for line in p.stdout.splitlines() if '=' in line)
 if not values.get('password'): raise RuntimeError('No stored GitHub credential')
 r=requests.get('https://api.github.com/user',headers={'Authorization':'Bearer '+values['password'],'Accept':'application/vnd.github+json'},timeout=25)
 result['http_status']=r.status_code
 if r.status_code==200:
  result.update(authenticated=True,login=r.json()['login'],profile_url=r.json()['html_url'])
 else: result.update(authenticated=False,error='Stored credential rejected by GitHub API')
except Exception as e: result.update(authenticated=False,error=f'{type(e).__name__}: {e}')
(root/'workflow').mkdir(exist_ok=True)
(root/'workflow'/'github_status.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
