from pathlib import Path
from html import unescape
from urllib.parse import urlsplit
import copy, hashlib, json, subprocess
from bs4 import BeautifulSoup
from wiki import read,search
ROOT=Path(__file__).resolve().parents[1]

def fact_errors(entries,chunks,manifest):
 errors=[];bychunk={c['id']:c for c in chunks};sources={s['id']:s for s in manifest}
 for e in entries:
  for c in e['claims']:
   chunk=bychunk.get(c.get('chunk_id'));source=sources.get(c['source'])
   if not chunk or not source or source['ingest_status']!='success': errors.append(c['id']+': missing chunk/source');continue
   if chunk['source_id']!=c['source'] or chunk['page']!=c['page'] or c['anchor'].lower() not in chunk['text'].lower(): errors.append(c['id']+': evidence mismatch')
   if c['source_url']!=source['url']: errors.append(c['id']+': URL mismatch')
 return errors

def validate():
 (ROOT/'tests').mkdir(parents=True,exist_ok=True)
 checks=[]
 def check(name,condition,detail=''): checks.append({'name':name,'passed':bool(condition),'detail':detail})
 sources=read('source_manifest.json');entries=read('wiki/index.json');chunks=read('data/chunks.json')
 check('at least five ingested full PDFs',sum(s['ingest_status']=='success' and s.get('title_verified',False) for s in sources)>=5)
 for s in sources:
  check(s['id']+' local PDF checksum',hashlib.sha256((ROOT/s['raw_path']).read_bytes()).hexdigest()==s['sha256'])
  doc=read(s['text_path'])
  check(s['id']+' text chunks have exact page offsets',all(c['text']==doc['pages'][c['page']-1][c['start']:c['end']] for c in doc['chunks']))
 check('all claims evidence and URLs consistent',not fact_errors(entries,chunks,sources))
 broken=copy.deepcopy(entries);broken[0]['claims'][0]['chunk_id']='S99-fake'
 check('negative fixture: fake citation rejected',bool(fact_errors(broken,chunks,sources)),'Deliberately injected fixture; not an operational failure')
 wrong=copy.deepcopy(entries);wrong[0]['claims'][0]['source']='S02'
 check('negative fixture: wrong source rejected',bool(fact_errors(wrong,chunks,sources)))
 results=[]
 for query,expected in [('說話者分段','diarization'),('人臉追蹤','face-tracking'),('active speaker detection','active-speaker'),('speaker association','association'),('TalkNet','talknet'),('DER','evaluation'),('off screen 限制','limitations')]:
  hits=search(query);passed=bool(hits) and hits[0]['entry_id']==expected
  check('Wiki query: '+query,passed)
  results.append({'query':query,'expected_top1':expected,'passed':passed,'hits':hits})
 check('unknown Wiki query returns no hits',not search('zzzznonexistent'))
 (ROOT/'tests'/'query_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
 site=ROOT/'site';soups={p.name:BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser') for p in site.glob('*.html')}
 slides=soups['slides.html'].select('.slide');check('at least ten slides',len(slides)>=10)
 check('every slide cites Wiki and claim',all(s.select('.citations a') and s.select('.wiki-link a') for s in slides))
 outline=read('workflow/outline.json');retrieval=read('workflow/retrieval_results.json')
 check('outline based on actual retrieval results',all(set(s['selected_entries']).issubset({r['entry_id'] for r in retrieval[i]['results']}) for i,s in enumerate(outline)))
 ids={c['id'] for e in entries for c in e['claims']}
 check('slide claims belong to Wiki',all(p['data-claim'] in ids for p in soups['slides.html'].select('[data-claim]')))
 linkerrors=[]
 for filename,soup in soups.items():
  check(filename+' language/viewport/doctype',soup.html.get('lang')=='zh-Hant' and bool(soup.select('meta[name="viewport"]')) and str(soup).lower().startswith('<!doctype html>'))
  allids=[t['id'] for t in soup.select('[id]')];check(filename+' unique IDs',len(allids)==len(set(allids)))
  for tag in soup.select('[href], [src]'):
   value=tag.get('href',tag.get('src'));url=urlsplit(value)
   if url.scheme or url.netloc: continue
   target=site/(url.path or filename)
   if not target.exists(): linkerrors.append(filename+': '+value)
   elif url.fragment and target.suffix=='.html' and not soups[target.name].find(id=url.fragment): linkerrors.append(filename+': #'+url.fragment)
 check('all local resources and anchors valid',not linkerrors,'; '.join(linkerrors))
 for script in (site/'assets').glob('*.js'):
  p=subprocess.run(['node','--check',str(script)],capture_output=True,text=True)
  check(script.name+' JavaScript syntax',p.returncode==0,p.stderr)
 check('public artifact excludes PDF/full extracted corpus',not list(site.rglob('*.pdf')) and not (site/'data').exists())
 check('Pages workflow exists',(ROOT/'.github/workflows/pages.yml').exists())
 report={'passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks),'checks':checks}
 (ROOT/'tests'/'static_results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 artifact={p.relative_to(site).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(site.rglob('*')) if p.is_file()}
 (ROOT/'tests'/'artifact_hashes.json').write_text(json.dumps(artifact,indent=2),encoding='utf-8')
 return report
