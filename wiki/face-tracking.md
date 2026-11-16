# Face Detection 與 Tracking：框與軌跡

- Who said that? 將個別人臉偵測串成 face tracks；同篇另用臉部 embedding 比對參與者，說明追蹤與辨認身分是不同步驟。 [S02 p.3 / S02-p003-c01080](https://arxiv.org/abs/1906.10042)
- SORT 是一般多物件追蹤方法，結合 Kalman Filter 與 Hungarian algorithm；可用來理解偵測後的跨幀關聯，但原論文不是專門的人臉追蹤模型。 [S05 p.1 / S05-p001-c00000](https://arxiv.org/abs/1602.00763)
- Deep SORT 加入外觀資訊，改善遮擋下的軌跡關聯；原研究使用行人重識別資料，不能直接把其成績宣稱為人臉追蹤成績。 [S06 p.1 / S06-p001-c00000](https://arxiv.org/abs/1703.07402)

**教學重點／推論**：Detection：這一幀的臉在哪？Tracking：連續幀中哪個框屬於同一條軌跡？

相關索引：face detection, face tracking, SORT, Deep SORT, 人臉偵測, 人臉追蹤
