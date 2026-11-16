# 第十週作業繳交：用 LLM Wiki 做一份教學 HTML 簡報

## 專案主題與成果入口

**Audio-Visual Speaker Diarization — AI 如何辨識影片中誰正在說話？**

本專案先以真實論文建立可追溯 Wiki，再透過實際 Wiki 查詢結果整理教學大綱，完成繁體中文 HTML 教學簡報。專案已在目前工作目錄實作並完成真實執行。

- 本機首頁：`site/index.html`
- HTML 簡報：`site/slides.html`
- 可搜尋 Wiki：`site/wiki.html`
- 完整檔案清單：`file_inventory.md`
- GitHub repository：https://github.com/jinyusyunn/av-speaker-wiki-week10
- GitHub Pages：已部署並實際驗證：https://jinyusyunn.github.io/av-speaker-wiki-week10/

## Wiki、資料來源與生成方式

先建立 wiki_plan.md、discussion_log.md，比較「依論文逐篇整理」與「依概念條目、附來源證據」兩種方式，最後採第二種並保留來源索引。實際成功 ingest **7 篇全文、80 頁、421 個 chunks**，產生 **9 個 Wiki 條目、19 個有引用的 claim**。

每篇記錄來源 ID、標題、URL、ingest_status、PDF hash 與頁數。資料先下載成 PDF、擷取逐頁文字、以 1400 字元視窗與 320 字元重疊切分，保留頁碼與 offset。查詢使用詞彙排序及中英別名，並可回到原文 chunk。

繁中語意內容由本次 Codex LLM 閱讀原文後整理，保存在 content/knowledge.json；本機程式負責可重現的 ingestion、證據定位、條目編譯、查詢與網頁生成，沒有冒稱另行呼叫未執行的 LLM API。詳見 content/generation_record.md。

|ID|論文|實際 ingest|
|---|---|---|
|S01|[A review of speaker diarization: Recent advances with deep learning](https://arxiv.org/abs/2101.09624)|成功，全文 29 頁|
|S02|[Who said that?: Audio-visual speaker diarisation of real-world meetings](https://arxiv.org/abs/1906.10042)|成功，全文 5 頁|
|S03|[AVA-ActiveSpeaker: An Audio-Visual Dataset for Active Speaker Detection](https://arxiv.org/abs/1901.01342)|成功，全文 15 頁|
|S04|[Is Someone Speaking? Exploring Long-term Temporal Features for Audio-visual Active Speaker Detection](https://arxiv.org/abs/2107.06592)|成功，全文 9 頁|
|S05|[Simple Online and Realtime Tracking](https://arxiv.org/abs/1602.00763)|成功，全文 5 頁|
|S06|[Simple Online and Realtime Tracking with a Deep Association Metric](https://arxiv.org/abs/1703.07402)|成功，全文 5 頁|
|S07|[AVA-AVD: Audio-Visual Speaker Diarization in the Wild](https://arxiv.org/abs/2111.14448)|成功，全文 12 頁|

## Wiki 查詢與教學簡報

Wiki 查詢 Top-1 測試 **7/7 通過**；例如「人臉追蹤」找到 face-tracking、「speaker association」找到 association、「TalkNet」找到 talknet。未知關鍵字可回報無結果。全部結果在 tests/query_results.json。

投影片 **14 張**，內容包含 diarization 定義、聲音不足之處、AV 原理、人臉偵測與追蹤、ASD、TalkNet、聲音人物配對、完整 AV pipeline、論文案例、限制、評估、互動練習及總結參考。每頁的重要敘述能連回 Wiki 與原始論文。

網頁具 RWD、上一頁／下一頁、鍵盤切換、頁碼、進度列、指定頁 hash、互動題與原創教學圖解。時間軸、人物狀態與流程示意均明確標示為教學圖解，不是模型實測結果。

## Loop／Graph 與真實執行

實作流程為 Source Collection → Ingest → Wiki Generation → Wiki Retrieval → Outline → Fact Check → Slide Generation → HTML Validation → Publish Readiness。每節點輸入、輸出、檢查、fallback 與 2 次重試上限見 workflow/graph.md。資料不足回到 ingestion，引用錯誤回到 Wiki generation，網頁錯誤回到 slide generation。

首次完整 run 20261111T174421Z 因 tests/ 目錄未建立而在 HTML Validation 發生 FileNotFoundError，實際回退與重試兩次後停止；修正初始化後完整執行成功。最新成功 run 為 `20261116T174528Z`。每次節點起訖時間、錯誤與 traceback 保留在 workflow/runs/；最新摘要為 workflow/execution_log.md。

另一次真實前期問題是 TalkNet 候選 arXiv ID 指向數學論文。閱讀第一頁發現後已隔離錯誤資料、改用正確 2107.06592，並把標題 gate 移到成功 ingest 之前；最終資料不含錯誤論文。

## 驗證與反思

最新自動驗證：**106 通過、0 失敗**（靜態 41、真實 Chromium 65）。檢查至少五篇成功 ingest、PDF hash、chunk offset、Wiki 查詢、引用、至少十張簡報、內部連結、JS 語法與實際互動功能。

Chromium 實測桌機 1440×1000、手機 390×844，包含鍵盤、上下頁、深連結、引用跳轉、Wiki 搜尋、互動題、14 頁水平溢位及零 JS 例外；另保存並檢視截圖。兩項故意注入的無效引用 fixture 成功被拒絕，算防錯測試通過，不偽稱為實際內容失敗。測試範圍與限制見 tests/summary.md。

反思指出最易出錯的是「來源身分正確性」，下載可解析的 PDF 仍可能是錯論文；其次是固定回退無法修正驗證環境初始化。已前移標題核對、測試目錄初始化與 artifact hash gate。截圖曾抓到進場動畫的透明起點，調整動畫完成後截圖並增補 opacity 檢查。詳細反思見 reflection.md。

## 公開部署與誠實限制

已部署並實際驗證：https://jinyusyunn.github.io/av-speaker-wiki-week10/

GitHub Actions 已成功部署，並直接 GET 公開首頁、簡報、Wiki 與三個 CSS／JS 資產，6／6 回應 HTTP 200 且 SHA-256 與本機已驗證 artifact 一致。證據在 tests/remote_results.json；公開 artifact 不含第三方 PDF。未訓練或執行 AV 辨識模型，未宣稱模型準確率。自動引用定位不等同完整語意事實查核；中文新同義詞的詞彙檢索仍可能不足。

## 對照題目提供的 9～10 分要求

未提供老師正式 rubric 全文，以下逐項對照本題列出的要求，不保證最終評分。

|題目提供的高分要求|完成情形|可查證成果／限制|
|---|---|---|
|先規劃、比較至少兩種 Wiki 組織|完成|wiki_plan.md、discussion_log.md；逐篇論文 vs 概念條目|
|至少 5 篇真實且覆蓋五大主題的資料|完成|7 篇全文；source_manifest.json 與 source_collection.md|
|真實 ingestion、切分、追蹤、條目生成、查詢|完成|下載 PDF、80 頁文字、421 chunks、9 條目、詞彙查詢；並非只存 PDF|
|每篇來源 ID／標題／URL／實際狀態|完成|manifest 含 hash、頁數、scope、attempts、標題核對|
|Wiki 正確引用、誠實處理限制|完成並揭露邊界|19 claims 有 source／chunk／page；自動定位之外仍須語意審閱|
|至少 10 張繁中教學簡報及指定內容|完成|14 張，涵蓋全部指定主題、AV pipeline、案例、限制與參考|
|美觀、RWD、導航、鍵盤、頁碼、圖解|完成|原創深色設計；桌機與手機 Chromium 實測、截圖|
|用實際 Wiki 查詢結果生成內容|完成|retrieval_results.json → outline.json → Wiki claims → slides|
|九節點 Loop／Graph 契約、回退與重試|完成|graph.md、pipeline.py；真實失敗回退兩次後停止|
|完整執行、真實節點與錯誤紀錄|完成|runs/ 保留 failed 與 success；execution_log.md|
|根據實測反思與改進流程|完成|reflection.md：錯來源、初始化錯誤、動畫截圖與前移檢查|
|自動驗證與可用時瀏覽器測試|完成|106 通過、0 失敗；其中靜態 41、Chromium 65|
|公開 Wiki 與 GitHub Pages|完成|GitHub Actions 成功，公開首頁／簡報／Wiki 及資產共 6 個 URL 的 HTTP 與 SHA-256 均通過|
|可重現與繳交文件|完成|README、AGENTS、requirements、submission、完整檔案清單|

## 重現指令

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
python scripts/pipeline.py
python scripts/wiki.py "speaker association"
python scripts/verify_public.py
```

Python 需可下載論文，或已有本機快取；Node.js 用於 JS 語法檢查。所有成果、限制與數量均依實際檔案和報告填寫。

## 線上成果與繳交清單

- 首頁：https://jinyusyunn.github.io/av-speaker-wiki-week10/
- 教學簡報：https://jinyusyunn.github.io/av-speaker-wiki-week10/slides.html
- 可查詢 Wiki：https://jinyusyunn.github.io/av-speaker-wiki-week10/wiki.html
- GitHub 程式與文件：https://github.com/jinyusyunn/av-speaker-wiki-week10
- 真實部署紀錄：https://github.com/jinyusyunn/av-speaker-wiki-week10/actions/runs/43921457845
- 本機繳交 ZIP：`deliverables/week10_submission.zip`（不含第三方 PDF、完整原文或憑證；可依 README 重新下載來源）

建議在作業平台貼上教學簡報與 GitHub repository 連結，再貼本文件全文；若平台需要附件，上傳 ZIP。完整要求對照、反思與真實測試證據已包含於專案。
