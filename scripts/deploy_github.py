"""Authorized GitHub upload and Pages deployment; credentials remain in memory."""
from pathlib import Path
import argparse, datetime, hashlib, json, subprocess, sys
import requests

ROOT=Path(__file__).resolve().parents[1]
OWNER='jinyusyunn'
REPO='av-speaker-wiki-week10'
TARGET=f'{OWNER}/{REPO}'
STATUS=ROOT/'workflow/github_status.json'
AUDIT=ROOT/'workflow/deployment_log.json'

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(path,value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
def record(action,**details):
 events=json.loads(AUDIT.read_text(encoding='utf-8')) if AUDIT.exists() else []
 events.append({'time':now(),'action':action,**details});save(AUDIT,events)
def main(mode):
 credential=subprocess.run(['git','credential-manager','get'],input='protocol=https\nhost=github.com\n\n',text=True,capture_output=True,timeout=30,check=True)
 values=dict(line.split('=',1) for line in credential.stdout.splitlines() if '=' in line)
 secret=values.get('password')
 if not secret: raise RuntimeError('No GitHub login available')
 session=requests.Session();session.headers.update({'Authorization':'Bearer '+secret,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'})
 def api(method,path,body=None,allowed=(200,201,202,204)):
  r=session.request(method,'https://api.github.com'+path,json=body,timeout=45)
  if r.status_code not in allowed:
   message=r.json().get('message',r.reason) if 'json' in r.headers.get('content-type','') else r.reason
   raise RuntimeError(f'GitHub {method} {path}: HTTP {r.status_code}: {message}')
  return r
 def git(*args,check=True):
  p=subprocess.run(['git',*args],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=150)
  if check and p.returncode: raise RuntimeError((p.stderr or p.stdout).replace(secret,'[REDACTED]'))
  return p
 user=api('GET','/user').json()
 if user['login'].lower()!=OWNER.lower(): raise RuntimeError('Authenticated account differs from confirmed target')
 state=json.loads(STATUS.read_text(encoding='utf-8')) if STATUS.exists() else {}
 state.update(authenticated=True,http_status=200,login=user['login'],target_confirmed=True,target=TARGET,authorization='使用者於本次要求上傳 GitHub；沿用先前明確提出的公開 repository 目標。',checked_at=now())
 repo_path='/repos/'+TARGET
 if mode=='prepare':
  subprocess.run([sys.executable,'scripts/verify_public.py'],cwd=ROOT,check=True)
  existing=api('GET',repo_path,allowed=(200,404))
  if existing.status_code==404:
   repository=api('POST','/user/repos',{'name':REPO,'description':'第十週：以可追溯 LLM Wiki 生成 Audio-Visual Speaker Diarization 繁中 HTML 教學簡報','private':False,'auto_init':False}).json()
   record('repository_created',repository_url=repository['html_url'],visibility='public')
  else:
   repository=existing.json()
   if repository.get('private'): raise RuntimeError('Existing target is private; refusing to change visibility automatically')
   remote=git('remote','get-url','origin',check=False)
   if repository.get('size',0)>0 and remote.returncode!=0:
    raise RuntimeError('Existing nonempty repository has no matching local remote; refusing unrelated upload')
   record('repository_reused',repository_url=repository['html_url'])
  remote=git('remote','get-url','origin',check=False)
  if remote.returncode: git('remote','add','origin',repository['clone_url'])
  elif remote.stdout.strip()!=repository['clone_url']: raise RuntimeError('Existing origin differs from authorized repository')
  state.update(repository_url=repository['html_url'],repository_initialized=True,repository_created=True,deployed=False)
 elif mode=='push':
  subprocess.run([sys.executable,'scripts/verify_public.py'],cwd=ROOT,check=True)
  if git('remote','get-url','origin').stdout.strip()!=f'https://github.com/{TARGET}.git': raise RuntimeError('Remote mismatch')
  git('add','--all')
  artifact_hashes=json.loads((ROOT/'tests/artifact_hashes.json').read_text(encoding='utf-8'))
  for name,expected in artifact_hashes.items():
   staged_bytes=subprocess.run(['git','show',':site/'+name],cwd=ROOT,capture_output=True,check=True).stdout
   if hashlib.sha256(staged_bytes).hexdigest()!=expected: raise RuntimeError('Git index changes tested artifact bytes: '+name)
  staged=git('diff','--cached','--name-only').stdout.splitlines()
  forbidden=[p for p in staged if p.startswith(('data/','workflow/rejected_','deliverables/')) or p.endswith('.pdf') or p=='.env']
  if forbidden: raise RuntimeError('Refusing to upload local-only files: '+', '.join(forbidden))
  for name in staged:
   path=ROOT/name
   if path.is_file() and path.suffix.lower() in {'.py','.md','.json','.html','.js','.yml','.txt'}:
    if secret in path.read_text(encoding='utf-8',errors='ignore'): raise RuntimeError('Credential detected in staged content')
  if staged:
   git('-c','user.name='+OWNER,'-c',f'user.email={user["id"]}+{OWNER}@users.noreply.github.com','commit','-m','Publish verified AV speaker wiki, teaching slides, and submission evidence')
  git('push','-u','origin','main')
  sha=git('rev-parse','HEAD').stdout.strip()
  state.update(last_pushed_commit=sha,repository_url=f'https://github.com/{TARGET}')
  record('git_push',commit=sha,branch='main',files_changed=len(staged),repository_url=state['repository_url'])
 elif mode=='pages':
  current=api('GET',repo_path+'/pages',allowed=(200,404))
  if current.status_code==404: api('POST',repo_path+'/pages',{'build_type':'workflow'})
  elif current.json().get('build_type')!='workflow': api('PUT',repo_path+'/pages',{'build_type':'workflow'})
  pages=api('GET',repo_path+'/pages').json()
  state.update(pages_configured=True,pages_candidate_url=pages['html_url'])
  api('POST',repo_path+'/actions/workflows/pages.yml/dispatches',{'ref':'main'})
  record('pages_configured_and_workflow_dispatched',build_type='workflow',candidate_url=pages['html_url'])
 elif mode=='status':
  runs=api('GET',repo_path+'/actions/workflows/pages.yml/runs?per_page=5').json()['workflow_runs']
  summary=[{k:r.get(k) for k in ['id','status','conclusion','html_url','head_sha','created_at']} for r in runs]
  state['action_runs']=summary
  print(json.dumps({'runs':summary},ensure_ascii=False))
  latest=next((r for r in runs if r['head_sha']==state.get('last_pushed_commit')),runs[0] if runs else None)
  if latest and latest['conclusion']=='failure':
   jobs=api('GET',repo_path+f'/actions/runs/{latest["id"]}/jobs').json()['jobs']
   failed=[{'name':j['name'],'steps':[{'name':s['name'],'conclusion':s['conclusion']} for s in j.get('steps',[]) if s['conclusion']=='failure']} for j in jobs if j['conclusion']=='failure']
   record('actions_failure',run_url=latest['html_url'],jobs=failed)
   print(json.dumps({'failed_jobs':failed},ensure_ascii=False))
  if latest and latest['conclusion']=='success':
   pages=api('GET',repo_path+'/pages').json();url=pages['html_url'].rstrip('/')+'/'
   hashes=json.loads((ROOT/'tests/artifact_hashes.json').read_text(encoding='utf-8'))
   checks=[]
   # Verify the actual public bytes, not just a guessed URL or an Actions success badge.
   for filename in ['index.html','slides.html','wiki.html','assets/style.css','assets/deck.js','assets/wiki.js']:
    r=requests.get(url+filename,timeout=35,headers={'Cache-Control':'no-cache'})
    checks.append({'path':filename,'http_status':r.status_code,'sha256_matches_local':r.status_code==200 and hashlib.sha256(r.content).hexdigest()==hashes[filename]})
   verified=all(c['sha256_matches_local'] for c in checks)
   evidence={'time':now(),'actions_run_url':latest['html_url'],'actions_commit':latest['head_sha'],'pages_url':url,'verified':verified,'checks':checks}
   save(ROOT/'tests/remote_results.json',evidence)
   if verified:
    state.update(deployed=True,pages_url=url,slides_url=url+'slides.html',wiki_url=url+'wiki.html',deployment_run_url=latest['html_url'],deployed_commit=latest['head_sha'],verified_at=now())
    record('public_pages_verified',pages_url=url,actions_run_url=latest['html_url'],checks=checks)
   print(json.dumps(evidence,ensure_ascii=False))
 save(STATUS,state)
 print(json.dumps({'mode':mode,'target':TARGET,'repository_url':state.get('repository_url'),'deployed':state.get('deployed',False),'pages_url':state.get('pages_url')},ensure_ascii=False))

if __name__=='__main__':
 sys.stdout.reconfigure(encoding='utf-8')
 parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','push','pages','status']);args=parser.parse_args()
 try: main(args.mode)
 except Exception as e:
  message=f'{type(e).__name__}: {e}';record('error',mode=args.mode,error=message);print(message,file=sys.stderr);sys.exit(1)
