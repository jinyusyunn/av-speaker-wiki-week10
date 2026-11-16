# 真實節點執行紀錄

Run `20261116T174528Z` — **success**。時間為 UTC；臺灣時間為 UTC+8。

|節點|開始 UTC|結果|產出／錯誤|
|---|---|---|---|
|Source Collection|2026-11-16T17:45:28.813025+00:00|success|{"configured_primary_sources": 7, "input": "wiki_plan.md + scripts/ingest.py SOURCES", "output": "validated source configuration; official PDF URL is checked at Ingest"}|
|Ingest|2026-11-16T17:45:28.813150+00:00|success|{"sources_success": 7, "chunks": 421, "input": "verified source configuration + cached PDF or network", "output": "source_manifest.json, data/raw/, data/text/, data/chunks.json"}|
|Wiki Generation|2026-11-16T17:45:30.981678+00:00|success|{"entries": 9, "claims": 19, "input": "content/knowledge.json (LLM-authored) + ingested chunks", "output": "wiki/*.md + wiki/index.json"}|
|Wiki Retrieval|2026-11-16T17:45:30.991885+00:00|success|{"queries": 14, "input": "Wiki index + lesson questions", "output": "workflow/retrieval_results.json"}|
|Outline|2026-11-16T17:45:30.996019+00:00|success|{"slides": 14, "input": "actual retrieval results + teaching brief", "output": "workflow/outline.json + outline.md"}|
|Fact Check|2026-11-16T17:45:30.996809+00:00|success|{"claim_locator_errors": 0, "input": "Wiki claims + full-text chunks + manifest", "output": "workflow/fact_check.json"}|
|Slide Generation|2026-11-16T17:45:30.997232+00:00|success|{"input": "checked Wiki claims + retrieval-derived outline", "output": "site/index.html, site/wiki.html, site/slides.html, assets"}|
|HTML Validation|2026-11-16T17:45:30.999841+00:00|success|{"passed": 106, "failed": 0, "input": "site/ + expected evidence and behavior", "output": "tests/static_results.json, browser_results.json, screenshots/"}|
|Publish Readiness|2026-11-16T17:45:33.574733+00:00|success|{"input": "passing tests + GitHub preflight", "output": "workflow/publish_readiness.json", "local_ready": true, "remote_published": true}|

## 前期真實發現與修正

詳見 observed_issues.json：S04 候選論文編號錯配、Windows cp950 輸出例外、gh 不存在。錯配於閱讀第一頁時發現，非宣稱自動測試先抓到；隨後才加入標題 gate。初始未核實 manifest 已隔離為 initial_manifest_unverified.json，不能當成功來源清單。

完整原始錯誤、traceback 與每次 graph 重試保存在 runs/。本檔只呈現最新一次 run；早期失敗不會被刪除。