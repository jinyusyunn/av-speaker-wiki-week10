# 根據實際執行的反思

## 11 月 17 日實際部署追加紀錄

使用者確認上傳 GitHub 後，已建立公開 repository。第一次 GitHub Actions 在 Check static artifact 失敗：Windows 產生的 HTML 含 CRLF，Git 正規化後變 LF，導致公開 artifact 的 SHA-256 與本機測試版本不一致。這是真實 CI 失敗，原始 runner log 保存於 `workflow/first_deployment_failure.log`。

修正方式是讓 renderer 明確使用 LF 輸出，加上 `.gitattributes` 保留 site/ 精確位元組，並在 push 前逐一比對 Git index 中 artifact 與測試 hash。沒有關掉 hash gate。重新執行 pipeline 與獨立 Chromium 測試後才重新推送；最終部署結果見 `workflow/github_status.json`、`tests/remote_results.json` 與 `submission.md`。

## 最容易出錯的節點：來源識別，而不只是下載

最初選定 TalkNet 的候選 arXiv ID 為 2103.14097。HTTP 成功、PDF 可解析，原先 ingestion 因而標成 success；但閱讀第一頁才發現那其實是 *Impedance eigenvalues in linear elasticity*。這是真實來源錯配，不是故意注入的測試，也不能把「下載成功」當成「資料正確」。初始未核實 manifest 保存於 `workflow/initial_manifest_unverified.json`；錯誤文件已隔離，不進最終知識索引。

查詢原始論文頁後，改成正確 TalkNet ID 2107.06592，重新下載並 ingest。最終 manifest 的 S04 有 9 頁，標題吻合；有效 corpus 為 7 篇、80 頁、421 chunks。先前含錯誤數學論文的 466 chunks 不是交付的有效資料數。

檢查前移：在擷取第一頁後、切分與成功標記前，加入移除空白與標點後的標題比對。它能抓到本次錯配，但對掃描 PDF 或標題 OCR 變形可能過度拒絕；若擴展來源，應另有人工審核與 OCR，不宜直接放寬門檻跳過來源驗證。

## Graph 有運作，卻不代表重試能修所有問題

第一次完整 run `20261111T174421Z` 在 HTML Validation 寫 `tests/query_results.json` 時出現 FileNotFoundError，原因是測試資料夾尚未初始化。執行器確實退回 Slide Generation，重試兩次後在第三次失敗停止；真實 traceback 留在 runs/。重新生成 HTML 無法修好驗證器本身，這次失敗暴露固定回退的邊界。

我在 validate() 入口加入 `mkdir(parents=True, exist_ok=True)`，第二次完整 run `20261111T174431Z` 成功，後續加入截圖與 artifact gate 的改良後再完整重跑。沒有為了過關提高重試上限。未來可把「環境／初始化錯誤」與「內容／網頁錯誤」分類，前者直接要求修正環境，後者才回到生成節點；目前程式仍使用 graph.md 記載的固定回退，不宣稱已完成動態錯誤分類。

## 瀏覽器測試也需要觀察產物

最初桌機與手機行為測試通過，但人工觀看 PNG 時發現截圖剛好抓在 0.25 秒進場動畫剛開始，畫面幾乎透明；這不是已完成動畫後的實際簡報外觀。調整 screenshot 使用 `animations='disabled'`，讓有限動畫完成後再拍，另加入 computed opacity 為 1 的檢查。再次觀看桌機 pipeline 與手機追蹤頁，確認文字與圖解可讀。手機內容允許垂直捲動，固定控制列仍可操作。

這說明「測試通過」應說明檢查範圍：水平不溢位不等於所有視覺品質都符合期待。現在同時保留功能斷言、截圖與人工閱讀證據。

## 引用定位與語意事實查核是兩件事

自動 gate 驗證 source ID、chunk、頁碼、原文短語與 URL。兩項刻意注入的負向 fixture 確認假 chunk 與錯誤 source 會被拒絕；它們是通過的防錯測試，不應說成專案真的產生了那兩種錯誤。繁中論述由本次 LLM 閱讀相關原文後審閱，並明確把教學推論與研究描述分開。

例如 SORT 與 Deep SORT 原論文是一般多物件／行人追蹤，不能直接宣稱人臉追蹤成績；ASD 也不能等同整體 diarization。簡報未複製論文的 benchmark 數字，避免忽略資料集、版本與評分條件。未來可增加第二位獨立審閱者；目前沒有宣稱有外部專家審核。

## 已修改與未修改的 workflow

已修改：Ingest 新增標題 gate；HTML Validation 提前建立測試目錄；截圖完成動畫並檢查 opacity；Pages 部署前比對已測試 artifact 的雜湊。主幹仍是九個節點，每個節點的輸入、輸出與回退明定。

尚未實作：向量／語意檢索、重跑時呼叫新的 LLM、AV 模型訓練或影片辨識。這些不是本次知識教學成果的實測能力。GitHub Pages 若尚未部署，原因是公開目標確認仍待完成，不能把本機網址或推測網址列為公開成果。
