# 本次 LLM Wiki 生成紀錄

生成者是本次對話中的 Codex LLM，不是 scripts/ 下另外執行的模型。沒有呼叫外部付費 LLM API。這份紀錄描述真實工作方式，不虛構 API request、模型輸出日誌或第二位審閱者。

1. 在 ingestion 前先撰寫 wiki_plan.md 與 discussion_log.md，比較逐篇論文與概念導向架構。
2. 實際下載 PDF、以 pypdf 擷取帶頁碼文字。閱讀所有來源的第一頁，並額外查閱 S01 第 3 頁的評估段落、S02 第 3 頁的人臉追蹤段落等。
3. 發現 S04 錯配並修正後，LLM 將讀到的內容整理成 9 個繁中概念條目、19 個 claim，每個指定 source、頁碼與短定位語，儲存在 knowledge.json。
4. scripts/wiki.py 根據指定位置找出實際 chunk，找不到即拒絕；產生 Wiki Markdown、JSON 索引與網頁所需結構。
5. 依教學目標設計查詢，實際執行 Wiki Retrieval。Outline 只採用查詢結果中的條目；HTML 中的研究敘述直接取自查核後 Wiki claims。
6. 加入原創圖解、示意時間軸與互動問題。這些皆標示示意或工程建議，不偽裝為論文實測或本專案模型推論。

內容整理時採取的限制：不抄錄長段原文、不自行填造 benchmark、不把一般行人追蹤當成已驗證的人臉模型、不把可見臉的 ASD 當成完整 diarization。19 個 claim 的自動檢查結果見 workflow/fact_check.json；語意審閱仍需閱讀原文，本次審閱不等同獨立專家背書。
