# 真實來源蒐集與確認

本次先用網路搜尋找原始論文，下載後再閱讀第一頁核對。以下是實際使用的查詢主題（不是宣稱由本機 pipeline 自動搜尋）：

- `audio visual speaker diarisation wild Chung 2019 arxiv`
- `AVA ActiveSpeaker dataset 1908.07439 TalkNet 2103.14097`
- `speaker diarization review 2012.14941 Deep SORT 1703.07402`
- 發現 TalkNet 編號錯配後查詢：`"Is Someone Speaking?" "arxiv" TalkNet`

上述查詢中的候選編號有錯，不能拿查詢字串本身當引用。最終一律以下載內容與下表為準。

|ID|原始論文 URL|涵蓋範圍|
|---|---|---|
|S01|https://arxiv.org/abs/2101.09624|Speaker Diarization 綜述、典型流程、DER|
|S02|https://arxiv.org/abs/1906.10042|AV diarization、face tracks、自我註冊與人物關聯|
|S03|https://arxiv.org/abs/1901.01342|AVA-ActiveSpeaker、ASD 定義與標註|
|S04|https://arxiv.org/abs/2107.06592|TalkNet、長期視聽特徵與 attention|
|S05|https://arxiv.org/abs/1602.00763|SORT：一般追蹤的運動與跨幀關聯|
|S06|https://arxiv.org/abs/1703.07402|Deep SORT：外觀特徵與遮擋關聯|
|S07|https://arxiv.org/abs/2111.14448|AVA-AVD、畫外說話者、modality mask|

另參照原始發布者資料頁確認：

- Google Research 的 [AVA-ActiveSpeaker 官方論文介紹](https://research.google/pubs/ava-activespeaker-an-audio-visual-dataset-for-active-speaker-detection/)。
- AVA 官方資料集 [GitHub README](https://github.com/cvdfoundation/ava-dataset/blob/master/README.md)，其論文連結為 1901.01342。
- [TalkNet 原始 arXiv 頁](https://arxiv.org/abs/2107.06592)，標題及作者與下載文件相符。

只有 S01–S07 算成功 ingest 來源；上述額外介紹頁未納入 corpus，不灌入篇數。最終成功狀態、PDF SHA-256、頁數與 cache 狀態見根目錄 source_manifest.json。
