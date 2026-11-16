"""Download primary papers, extract page text, chunk with provenance. No model API."""
from pathlib import Path
import concurrent.futures, datetime, hashlib, io, json, re, time
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
 ('S01','2101.09624','A review of speaker diarization: Recent advances with deep learning','Speaker Diarization'),
 ('S02','1906.10042','Who said that?: Audio-visual speaker diarisation of real-world meetings','Speaker Association'),
 ('S03','1901.01342','AVA-ActiveSpeaker: An Audio-Visual Dataset for Active Speaker Detection','Active Speaker Detection'),
 ('S04','2107.06592','Is Someone Speaking? Exploring Long-term Temporal Features for Audio-visual Active Speaker Detection','Active Speaker Detection / TalkNet'),
 ('S05','1602.00763','Simple Online and Realtime Tracking','Face Tracking / general object tracking'),
 ('S06','1703.07402','Simple Online and Realtime Tracking with a Deep Association Metric','Face Tracking / general object tracking'),
 ('S07','2111.14448','AVA-AVD: Audio-Visual Speaker Diarization in the Wild','Audio-Visual Speaker Diarization'),
]

def ingest_one(row):
 sid, aid, title, topic = row
 out = dict(id=sid, arxiv_id=aid, title=title, url=f'https://arxiv.org/abs/{aid}', pdf_url=f'https://arxiv.org/pdf/{aid}', topic=topic, ingest_status='failed', attempts=[])
 folder=ROOT/'data'/'raw'; folder.mkdir(parents=True,exist_ok=True)
 for attempt in range(1,4):
  started=datetime.datetime.now(datetime.timezone.utc).isoformat()
  try:
   cache=folder/f'{sid}.pdf'
   cached=cache.exists()
   if cached: payload=cache.read_bytes()
   else:
    response=requests.get(out['pdf_url'],timeout=75,headers={'User-Agent':'AVD-Education-Wiki/1.0'})
    response.raise_for_status(); payload=response.content
    if not payload.startswith(b'%PDF'): raise ValueError('Response is not PDF')
    cache.write_bytes(payload)
   reader=PdfReader(io.BytesIO(payload))
   pages=[re.sub(r'\s+',' ',p.extract_text() or '').strip() for p in reader.pages]
   if sum(map(len,pages))<2500: raise ValueError('Insufficient extracted text')
   normalize=lambda value: re.sub('[^a-z0-9]','',value.lower())
   if normalize(title) not in normalize(pages[0]): raise ValueError('Title mismatch: '+pages[0][:180])
   # Retain offsets into each normalized page; page boundaries never disappear.
   chunks=[]
   for page,text in enumerate(pages,1):
    for start in range(0,len(text),1080):
     end=min(start+1400,len(text)); fragment=text[start:end]
     if len(fragment)<50: continue
     chunks.append(dict(id=f'{sid}-p{page:03d}-c{start:05d}',source_id=sid,page=page,start=start,end=end,text=fragment))
   out.update(ingest_status='success',title_verified=True,scope='full_pdf_text',pages=len(pages),characters=sum(map(len,pages)),chunks=len(chunks),sha256=hashlib.sha256(payload).hexdigest(),raw_path=f'data/raw/{sid}.pdf',text_path=f'data/text/{sid}.json',retrieved_at=started,cache_used=cached,pdf_metadata=dict((str(k),str(v)) for k,v in (reader.metadata or {}).items()))
   (ROOT/'data'/'text').mkdir(parents=True,exist_ok=True)
   (ROOT/out['text_path']).write_text(json.dumps({'pages':pages,'chunks':chunks},ensure_ascii=False,indent=2),encoding='utf-8')
   out['attempts'].append(dict(attempt=attempt,time=started,status='success',cache_used=cached))
   return out
  except Exception as e:
   out['attempts'].append(dict(attempt=attempt,time=started,status='failed',error=f'{type(e).__name__}: {e}'))
 return out

def ingest():
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: manifest=list(pool.map(ingest_one,SOURCES))
 (ROOT/'source_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 chunks=[]
 for s in manifest:
  if s['ingest_status']=='success': chunks+=json.loads((ROOT/s['text_path']).read_text(encoding='utf-8'))['chunks']
 (ROOT/'data'/'chunks.json').write_text(json.dumps(chunks,ensure_ascii=False,indent=2),encoding='utf-8')
 return manifest,chunks

if __name__=='__main__':
 m,c=ingest()
 print(json.dumps({'sources':[(s['id'],s['ingest_status'],s.get('pages'),s['attempts']) for s in m],'chunks':len(c)},ensure_ascii=False,indent=2))
