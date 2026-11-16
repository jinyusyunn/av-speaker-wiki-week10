# Audio-Visual Speaker Diarization：LLM Wiki 教學簡報

第十週作業：從真實論文建立可查詢、可追溯的 Wiki，再依查詢結果製作繁體中文 HTML 教學簡報。

入口：`site/index.html`；簡報：`site/slides.html`；公開 Wiki：`site/wiki.html`。三者可直接用瀏覽器開啟，沒有 CDN、前端套件或外部字型依賴。

## 目前成果

- 7 篇正確論文全文成功 ingest，80 頁、421 個有頁碼與 offset 的 chunks。
- 9 個 Wiki 條目、19 個引用 claim、14 張繁中投影片。
- 每個研究敘述連到 Wiki claim、來源 ID、chunk ID、PDF 頁碼與原文 URL。
- CLI 詞彙排序查詢、中英別名、網頁搜尋、教學圖解與互動練習。
- 真實有限重試 Graph、成功與失敗執行紀錄、Chromium 桌機與手機驗證。
- GitHub Pages artifact 與 Actions workflow 已備妥；實際部署以 `workflow/github_status.json` 及 `submission.md` 為準，不把預期網址當成已發布網址。

## 安裝與重現

需 Python 3.10+、Node.js（只用 `node --check` 檢查原生 JavaScript）及網路。

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
python scripts/pipeline.py
python scripts/wiki.py "speaker association"
python scripts/verify_public.py
```

首次執行會從 arXiv 下載 PDF；之後使用快取，仍重新擷取與核對標題。無網路且無快取時，會如實記錄下載失敗並停止。完整來源狀態見 `source_manifest.json`。`wiki.py` 同時輸出 Wiki 檢索結果與原文 chunk 查詢結果；原文只保留在本機。

只測瀏覽器：`python scripts/browser_test.py`。本機 HTTP 預覽：`python -m http.server 8000 --directory site`，再開啟 `http://localhost:8000`。完成後 Ctrl+C 關閉。瀏覽器自動測試會自行建立臨時伺服器並在結束時關閉。

## 結構與實際能力

|路徑|用途|
|---|---|
|wiki_plan.md、discussion_log.md|先規劃與方案比較|
|scripts/ingest.py|真實 PDF 下載、標題 gate、文字擷取、重疊切分|
|data/raw、data/text、data/chunks.json|本機原始文件與帶頁碼文字，不進公開網頁|
|source_manifest.json|來源 URL、SHA-256、ingest 狀態、重試與文件 metadata|
|content/knowledge.json|本次 Codex LLM 根據原文撰寫的繁中知識輸入|
|scripts/wiki.py、wiki/|證據定位、條目生成、詞彙排序查詢|
|content/slides.json|教學問題、檢索 query 與視覺設計|
|workflow/retrieval_results.json、outline.json|實際檢索結果與大綱依據|
|scripts/pipeline.py、workflow/graph.md|Graph 執行器、節點契約與回退|
|site/、assets/、scripts/render.py|可公開的靜態網站與生成來源|
|tests/|靜態／瀏覽器／查詢報告、截圖與 artifact hashes|
|workflow/runs/|每次真實執行與失敗 traceback|
|reflection.md、submission.md|實際反思與可直接繳交文字|
|file_inventory.md|完整專案檔案清單（不列環境快取與 .git）|

這是由本次 Codex LLM 整理語意、程式負責確定性編譯與查詢的 Wiki。沒有私自設定付費模型 API，沒有宣稱本機程式能自行撰寫新研究內容，也沒有實作或訓練 AV diarization 模型。檢索使用詞彙評分及中英別名，並非向量資料庫；不熟悉的新中文同義詞可能查不到。引文自動檢查能驗證來源定位，不能單獨證明語意正確，仍需閱讀原文語境。

## GitHub Pages 部署

公開 repository：[jinyusyunn/av-speaker-wiki-week10](https://github.com/jinyusyunn/av-speaker-wiki-week10)。使用者已確認上傳，專案已推送。已透過 Git Credential Manager 與 GitHub REST API 驗證；起始時沒有 repository，且 `gh` 未安裝。

GitHub Pages 的已驗證公開網址見 `submission.md` 與 `workflow/github_status.json`，實際部署／失敗紀錄見 `workflow/deployment_log.json`。重新部署的操作如下：

1. 將已驗證的可追蹤檔案推送到上述 repository 的 `main`，遵守 `.gitignore`。不要上傳原始 PDF、完整擷取文字或憑證。
2. Repository 的 Settings → Pages → Build and deployment 選 **GitHub Actions**。
3. 執行 `.github/workflows/pages.yml` 的 workflow dispatch，或推送 main 觸發。
4. 查看 Actions 的實際部署結果與 Settings → Pages 顯示的 URL，成功後才填入繳交文件。

本機已初始化 Git 時，可在自己確認遠端網址後執行：

```powershell
git remote add origin <已確認的 repository HTTPS URL>
git add .
git commit -m "Add verified AV speaker teaching wiki and slides"
git push -u origin main
```

若 Git 尚未設定提交者，先設定自己的姓名與 email；不應使用代理替您猜的身分。若有既存 origin，先用 `git remote -v` 核對，不要直接覆寫。

Actions 先確認測試通過，再核對 `site/` 全部檔案的 SHA-256，確保部署的是已驗證版本；CI 不重新下載論文或冒稱重新跑了模型。公開資料只包含 site/，第三方完整論文保留本機，原始版權歸作者／出版者。

第一次 CI 曾因 Windows／Git 換行轉換造成 hash 不符而失敗，已保留原始 log 並修正 renderer、`.gitattributes` 與 Git index 上傳前檢查。沒有略過 artifact gate。

## 繳交整理

閱讀 `handin.md` 即可取得應貼的連結與精簡繳交文字，完整報告是 `submission.md`。本機附件為 `deliverables/week10_submission.zip`，包含程式、Wiki、網站、規劃、流程、反思與真實測試紀錄，不含原始 PDF、完整擷取 corpus、Git 內部資料或憑證。

重新產生報告與附件：

```powershell
python scripts/finalize.py
python scripts/pack_submission.py
```

## 驗證與評分邊界

具體測試數量、每次 run 與尚未完成事項見 `tests/summary.md`、`workflow/execution_log.md`、`submission.md`。沒有老師正式評分細則全文，因此 `submission.md` 只依題目列出的 9～10 分要求逐項對照，不保證分數。
