# 教學大綱

1. AI 如何辨識影片中誰正在說話？ — 查詢：audio visual 基本原理 → av-fusion
2. 先回答：誰，在何時？ — 查詢：speaker diarization 說話者分段 → diarization
3. 只有聲音，少了哪一塊拼圖？ — 查詢：active speaker detection 嘴巴 → active-speaker
4. 視聽融合：互相補充的線索 — 查詢：audio visual 視聽融合 → av-fusion
5. 先找到臉，再串成軌跡 — 查詢：face tracking SORT 人臉偵測 → face-tracking
6. 誰正在說話？ASD 的判斷單位 — 查詢：active speaker detection ASD → active-speaker
7. TalkNet：把時間也看進去 — 查詢：TalkNet temporal 時間脈絡 → talknet
8. 把 Speaker A 連到 Person 01 — 查詢：speaker association 聲音人物配對 → association
9. 完整 AV Pipeline：兩條支線，一份時間軸 — 查詢：AV pipeline audio visual face tracking speaker association → av-fusion, diarization, face-tracking, association
10. 從會議記錄到紀錄片旁白 — 查詢：applications meeting AMI 案例 → applications
11. 看不到、聽不清、不同步，怎麼辦？ — 查詢：limitations challenge off screen 限制 → limitations
12. 評估時，先說清楚量測對象 — 查詢：evaluation DER 評估 → evaluation
13. 小練習：旁白出現時，要配哪張臉？ — 查詢：speaker association off screen → association
14. 三個問題，帶走完整概念 — 查詢：speaker diarization active speaker detection speaker association → diarization, active-speaker, association