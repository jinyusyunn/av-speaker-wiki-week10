from pathlib import Path
import json, math, re, sys
ROOT=Path(__file__).resolve().parents[1]

def read(path): return json.loads((ROOT/path).read_text(encoding='utf-8'))
def write(path,value):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
def tokens(text):
 text=text.lower()
 words=re.findall(r'[a-z0-9]+',text)
 for run in re.findall(r'[\u4e00-\u9fff]+',text):
  words += [run[i:i+2] for i in range(max(1,len(run)-1))]
 return words

def compile_wiki(chunks):
 entries=read('content/knowledge.json')
 for entry in entries:
  for claim in entry['claims']:
   matches=[c for c in chunks if c['source_id']==claim['source'] and c['page']==claim['page'] and claim['anchor'].lower() in c['text'].lower()]
   if not matches: raise ValueError(f"Unsupported evidence locator: {claim['id']} / {claim['anchor']}")
   c=matches[0]
   claim.update(chunk_id=c['id'],source_url=next(s['url'] for s in read('source_manifest.json') if s['id']==claim['source']),review='本次 Codex LLM 已閱讀全文相關段落並審閱繁中轉述；程式僅檢查定位與一致性，不等同語意真偽保證。')
  entry['search_text']=' '.join([entry['title'],*entry['aliases'],entry['takeaway'],*(c['text'] for c in entry['claims'])])
  markdown=f"# {entry['title']}\n\n"
  for c in entry['claims']:
   markdown+=f"- {c['text']} [{c['source']} p.{c['page']} / {c['chunk_id']}]({c['source_url']})\n"
  markdown+=f"\n**教學重點／推論**：{entry['takeaway']}\n\n相關索引："+', '.join(entry['aliases'])+'\n'
  p=ROOT/'wiki'/f"{entry['id']}.md";p.parent.mkdir(exist_ok=True);p.write_text(markdown,encoding='utf-8')
 write('wiki/index.json',entries)
 return entries

def search(query,entries=None,k=6):
 entries=entries if entries is not None else read('wiki/index.json')
 q=set(tokens(query));docs=[tokens(e['search_text']) for e in entries]
 df={term:sum(term in d for d in docs) for term in q}
 results=[]
 for e,d in zip(entries,docs):
  score=sum((1+math.log(1+d.count(t)))*math.log(1+(len(docs)+1)/(df[t]+1)) for t in q if t in d)
  if score>0: results.append({'entry_id':e['id'],'score':round(score,4),'title':e['title'],'claim_ids':[c['id'] for c in e['claims']],'citations':[c['chunk_id'] for c in e['claims']]})
 return sorted(results,key=lambda x:(-x['score'],x['entry_id']))[:k]

def search_chunks(query,k=5):
 q=set(tokens(query));results=[]
 for c in read('data/chunks.json'):
  found=q.intersection(tokens(c['text']))
  if found: results.append({**c,'score':len(found)})
 return sorted(results,key=lambda x:-x['score'])[:k]

if __name__=='__main__':
 sys.stdout.reconfigure(encoding='utf-8')
 query=' '.join(sys.argv[1:]) or '誰的聲音 speaker association'
 print(json.dumps({'query':query,'wiki_results':search(query),'source_chunks':search_chunks(query)},ensure_ascii=False,indent=2))
