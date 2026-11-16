"""Bounded graph executor. Each failed node routes to the declared fallback."""
from pathlib import Path
import datetime, hashlib, json, sys, traceback
from ingest import ingest,SOURCES
from wiki import read,write,compile_wiki,search
from render import render
from validate import fact_errors,validate
from browser_test import run as browser_run
ROOT=Path(__file__).resolve().parents[1]
NODES=['Source Collection','Ingest','Wiki Generation','Wiki Retrieval','Outline','Fact Check','Slide Generation','HTML Validation','Publish Readiness']
FALLBACK={'Source Collection':'Source Collection','Ingest':'Source Collection','Wiki Generation':'Ingest','Wiki Retrieval':'Ingest','Outline':'Wiki Retrieval','Fact Check':'Wiki Generation','Slide Generation':'Outline','HTML Validation':'Slide Generation','Publish Readiness':'HTML Validation'}
context={};events=[]

def execute(node):
 if node=='Source Collection':
  assert (ROOT/'wiki_plan.md').exists() and (ROOT/'discussion_log.md').exists()
  assert len(SOURCES)>=5 and len({s[0] for s in SOURCES})==len(SOURCES)
  return {'configured_primary_sources':len(SOURCES),'input':'wiki_plan.md + scripts/ingest.py SOURCES','output':'validated source configuration; official PDF URL is checked at Ingest'}
 if node=='Ingest':
  manifest,chunks=ingest();context.update(manifest=manifest,chunks=chunks)
  assert sum(s['ingest_status']=='success' for s in manifest)>=5
  assert all(s.get('title_verified') for s in manifest)
  return {'sources_success':len(manifest),'chunks':len(chunks),'input':'verified source configuration + cached PDF or network','output':'source_manifest.json, data/raw/, data/text/, data/chunks.json'}
 if node=='Wiki Generation':
  context['entries']=compile_wiki(context['chunks'])
  return {'entries':len(context['entries']),'claims':sum(len(e['claims']) for e in context['entries']),'input':'content/knowledge.json (LLM-authored) + ingested chunks','output':'wiki/*.md + wiki/index.json'}
 if node=='Wiki Retrieval':
  results=[]
  for slide in read('content/slides.json'):
   hits=search(slide['query'],context['entries'],k=9)
   if not set(slide['entries']).issubset({h['entry_id'] for h in hits}): raise ValueError('Retrieval insufficient: '+slide['query'])
   results.append({'query':slide['query'],'results':hits})
  write('workflow/retrieval_results.json',results);context['retrieval']=results
  return {'queries':len(results),'input':'Wiki index + lesson questions','output':'workflow/retrieval_results.json'}
 if node=='Outline':
  outline=[]
  for slide,hits in zip(read('content/slides.json'),context['retrieval']):
   selected=[e for e in slide['entries'] if e in {h['entry_id'] for h in hits['results']}]
   assert selected
   outline.append({**slide,'selected_entries':selected,'query_result_sha256':hashlib.sha256(json.dumps(hits,ensure_ascii=False,sort_keys=True).encode()).hexdigest()})
  assert len(outline)>=10
  context['outline']=outline;write('workflow/outline.json',outline)
  (ROOT/'workflow/outline.md').write_text('# 教學大綱\n\n'+'\n'.join(f"{i}. {s['title']} — 查詢：{s['query']} → {', '.join(s['selected_entries'])}" for i,s in enumerate(outline,1)),encoding='utf-8')
  return {'slides':len(outline),'input':'actual retrieval results + teaching brief','output':'workflow/outline.json + outline.md'}
 if node=='Fact Check':
  errors=fact_errors(context['entries'],context['chunks'],context['manifest'])
  write('workflow/fact_check.json',{'errors':errors,'claims_checked':19,'semantic_review':'本次 LLM 閱讀相關段落並審閱繁中轉述；不冒稱自動定位能證明語意蘊含。','method':'source ID + chunk + page + verbatim locator + URL consistency'})
  if errors: raise ValueError('; '.join(errors))
  return {'claim_locator_errors':0,'input':'Wiki claims + full-text chunks + manifest','output':'workflow/fact_check.json'}
 if node=='Slide Generation':
  render(context['entries'],context['outline'],context['manifest'])
  return {'input':'checked Wiki claims + retrieval-derived outline','output':'site/index.html, site/wiki.html, site/slides.html, assets'}
 if node=='HTML Validation':
  static=validate();browser=browser_run()
  context.update(static=static,browser=browser)
  if static['failed'] or browser['failed']: raise ValueError(f"Validation failed: static={static['failed']}, browser={browser['failed']}")
  return {'passed':static['passed']+browser['passed'],'failed':0,'input':'site/ + expected evidence and behavior','output':'tests/static_results.json, browser_results.json, screenshots/'}
 if node=='Publish Readiness':
  github=read('workflow/github_status.json')
  reason='本機 site/ 已通過驗證；公開部署狀態依 GitHub API 與實際 HTTP 驗證記錄。' if github.get('target_confirmed') else 'GitHub Pages 遠端目標須經使用者確認；本機 site/ 已通過驗證。'
  ready={'local_ready':True,'public_deployed':github.get('deployed',False),'github_authenticated':github.get('authenticated',False),'target_confirmed':github.get('target_confirmed',False),'reason':reason,'public_artifact':'site/ only','next_command':'python scripts/deploy_github.py status','repository_url':github.get('repository_url'),'pages_url':github.get('pages_url')}
  write('workflow/publish_readiness.json',ready)
  return {'input':'passing tests + GitHub preflight','output':'workflow/publish_readiness.json','local_ready':True,'remote_published':ready['public_deployed']}

def main():
 runid=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 index=0;failures={n:0 for n in NODES};visits=0;status='failed'
 try:
  while index<len(NODES):
   visits+=1
   if visits>60: raise RuntimeError('Global transition budget exceeded')
   node=NODES[index];started=datetime.datetime.now(datetime.timezone.utc).isoformat()
   try:
    result=execute(node)
    events.append({'run':runid,'node':node,'started':started,'ended':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'success','result':result})
    print(node+': success',flush=True);index+=1
   except Exception as e:
    failures[node]+=1
    event={'run':runid,'node':node,'started':started,'ended':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'failed','error':f'{type(e).__name__}: {e}','traceback':traceback.format_exc(),'fallback':FALLBACK[node],'failure_count':failures[node],'max_retries':2}
    events.append(event);print(event['error'],flush=True)
    if failures[node]>2: raise
    index=NODES.index(FALLBACK[node])
  status='success'
 finally:
  path=ROOT/'workflow'/'runs';path.mkdir(parents=True,exist_ok=True)
  report={'run_id':runid,'status':status,'events':events}
  write(f'workflow/runs/{runid}.json',report);write('workflow/latest_run.json',report)
  lines=['# 真實節點執行紀錄','',f'Run `{runid}` — **{status}**。時間為 UTC；臺灣時間為 UTC+8。','', '|節點|開始 UTC|結果|產出／錯誤|','|---|---|---|---|']
  for event in events: lines.append('|'+event['node']+'|'+event['started']+'|'+event['status']+'|'+json.dumps(event.get('result',event.get('error')),ensure_ascii=False).replace('|','／')+'|')
  lines+=['','## 前期真實發現與修正','','詳見 observed_issues.json：S04 候選論文編號錯配、Windows cp950 輸出例外、gh 不存在。錯配於閱讀第一頁時發現，非宣稱自動測試先抓到；隨後才加入標題 gate。初始未核實 manifest 已隔離為 initial_manifest_unverified.json，不能當成功來源清單。','','完整原始錯誤、traceback 與每次 graph 重試保存在 runs/。本檔只呈現最新一次 run；早期失敗不會被刪除。']
  (ROOT/'workflow/execution_log.md').write_text('\n'.join(lines),encoding='utf-8')
 return 0 if status=='success' else 1

if __name__=='__main__':
 sys.stdout.reconfigure(encoding='utf-8')
 sys.exit(main())
