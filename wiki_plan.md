# Wiki 規劃（先於 ingestion 建立）

主題：Audio-Visual Speaker Diarization；讀者：第一次接觸多模態語音技術的學生。

|方案|優點|限制|
|---|---|---|
|依論文逐篇整理|來源界線清楚，容易核對|概念分散，難直接用來教學|
|依概念建立條目，再連回來源與 chunk|符合教學順序，可跨論文查詢|必須額外維護 claim → chunk → 原文的追蹤|

採用第二種，加上獨立來源清單，兼顧教學與查證。條目預計包含 diarization、AV 融合、face tracking、active speaker、association、評估與限制。來源先查證標題與 URL，再下載全文；若只能取得摘要，明確標示，不能宣稱全文 ingest。

資料路徑：來源 → 本機原始文件 → 含頁碼的文字 → 重疊切分 → lexical 檢索 → 經人工／本次 LLM 審閱的繁中 claim → Wiki → retrieval evidence → outline → 引用檢查 → HTML。

不用未提供的付費 LLM API。Wiki 繁中綜合由本次 Codex LLM 產生、保存為可檢閱的結構化輸入；本機程式負責可重現的擷取、檢索、證據定位、編譯與驗證，不冒稱執行另一個 LLM 模型。無證據的 claim 必須失敗，不自動補寫。

成功條件：至少五篇實際 ingest、每條 claim 有原文定位、Wiki 可查詢、至少十張投影片、節點與回退紀錄、靜態與瀏覽器測試、誠實揭露部署狀態。
