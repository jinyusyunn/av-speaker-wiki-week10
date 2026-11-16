from pathlib import Path
from html import escape as E
import json, shutil
ROOT=Path(__file__).resolve().parents[1]
def shell(title,body,script=''):
 return '<!doctype html>\n<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="以可追溯論文 Wiki 學習 Audio-Visual Speaker Diarization"><title>'+E(title)+'</title><link rel="stylesheet" href="assets/style.css"></head><body><a class="skip" href="#main">跳至內容</a><header><a class="brand" href="index.html">AV / SPEAKER WIKI</a><nav aria-label="主要導覽"><a href="slides.html">教學簡報</a><a href="wiki.html">查詢 Wiki</a></nav></header>'+body+('<script src="assets/'+script+'" defer></script>' if script else '')+'</body></html>'

def reference_list(manifest):
 return '<ol class="source-list">'+''.join(f'<li id="{s["id"]}"><strong>{s["id"]}</strong> <a href="{s["url"]}">{E(s["title"])}</a><br><span class="badge">全文 ingest · {s["pages"]} 頁 · 標題已核對</span></li>' for s in manifest)+'</ol>'

def citations(claim):
 return f'<a href="wiki.html#{claim["id"]}">{claim["source"]} · p.{claim["page"]} · {claim["id"]}</a>'

def visual(kind):
 face=lambda name,quiet=False:f'<div class="face {"quiet" if quiet else ""}"><div class="head">◉</div>{name}<br><small>{"靜默／未知" if quiet else "說話活動"}</small></div>'
 items={
 'hero':'<div class="label">WHO SPOKE WHEN?</div><div class="big">聽見聲音<br>也看見線索</div><div class="row"><span class="pill">音訊特徵</span><span class="arrow">×</span><span class="pill">人物軌跡</span></div>',
 'timeline':'<div class="label">合成時間軸 / 非模型結果</div><div class="lanes"><div class="lane">A<div class="bar"><span style="width:33.33%">A</span><span class="blank" style="width:33.33%"></span><span style="width:33.34%">A</span></div></div><div class="lane">B<div class="bar"><span class="blank" style="width:33.33%"></span><span class="b" style="width:33.33%">B</span></div></div></div><div class="row label"><span>0s</span><span>2s</span><span>4s</span><span>6s</span></div>',
 'compare':'<div class="label">兩種不完整的觀察</div><div class="box">只有音訊 → 有人在說話，哪張臉？</div><div class="arrow">＋</div><div class="box">只有影像 → 有人張嘴，是說話嗎？</div><div class="arrow">↓</div><div class="pill">一起考慮視聽與時間線索</div>',
 'fusion':'<div class="row"><div class="box">音訊片段<br>發聲特徵</div><div class="box">嘴部影格<br>動作特徵</div></div><div class="arrow">↓ 對齊時間 ↓</div><div class="box">視聽關聯／融合</div><div class="arrow">↓</div><div class="pill">支援說話活動與身分推斷</div>',
 'tracks':'<div class="label">同一條軌跡 / 跨三個影格</div><div class="frames">'+''.join(f'<div class="face"><div class="head">◉</div>Track 01<br>t = {i}</div>' for i in range(3))+'</div><p class="visual-caption">位置可以移動；track ID 應保持連續。這是概念示意。</p>',
 'faces':'<div class="label">ASD 示意 / 非模型分數</div><div class="row" style="margin-top:30px">'+face('Person 01')+face('Person 02',True)+'</div><p class="visual-caption">為每張可見人臉判斷此刻的說話活動。</p>',
 'temporal':'<div class="label">TALKNET 概念抽象</div><div class="row"><span class="pill">音訊 encoder</span><span class="pill">視覺 encoder</span></div><div class="arrow">↓</div><div class="box">Cross-attention · 跨模態互動</div><div class="arrow">↓</div><div class="box">Self-attention · 長期說話線索</div>',
 'association':'<div class="label">關聯結果可以是未知 / 示意</div><div class="lanes"><div class="row"><span class="pill">Speaker A</span><span class="arrow">→</span><span class="pill">Track 01</span></div><div class="row"><span class="pill">Speaker B</span><span class="arrow">→</span><span class="pill">Off-screen</span></div></div><div class="box">聲音分群 ≠ 人臉追蹤 ≠ 真實姓名</div>',
 'pipeline':'<div class="label">教學用模組化 AV PIPELINE</div><div class="box" style="margin:10px 0">影片輸入 → 視聽時間對齊</div><div class="pipeline"><div class="box">音訊 → 語音活動偵測</div><div class="box">影像 → Face Detection</div><div class="box">聲音 embedding / 分群</div><div class="box">Face Tracking</div><div class="box merge">音訊＋人臉軌跡 → Active Speaker Detection</div><div class="box merge">Speaker-to-Person Association</div><div class="box merge">時間區間＋Speaker ID＋Track ID / unknown</div></div>',
 'cases':'<div class="label">論文中的真實研究情境</div><div class="box">S02 · Who said that?<br>會議、環景影片、AMI corpus</div><div class="arrow">↓ 場景走向複雜 ↓</div><div class="box">S07 · AVA-AVD<br>電影、紀錄片、畫外旁白</div>',
 'limits':'<div class="label">失去線索時保留不確定性</div><div class="lanes"><div class="box">遮擋 → 臉部線索缺失</div><div class="box">噪音／重疊說話 → 聲音更難分辨</div><div class="box">畫外音 → 沒有可配對的臉</div></div><span class="pill">同步與人工複核是工程檢查建議</span>',
 'metrics':'<div class="label">DIARIZATION ERROR RATE</div><div class="lanes"><div class="box">False Alarm · 不該有語音卻標了</div><div class="box">Missed Speech · 漏掉語音</div><div class="box">Speaker Confusion · 說話者標錯</div></div><div class="pill">需連同評分設定一起比較</div>',
 'quiz':'<div class="label">形成性評量 / 示意情境</div><div class="quiz-options"><button data-answer="wrong">A. 一律配給畫面正中央的人</button><button data-answer="correct">B. 保留畫外說話者／未知人物</button></div><p class="quiz-feedback" role="status" aria-live="polite">選擇一個答案。</p>',
 'summary':'<div class="label">THREE QUESTIONS</div><div class="lanes"><div class="box">Diarization → 誰何時說話？</div><div class="box">ASD → 哪張可見的臉在說話？</div><div class="box">Association → 聲音連到哪個人？</div></div><a href="wiki.html#references">開啟全部論文與引用</a>'
 }
 return '<div class="visual" role="group" aria-label="'+E(kind)+' 教學圖解">'+items[kind]+'<div class="visual-caption">原創教學圖解 · 非模型推論輸出</div></div>'

def render(entries,outline,manifest):
 site=ROOT/'site';site.mkdir(exist_ok=True)
 shutil.copytree(ROOT/'assets',site/'assets',dirs_exist_ok=True)
 (site/'.nojekyll').write_text('',encoding='utf-8')
 write=lambda name,text:(site/name).write_text(text,encoding='utf-8')
 entrymap={e['id']:e for e in entries}
 wiki='<main id="main" class="wrap"><p class="kicker">TRACEABLE KNOWLEDGE / 可檢索與查證</p><h1>AV Speaker Wiki</h1><p>9 個概念條目，連回 7 篇已 ingest 的原始論文。繁中轉述由本次 Codex LLM 整理；詞彙查詢與證據定位由程式執行。教學推論另行標示。</p><label for="wiki-search">搜尋概念（中英關鍵字，如：人臉、TalkNet、DER）</label><input id="wiki-search" class="search" type="search" placeholder="輸入關鍵字；多詞取交集"><p id="search-status" role="status" aria-live="polite"></p>'
 for e in entries:
  wiki+=f'<article class="entry" id="{e["id"]}" data-search="{E(e["search_text"],quote=True)}"><h2>{E(e["title"])}</h2>'
  for c in e['claims']:
   wiki+=f'<p id="{c["id"]}">{E(c["text"])}<br><small>{c["id"]} → {c["chunk_id"]} → <a href="{c["source_url"]}">{c["source"]} 原文</a> · PDF 第 {c["page"]} 頁<br>定位短語：<q>{E(c["anchor"])}</q> · <a href="https://arxiv.org/pdf/{next(s["arxiv_id"] for s in manifest if s["id"]==c["source"])}#page={c["page"]}">開啟 PDF 該頁</a></small></p>'
  wiki+=f'<p class="note">教學重點／推論：{E(e["takeaway"])}</p></article>'
 wiki+='<section id="references"><h2>參考資料與 ingestion 狀態</h2>'+reference_list(manifest)+'</section><footer>完整原文、chunk 與 SHA-256 保留在本機 data/；公開網頁只提供繁中轉述、短定位語與原文連結。自動引用檢查不取代人工語意審閱。</footer></main>'
 write('wiki.html',shell('可查詢 Wiki｜AV Speaker',wiki,'wiki.js'))
 slides='<main id="main" class="deck"><noscript>簡報切換需要 JavaScript；您仍可閱讀所有投影片或開啟 Wiki。</noscript>'
 for i,s in enumerate(outline,1):
  selected=[entrymap[x] for x in s['selected_entries']]
  claims=[c for e in selected for c in e['claims']]
  # Pipeline and summary use one representative claim per entry to keep teaching readable.
  if len(claims)>3: claims=[e['claims'][0] for e in selected]
  text=''.join(f'<p class="claim" data-claim="{c["id"]}">{E(c["text"])}<span class="citations">{citations(c)}</span></p>' for c in claims)
  links=' · '.join(f'<a href="wiki.html#{e["id"]}">{E(e["title"].split("：")[0])}</a>' for e in selected)
  slides+=f'<section class="slide" id="slide-{i}" data-title="{E(s["title"],quote=True)}" aria-labelledby="title-{i}"><p class="kicker">{E(s["kicker"])}</p><h1 id="title-{i}">{E(s["title"])}</h1><div class="layout"><div class="copy">{text}<div class="note">{E(s["note"])}</div><div class="wiki-link">Wiki 查詢依據：{links}</div></div>{visual(s["visual"])}</div>'
  if i==len(outline): slides+='<details class="references"><summary>展開全部參考資料（7 篇）</summary>'+reference_list(manifest)+'</details>'
  slides+='</section>'
 slides+='</main><nav class="controls" aria-label="投影片控制"><button id="prev" aria-label="上一頁">← 上一頁</button><span id="page-number" aria-live="polite"></span><div class="progress" aria-hidden="true"><i id="progress-fill"></i></div><button id="next" aria-label="下一頁">下一頁 →</button></nav>'
 write('slides.html',shell('AI 如何辨識影片中誰正在說話？',slides,'deck.js'))
 home='<main id="main" class="wrap"><p class="kicker">WEEK 10 / LLM WIKI → TEACHING DECK</p><h1>聽見聲音，<br>看懂誰在說話。</h1><p>Audio-Visual Speaker Diarization 教學專案</p><div class="row"><a class="box" href="slides.html">開始 14 張教學簡報 →</a><a class="box" href="wiki.html">查詢有來源的 Wiki →</a></div><div class="entry"><h2>從論文到教學，每一步可追溯</h2><p>7 篇全文 ingestion → 9 個概念條目 → 19 個引用 claim → 查詢證據 → 14 張投影片。</p><p>涵蓋 Speaker Diarization、Face Tracking、Active Speaker Detection、Speaker-to-Person Association 與評估限制。</p></div><div class="entry"><h2>如何閱讀與操作</h2><p>簡報可用上一頁／下一頁、方向鍵、PageUp／PageDown，以及 Home／End。可直接分享指定頁的 hash 網址；手機可垂直捲動。</p><p>每張投影片的引用可連回 Wiki 的 claim、chunk ID、PDF 頁碼與論文。互動練習及時間軸皆為教學示意。</p></div><footer>本專案實作知識流程與教學網頁；沒有執行影片辨識模型。來源證據與測試報告見 repository。</footer></main>'
 write('index.html',shell('AV Speaker Wiki｜第十週作業',home))
