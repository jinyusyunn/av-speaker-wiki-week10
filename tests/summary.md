# 實際驗證結果

最新完整 run：`20261116T174353Z`，狀態 `success`。

|類型|通過|失敗|證據|
|---|---:|---:|---|
|靜態、來源、引用、查詢、JS 語法|41|0|static_results.json|
|真實 Chromium 桌機／手機瀏覽器|65|0|browser_results.json|
|總計|106|0|以上兩份報告|

Wiki 中英查詢 Top-1 測試 7/7 通過，另有 unknown query 無結果測試。來源 7 篇，PDF 合計 80 頁，421 chunks。9 個條目、19 個 claims、14 張投影片。

負向 fixture 兩項：假 chunk 與錯 source，成功被拒絕，因此是通過測試。初次 full run 的測試目錄初始化例外不列為最新斷言測試失敗，但保留在 workflow/runs/；當次有 3 筆失敗節點事件（初次＋2 次重試），整體 run failed。

瀏覽器實測範圍：上一頁／下一頁、左右鍵、PageUp／PageDown、Home／End、深連結、邊界按鈕、互動題正誤回饋、Wiki 引用跳轉、中英搜尋、無結果、14 頁桌機與手機水平溢位、桌機控制列遮擋、進場動畫後不透明、零 JavaScript page errors。viewport 為 1440×1000 與 390×844；並非所有瀏覽器或手機機型都測過。

已實際檢視 screenshots/ 中桌機 pipeline 與手機 tracking 截圖。首次截圖抓到動畫剛開始而幾乎透明，之後使用 animations=disabled 並增補 opacity 檢查，重新截圖。截圖本身不是模型辨識結果。

部署 gate：`python scripts/verify_public.py` 確認已通過報告及 site/ 的精確 SHA-256。不以測試報告存在就推論任意後續版本也測過。
